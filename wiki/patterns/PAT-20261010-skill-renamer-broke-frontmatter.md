---
id: PAT-20261010-skill-renamer-broke-frontmatter
status: promoted          # candidate | promoted | rejected | superseded
models: []
domain: tooling
created: 2026-10-10
last-touched: 2026-10-10
supersedes: PAT-20260906-skill-name-dir-mismatch    # narrower focus
---

# A skill-rename that updates the directory but not the frontmatter `name:` leaves the skill invisible to VS Code

## Symptom

After renaming a skill's directory (e.g., for naming-uniformity with
siblings, or after importing an upstream skill whose dir-name
conflicts with a local convention), the skill:

- Loads correctly in tooling that scans directories (Trae, ZCode,
  tooling that walks the files and reads the frontmatter).
- Silently fails to load in **VS Code Copilot's Agent Skills** — the
  skill simply doesn't appear in `/skills` or in Chat: Open
  Customizations. No error, no warning.
- May also fail in tooling that validates `name == dir-name` strictly
  (VS Code's loader is the canonical example but not the only one).

## Root cause

VS Code's Agent Skills loader validates that the YAML frontmatter
`name` field matches the parent directory name and drops the skill
on mismatch. See `code.visualstudio.com/docs/agent-customization/
agent-skills` for the documented behavior. Other loaders resolve by
directory scanning and tolerate the mismatch, so a skill can work
in one tool while silently failing in another — the failure only
surfaces when you switch tools.

When `mv taste-skill design-taste-frontend` is run (or equivalent
during upstream-skill import), two things need to change: the
directory name AND the frontmatter `name:`. Skipping the
frontmatter update leaves the YAML stuck on the old name. There's
no validation hook that catches this — both files are valid
YAML and valid on their own; they just no longer match.

## Rule / workaround

When creating or renaming any skill: the frontmatter `name:` and the
directory name must be **byte-identical**. Two ways to enforce:

1. **Convention**: Before `mv`, `sed` the frontmatter `name:` field to
   match. After `mv`, run a quick `diff` between `name:` and the
   parent dir name. This is `write-a-skill`'s recipe (now deprecated
   since the upstream `skill-creator` covers it).
2. **Verification**: After any rename, run `find ~/.agents/skills -name
   SKILL.md | while read f; do dir=$(dirname "$f"); name=$(grep -m1
   '^name:' "$f" | awk '{print $2}'); [[ "$dir" !=
   "$(basename $(dirname $f))" ]] || true; done` — or whatever loads
   the skills in your tool of choice and confirm the skill appears.

A skill with no frontmatter fails the same way — always emit
frontmatter on every skill.

## Evidence

Five instances verified across two sessions:

| Date | Skill | Dir | Frontmatter `name:` | Resolution |
|---|---|---|---|---|
| 2026-09-06 | `taste-skill` → `design-taste-frontend` | `design-taste-frontend/` | `name: design-taste-frontend` | Renamed dir only → renamed frontmatter; load fixed |
| 2026-09-06 | `redesign-skill` → `redesign-existing-projects` | `redesign-existing-projects/` | `name: redesign-existing-projects` | Same pattern |
| 2026-09-06 | `karpathy-engineer` | (added without frontmatter) | (no frontmatter) | Added frontmatter |
| 2026-10-10 | `vercel-react-native-skills` → `react-native-skills` | `react-native-skills/` | `name: vercel-react-native-skills` | Renamed frontmatter `name:` to match dir |
| 2026-10-10 | `vercel-react-view-transitions` → `react-view-transitions` | `react-view-transitions/` | `name: vercel-react-view-transitions` | Same pattern |

The 2026-10-10 instances were caught by the codebase-audit's
"skill loader readiness" check (audit
`codebase-audit-mv2acmbz-6vjaxm`). Two FIXED; the pattern
re-validated.

## Related

Skills: `skill-creator` (universal skill-lifecycle, includes this
rule in its checklist), `write-a-skill` (deprecated fork, was
where this rule was first compiled) · Patterns:
  - `PAT-20260906-skill-name-dir-mismatch` (parent rule this
    narrows; describes the loader behavior + 1 known cause;
    superseded by this PAT for the "rename-drift" cause)

## Why this supersedes the broader PAT-20260906

PAT-20260906 documents the **symptom** (loader drops mismatches) and
the **loader behavior** as the rule. This PAT documents the **most
common cause** (rename-drift) and the **prevention** (rename both
together, not just the dir). The broader symptom-PAT stays valid
as long as the loader behavior remains; this cause-PAT is the
actionable lesson.

When the cause of a mismatch is something other than rename-drift
(e.g., a fresh skill written with mismatched name from the start),
PAT-20260906 still applies — keep both PATs.
