#!/usr/bin/env python3
"""Check upstream skills for updates against local copies in ~/.agents/skills/.

Each skill's SKILL.md frontmatter should contain:
    metadata:
      source: https://github.com/OWNER/REPO/tree/BRANCH/path/to/SKILL.md
      author: ...
      local_only: true   # if set, skip upstream check

Usage:
    update_skills.py [--dry-run | --apply] [--skill NAME] [--diff] [--json-out PATH]

Default behavior: print a table of skills whose upstream body differs from local.
--apply: overwrite local SKILL.md (and refresh metadata.last_reviewed).
--diff: print a unified diff for each outdated skill.
"""
from __future__ import annotations

import argparse
import datetime
import difflib
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

SKILLS_HOME = Path.home() / ".agents" / "skills"
MAX_FILE_BYTES = 2_000_000  # SKILL.md should never be this big

GITHUB_TREE_RE = re.compile(
    r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/tree/(?P<branch>[^/]+)/(?P<path>.+)$"
)


@dataclass
class SkillInfo:
    name: str
    local_path: Path
    source_url: str
    local_only: bool
    author: str
    last_reviewed: str

    @property
    def raw_url(self) -> str | None:
        """Convert a github.com tree URL to a raw.githubusercontent.com file URL.

        Accepts both file URLs (path ends in a file extension) and directory URLs
        (path is a directory like `skills/foo`). Directory URLs get `/SKILL.md`
        appended because that's the canonical entry file in every skill.
        """
        m = GITHUB_TREE_RE.match(self.source_url)
        if not m:
            return None
        path = m["path"]
        # If the last segment has no dot, treat it as a directory and append SKILL.md.
        last_segment = path.rsplit("/", 1)[-1]
        if "." not in last_segment:
            path = f"{path}/SKILL.md"
        return f"https://raw.githubusercontent.com/{m['owner']}/{m['repo']}/{m['branch']}/{path}"


@dataclass
class CheckResult:
    skill: SkillInfo
    status: str  # "up_to_date" | "update_available" | "local_only" | "no_source" | "fetch_error"
    upstream_body: str | None = None
    local_body: str | None = None
    error: str | None = None


def parse_frontmatter(text: str) -> tuple[str, str] | None:
    """Return (frontmatter_text, body) or None if no frontmatter."""
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None
    m = re.search(r"\r?\n---\r?\n", text[4:])
    if not m:
        return None
    raw = text[4 : 4 + m.start()]
    body = text[4 + m.start() + (4 if text.startswith("---\r\n") else 4) :]
    return raw, body


def parse_metadata(fm_text: str) -> dict[str, str]:
    """Pull metadata block values out of frontmatter text. Simple parser."""
    out: dict[str, str] = {}
    in_meta = False
    meta_indent = 0
    for line in fm_text.splitlines():
        if line.startswith("metadata:"):
            in_meta = True
            meta_indent = 0
            continue
        if in_meta:
            if not line.strip():
                continue
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            if indent == 0:
                in_meta = False
                continue
            if ":" in stripped:
                key, _, val = stripped.partition(":")
                val = val.strip().strip('"').strip("'")
                out[key.strip()] = val
    return out


def discover_skills() -> list[SkillInfo]:
    skills: list[SkillInfo] = []
    for entry in sorted(SKILLS_HOME.iterdir()):
        if not entry.is_dir():
            continue
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            continue
        text = skill_md.read_text(encoding="utf-8")
        parsed = parse_frontmatter(text)
        if not parsed:
            continue
        meta = parse_metadata(parsed[0])
        if not meta.get("source"):
            continue
        skills.append(
            SkillInfo(
                name=entry.name,
                local_path=skill_md,
                source_url=meta["source"],
                local_only=meta.get("local_only", "").lower() == "true",
                author=meta.get("author", "?"),
                last_reviewed=meta.get("last_reviewed", "?"),
            )
        )
    return skills


def fetch_url(url: str) -> str | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "skill-updater/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
            if len(data) > MAX_FILE_BYTES:
                return None
            return data.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return f"_HTTP_{e.code}"
    except Exception as e:
        return f"_ERR_{e}"


