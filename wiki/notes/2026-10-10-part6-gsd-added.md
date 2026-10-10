---
kind: addition-note
date: 2026-10-10
session: AGENTS.md Part 6 (Project Workflow / GSD) added
related: PAT-20261010-absorbslim-ordering
---

# 2026-10-10 — AGENTS.md Part 6 added (Project Workflow / GSD)

A new top-level section was appended to `~/.agents/AGENTS.md` covering
the **GSD (Get-Shit-Done) project workflow** conventions. Five rules,
phrased universally so they apply to any project adopting GSD-style
milestone tracking:

1. Every milestone has a `vX.Y/` subdirectory
2. Each milestone directory contains a `milestone-vX.Y-*.md` marker
   with `*Status:** Complete|Planned`
3. `sync_version.sh --from-gsd` reads only `Complete` markers to set
   the package version
4. New milestone checklist (create dir → marker w/ Planned → docs →
   flip to Complete → update index.md)
5. No flat milestone layouts (deprecated) — older flat files migrate
   to `docs/plans/vX.Y/` with originals archived under `_archive/`

## Where it lives

`~/.agents/AGENTS.md` **Part 6** (after Part 5 — File Layout & Install).
Numbered 1–5 within the section. Rules are operational conventions for
milestone tracking, not Part 1-style hard engineering standards; the
section header makes that distinction explicit.

## Universality correction (same session)

The first draft of rule 5 named a specific project's legacy path
(`novel_harness/docs/plans/`). User flagged this as a mistake — the
rules are supposed to be universal/abstract, not project-specific.
Rewritten rule 5 talks about the *pattern* ("flat milestone files
at root or any single directory without `vX.Y/` subdirs") rather
than any specific path, with the universal migration recipe
(migrate → `_archive/`). No project names in the ruleset now.

## Why a new Part rather than folding into Part 1

- Part 1 (Engineering Standards) is rule-shaped: imperative, applies
  to *every* code change. The GSD rules are operational conventions:
  they apply only when a project uses GSD for milestone tracking.
- Mixing them would dilute Part 1's "applies universally" framing.
- A new Part is also forward-compatible: future workflow conventions
  (e.g. release-train rules, dependency-update cadence) can slot in
  as Part 7+ without disturbing the engineering/safety parts.

## Apply-load delta

Nothing in `install.sh` or `route.yaml` references the new Part, so
the install surface is unchanged. All tools (pi, Copilot, Codex,
Gemini) auto-pick up the new content via the same
`~/AGENTS.md`-discovery path they already use.

## Backups

Pre-Part-6 copy at
`~/.agents/.archive/audit-fix-2026-10-10/AGENTS.md.before-part6-gsd-20261010-XXXXXX.bak`
(timestamp at creation). Revert by `cp` back.

## Related

- `~/.agents/AGENTS.md` Part 6 (the rules themselves)
- `~/.agents/wiki/notes/2026-10-10-instructions-consolidation.md`
  (prior session that absorbed the GSD block into
  gsd-protocol.instructions.md — that doc and Part 6 are now
  complementary, not overlapping)
