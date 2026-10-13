---
kind: session-note
date: 2026-10-13
session: Skill inventory reduction — candidates and decision protocol
related: PAT-20260919-skill-duplication-drift, wiki/skill-usage.md
---

# 2026-10-13 — Skill cull candidates

58 skills load their `description:` frontmatter into every session,
across five tools. Nothing recorded which skills were actually used, so
nothing could justify a deletion. This note fixes the measurement gap
and lists the candidates a first-pass review found.

## Measurement gap closed

`wiki/skill-usage.md` is now the usage log. `~/.agents/AGENTS.md`
("Skills" section) tells every agent to append a row when a skill's
guidance shapes delivered work. Tool value: the log is the only input
the cull decision trusts — not guesses about "feels useful".

## Candidates

### Retired platform (delete on sight)

| Skill | Reason |
|---|---|
| `claude-api` | Claude tool retired 2026-10-10 (`wiki/notes/2026-10-10-claude-removal.md`); targets a dead integration |
| `web-artifacts-builder` | Builds "claude.ai HTML artifacts"; tied to the retired platform's artifact surface |

### Overlap groups (merge, keep one)

| Group | Skills | Proposal |
|---|---|---|
| Frontend design | `frontend-design`, `design-taste-frontend`, `ui-ux-pro-max` | Keep `frontend-design` for build-time guidance; fold `design-taste-frontend` into it (same stated purpose). Keep `ui-ux-pro-max` only if its style/palette database gets log rows |
| Vercel deploy | `deploy-to-vercel`, `vercel-cli-with-tokens` | Both deploy. Keep the token variant for CI contexts, fold the other — or keep one after the log shows which is used |
| Vercel React | `vercel-react-best-practices`, `vercel-composition-patterns` | Both are React pattern guidance from Vercel Engineering. Merge into one |
| Writing/comms | `clear-technical-communication`, plus 4 others | `clear-technical-communication` overlaps the universal output rules already in AGENTS.md Part 1. Candidate for removal, not merge |

Not candidates: format skills (`docx`, `pptx`, `xlsx`, `pdf` — distinct
tools, distinct triggers), `video`, `laya-triage`, `i-have-adhd`
(daily-use, evidenced by AGENTS.md references).

## Decision protocol

1. Let the usage log run 2–4 weeks (until ~2026-11-10).
2. Cull: retired-platform skills now if desired; overlap-group members
   with zero rows after the window.
3. Merge: surviving overlap groups keep one skill; fold the others'
   unique content in first (absorb-then-delete, per the Claude
   retirement lesson).
4. Archive removed skills under `~/.agents/.deleted-skills-<date>/`
   (existing convention).
5. Verify: re-run `bin/test-hub` (frontmatter name checks) and
   `bin/update-skills` (lock file stays consistent).

## Facts checked

- All 58 skills have real descriptions; none are dead weight via empty
  frontmatter (verified `react-native-skills` and
  `vercel-composition-patterns` carry multi-line descriptions).
- Git history does not discriminate: one 2026-10-10 migration commit
  touched every skill directory.
