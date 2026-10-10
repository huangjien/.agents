---
kind: session-note
date: 2026-10-10
session: capabilities cleanup + Trae retirement fallout
related: PAT-20260919-skill-duplication-drift
---

# 2026-10-10 — Copilot instructions consolidation

After retiring Trae (2026-09), the global Copilot instructions layer had
accumulated three sources of duplication: engineering/safety rules
written twice (AGENTS.md Parts 1-2 + copilot-instructions.md), the Major
orchestrator routing table written three times (AGENTS.md Part 3 +
copilot-instructions.md + major-routing.instructions.md), and the GSD
integration block written twice (copilot-instructions.md bottom +
gsd-protocol.instructions.md).

## What changed

| Action | Effect |
|---|---|
| Deleted `~/.copilot/instructions/major-routing.instructions.md` | Routing table now sourced from AGENTS.md Part 3 only |
| Slimmed `~/.copilot/copilot-instructions.md` (220 → 41 lines) | Kept communication style + best-representation table + human-in-the-loop; deleted engineering principles, safety rules, working rules, GSD block |
| Moved GSD integration block into `gsd-protocol.instructions.md` | GSD topic lives in one file |
| Converted `~/.agents/copilot/copilot-instructions.md` (100 → 54 lines) | From a duplicate-doc into a setup helper stub: layer map + per-project copy guidance + force-load settings |
| Removed `major-routing.instructions.md` mention from `README.md`; clarified that Major routing loads via `~/AGENTS.md`, not via `~/.copilot/instructions/` | Single source of truth for the routing layer |

Result: Copilot instructions layer went from ~28 KB across 5 files
to ~15 KB across 4 files (−46%). Engineering/safety/routing rules
now have exactly one canonical declaration each.

## Why it took so long to catch

The Trae→VSCode migration in September extracted the routing table,
engineering rules, and GSD config into standalone
`*.instructions.md` files in `~/.copilot/instructions/`, but did not
delete the duplicated content already present in AGENTS.md /
copilot-instructions.md. Each new tool that consumes those files
inherited copies of the same content; consolidation was deferred because
each duplication in isolation looked like "the new place needs a copy
to be self-contained." A real cleanup needs to ask: which file is the
canonical declaration? Everything else should reference it.

## Reusable rule (forward of this session)

When migrating rules out of a tool being retired, the cleanup pass is:

1. Identify the canonical source file already in the home hub.
2. List every per-tool location that holds a copy of the same rule.
3. Pick ONE canonical declaration; rewrite all copies as thin pointers
   (`Full rule lives at <canonical path>.`). Per-tool files retain only
   the rules that are genuinely tool-specific (e.g., output style
   targeting Copilot's chat UI).
4. Verify no broken references: `grep -r '<old rule name>' <new tree>`.

## Restore path

All four originals are preserved at:
```
~/.agents/.archive/instructions-pre-consolidation-2026-10-10/
  copilot-instructions.md.bak        (11,706 B, slimmed)
  copilot-template.md.bak             (3,552 B, stub-ified)
  gsd-protocol.instructions.md.bak    (3,375 B, absorbed block)
  major-routing.instructions.md.bak   (3,086 B, deleted)
```

Revert by `cp`ing the relevant `.bak` back over the active file.

## Other work in the same session (lessons not yet promoted)

These happened earlier in the same session but were scoped cleanup
tasks, not reusable patterns. Listed here for traceability, not for
promotion:

- **Trae retirement fallout** — cleaned 8 docs/configs of stale
  `~/.trae/` references (paths, env vars, skill source URLs).
- **Skills duplicate** — deleted `write-a-skill/` (upstream fork of
  `skill-creator` with no unique content).
- **Skill lock orphans** — removed `find-skills`, `grill-me` entries
  from `.skill-lock.json` (installed but no longer on disk).
- **Skill lock missing entries** — registered 37 untracked local
  skills into the lockfile. Caveats solved in a follow-up: GitHub
  source attribution parsed from frontmatter (no more catch-all
  `local`), and `skillFolderHash` switched to a deterministic
  folder hash (sha1 over sorted `path\0sha1(content)\n` lines)
  so it covers sibling files too — not just SKILL.md.