def normalize_body(text: str) -> str:
    """Normalize body text for comparison.

    - Strip our injected `metadata:` block (the upstream may not have it).
    - Strip the `license:` line (it's an upstream artifact; our copies carry it
      but the line may differ in trailing whitespace).
    - Collapse per-line trailing whitespace.
    - Trim leading and trailing blank lines so a single blank at the boundary
      doesn't register as a diff.
    """
    parsed = parse_frontmatter(text)
    if not parsed:
        body = text
    else:
        body = parsed[1]
    # Drop lines starting with `license:` (upstream boilerplate).
    body = "\n".join(
        line for line in body.splitlines()
        if not line.lstrip().startswith("license:")
    )
    lines = [line.rstrip() for line in body.splitlines()]
    # Trim leading and trailing blank lines.
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def check_one(skill: SkillInfo) -> CheckResult:
    if skill.local_only:
        return CheckResult(skill, "local_only")
    raw_url = skill.raw_url
    if not raw_url:
        return CheckResult(skill, "no_source", error=f"source URL not a GitHub tree URL: {skill.source_url}")
    upstream_text = fetch_url(raw_url)
    if upstream_text is None:
        return CheckResult(skill, "fetch_error", error="empty or oversize response")
    if upstream_text.startswith("_HTTP_") or upstream_text.startswith("_ERR_"):
        return CheckResult(skill, "fetch_error", error=upstream_text)
    local_text = skill.local_path.read_text(encoding="utf-8")
    local_body = normalize_body(local_text)
    upstream_body = normalize_body(upstream_text)
    if local_body == upstream_body:
        return CheckResult(skill, "up_to_date")
    return CheckResult(
        skill,
        "update_available",
        upstream_body=upstream_body,
        local_body=local_body,
    )


def replace_metadata_block(text: str, new_meta: dict[str, str]) -> str:
    """Replace the `metadata:` block in frontmatter with new_meta."""
    parsed = parse_frontmatter(text)
    if not parsed:
        return text
    raw, body = parsed
    lines = raw.splitlines(keepends=True)
    new_block = ["metadata:\n"]
    for k, v in new_meta.items():
        new_block.append(f"  {k}: {v}\n")
    meta_start = next((i for i, ln in enumerate(lines) if ln.startswith("metadata:")), None)
    if meta_start is not None:
        end = meta_start + 1
        while end < len(lines) and (lines[end].startswith(" ") or lines[end].startswith("\t") or lines[end].strip() == ""):
            end += 1
        new_raw = "".join(lines[:meta_start]) + "".join(new_block) + "".join(lines[end:])
    else:
        new_raw = raw + "".join(new_block)
    return "---\n" + new_raw + "---\n" + body


def apply_update(result: CheckResult, today: str) -> None:
    """Overwrite local SKILL.md with the upstream text, preserving our metadata block.

    The upstream may carry its own metadata keys (e.g. `version`, `argument-hint`).
    We keep those and only override the three we manage: author, source, last_reviewed.
    """
    skill = result.skill
    raw_url = skill.raw_url
    assert raw_url is not None, "raw_url must be set for apply"
    full_upstream = fetch_url(raw_url)
    if not full_upstream or full_upstream.startswith("_"):
        raise RuntimeError(f"failed to fetch upstream: {full_upstream}")
    parsed = parse_frontmatter(full_upstream)
    if not parsed:
        raise RuntimeError("upstream SKILL.md has no frontmatter; refusing to overwrite")
    upstream_raw, upstream_body = parsed
    raw_lines = upstream_raw.splitlines(keepends=True)
    meta_start = next((i for i, ln in enumerate(raw_lines) if ln.startswith("metadata:")), None)

    # Parse existing upstream metadata keys so we can preserve them.
    upstream_meta: dict[str, str] = {}
    if meta_start is not None:
        for ln in raw_lines[meta_start + 1 :]:
            if not (ln.startswith(" ") or ln.startswith("\t")):
                break
            stripped = ln.lstrip()
            if ":" in stripped:
                k, _, v = stripped.partition(":")
                upstream_meta[k.strip()] = v.strip().strip('"').strip("'")

    # Fields we manage — override whatever the upstream has.
    upstream_meta["author"] = skill.author
    upstream_meta["source"] = skill.source_url
    upstream_meta["last_reviewed"] = today

    # Rebuild upstream_raw without the old metadata block, then append ours.
    if meta_start is not None:
        end = meta_start + 1
        while end < len(raw_lines) and (raw_lines[end].startswith(" ") or raw_lines[end].startswith("\t") or raw_lines[end].strip() == ""):
            end += 1
        upstream_raw = "".join(raw_lines[:meta_start]) + "".join(raw_lines[end:])
    metadata_block = "".join(f"  {k}: {v}\n" for k, v in upstream_meta.items())
    new_text = (
        "---\n"
        + upstream_raw.rstrip("\n")
        + ("\n" if upstream_raw.strip() else "")
        + "metadata:\n"
        + metadata_block
        + "---\n"
        + upstream_body
    )
    skill.local_path.write_text(new_text, encoding="utf-8")


