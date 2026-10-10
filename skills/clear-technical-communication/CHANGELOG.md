# Changelog

Versions for `clear-technical-communication`. Heuristic version, not SemVer strictly.

## v1.0 — 2026-10-10 — full MVP per design plan §14 plus extensions

This release ships the full plan-deliverable set:
- `D1` Concise global instruction addendum at `~/.copilot/copilot-instructions.md` (12 bullets).
- `D2` `SKILL.md` — main skill, adapted to actual Copilot-skill convention (`allowed-tools:` + `<objective>` / `<process>` sections).
- `D3` `references/ste-inspired-writing.md` — practical STE-inspired writing heuristics.
- `D4` `references/representation-selection.md` — decision table for choosing representation, plus restraint rules and selection flow.
- `D5` `references/examples-and-evaluation.md` — five representative test prompts + scoring rubric (1–5 across 8 dimensions; release threshold: avg ≥ 4.0, no score below 3 on correctness/completeness/honesty).
- `D6` Evaluation suite — documented (prompt set + rubric); execution is manual in VS Code (see README verification recipe).
- `D7` Compatibility check — **pending user execution**: `⌘⇧P → Developer: Reload Window`, then invoke the skill in Copilot Chat and confirm the workflow appears.
- `D8` Review and release notes — this `CHANGELOG.md`, the skill's `README.md`, and the wiki note `2026-10-10-clear-tech-comm-skill.md`.

Plus extensions beyond the plan's MVP scope:
- **Templates** (`templates/explanation.md`, `technical-design.md`, `comparison.md`, `incident-report.md`) — optional starting structures; skill doesn't force them.
- **CHANGELOG.md** added for version history.
- **Phase 4 P4-04** diff review and rollback path documented in `README.md` and `wiki/notes/2026-10-10-clear-tech-comm-skill.md`.
- **Strict-mode toggle** — `argument-hint: "[strictness=approximate|strict]"` flag in the skill's frontmatter; documented as a heuristic option (still not formal STE certification) per Plan §13 open decision #8.
- **YAML-frontmatter adaptation** — adjusted the plan's `tools:` / `color:` proposal to the actual local convention (`allowed-tools:` + body sections). Plan §7 explicitly directed this verification.

### Deferred (not in v1.0)

- Phase 3 P3-01 to P3-10 actual test runs in Copilot — require VS Code interactive testing.
- Phase 4 P4-01 fix evaluation failures — depends on Phase 3 output.
- Phase 4 P4-04 final diff review — done in this session for the v1.0 file set; no P0 issues outstanding.
- Visual artifacts / interactive HTML generation tooling — out of scope per plan; the skill recommends when appropriate but delegates generation to whatever the environment supports.

## v0.1 — 2026-10-10 — initial MVP

First 5-deliverable MVP shipped: `SKILL.md`, three references, README, and the
global-instructions addendum. Detailed in
`~/.agents/wiki/notes/2026-10-10-clear-tech-comm-skill.md`.

## Format conventions

Each release entry above follows roughly:
- New features
- Files touched (with relative paths from the skill directory)
- Open decisions still pending
- Reversal instructions