def render_diff(result: CheckResult) -> str:
    if result.status != "update_available":
        return ""
    diff = difflib.unified_diff(
        (result.local_body or "").splitlines(keepends=True),
        (result.upstream_body or "").splitlines(keepends=True),
        fromfile=f"local/{result.skill.name}.md",
        tofile=f"upstream/{result.skill.name}.md",
        n=3,
    )
    return "".join(diff)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = p.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", default=True,
                   help="(default) only report; do not modify files")
    g.add_argument("--apply", action="store_true",
                   help="overwrite local SKILL.md with upstream")
    p.add_argument("--skill", help="limit to a single skill name")
    p.add_argument("--diff", action="store_true",
                   help="print unified diff for each outdated skill")
    p.add_argument("--json-out", type=Path,
                   help="write machine-readable report")
    args = p.parse_args(argv)

    if args.apply:
        args.dry_run = False

    if not SKILLS_HOME.exists():
        print(f"Skills dir not found: {SKILLS_HOME}", file=sys.stderr)
        return 1

    skills = discover_skills()
    if args.skill:
        skills = [s for s in skills if s.name == args.skill]
        if not skills:
            print(f"Skill not found or no source URL: {args.skill}", file=sys.stderr)
            return 1

    results: list[CheckResult] = [check_one(s) for s in skills]

    today = datetime.date.today().isoformat()

    # ── Print ──────────────────────────────────────────────────────────
    cols = max((len(r.skill.name) for r in results), default=10)
    print(f"{'SKILL'.ljust(cols)}  {'STATUS'.ljust(20)}  AUTHOR      LAST_REVIEWED")
    print("-" * (cols + 50))
    counts = {"up_to_date": 0, "update_available": 0, "local_only": 0,
              "no_source": 0, "fetch_error": 0}
    outdated: list[CheckResult] = []
    for r in results:
        s = r.skill
        print(f"{s.name.ljust(cols)}  {r.status.ljust(20)}  "
              f"{s.author.ljust(10)}  {s.last_reviewed}")
        counts[r.status] += 1
        if r.status == "update_available":
            outdated.append(r)
        if r.error and r.status in ("fetch_error", "no_source"):
            print(f"  ! {r.error}")

    print()
    print(f"Up to date:       {counts['up_to_date']}")
    print(f"Update available: {counts['update_available']}")
    print(f"Local-only:       {counts['local_only']}")
    print(f"No source URL:    {counts['no_source']}")
    print(f"Fetch errors:     {counts['fetch_error']}")

    if args.diff and outdated:
        print()
        for r in outdated:
            print("=" * 78)
            print(f"DIFF: {r.skill.name}  ({r.skill.source_url})")
            print("=" * 78)
            print(render_diff(r), end="" if False else "")

    if args.apply and outdated:
        print()
        print(f"Applying updates to {len(outdated)} skill(s)...")
        for r in outdated:
            try:
                apply_update(r, today)
                print(f"  ✓ {r.skill.name}")
            except Exception as e:
                print(f"  ✗ {r.skill.name}: {e}")

    if args.json_out:
        payload = {
            "checked_at": today,
            "totals": counts,
            "results": [
                {
                    "name": r.skill.name,
                    "status": r.status,
                    "author": r.skill.author,
                    "source": r.skill.source_url,
                    "last_reviewed": r.skill.last_reviewed,
                    "error": r.error,
                }
                for r in results
            ],
        }
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nWrote JSON report: {args.json_out}")

    # Exit code: 0 = all up to date; 1 = updates available or errors
    return 0 if (not outdated and not counts["fetch_error"]) else 1


if __name__ == "__main__":
    sys.exit(main())
