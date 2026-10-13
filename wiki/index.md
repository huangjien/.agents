# Skill Wiki Index

One line per pattern. Status legend: `candidate` (recorded, not yet
compiled) → `promoted` (compiled into a skill) / `rejected` /
`superseded` (by a refined pattern).

| ID | Title | Status | Models | Domain |
|----|-------|--------|--------|--------|
| PAT-20260906-skill-name-dir-mismatch | VS Code silently skips skills whose frontmatter name ≠ directory name | promoted | — | tooling |
| PAT-20260919-skill-duplication-drift | Identical skills in global + project dirs silently drift after first edit | promoted | — | tooling |
| PAT-20261010-absorbslim-ordering | Tool-retirement migrations need an absorb-then-slim order, not slim-then-absorb | candidate | — | tooling |
| PAT-20261010-skill-renamer-broke-frontmatter | A skill-rename that updates the directory but not the frontmatter `name:` leaves the skill invisible to VS Code | promoted | — | tooling |

## Session Notes

One line per dated session note under `wiki/notes/`. These are the
underlying record for non-pattern observations (consolidations,
retirements, refactors) referenced by later PATs.

| ID | Title | Status | Domain |
|----|-------|--------|--------|
| NOTE-20261010-instructions-consolidation | Copilot instructions layer had triplicated engineering/routing/GSD rules after Trae→VSCode migration; consolidated to one canonical declaration each | recorded | tooling |
| NOTE-20261010-claude-removal | Retired Claude (deleted ~/.claude/); absorbed Communication/Style into AGENTS.md Part 1; extracted codebase-memory-mcp into ~/.agents/mcp/; slimmed codex/gemini/copilot docs to thin pointers. Refines the absorb-slim-ordering rule. | recorded | tooling |
| NOTE-20261010-audit-fixes | codebase-audit found 15 real issues across 5 axes; fixed 9 (P1–P5 + P7–P9), deferred P6 (GSD plugin out-of-scope) and P10 (install.sh migration comment kept as historical meta-note). verify-global-agents now passes 10 OK / 0 warnings. Follow-up sweep caught P11 (ui-ux-pro-max .claude paths) the audit missed. | recorded | tooling |
| NOTE-20261010-audit-fixes-p6-decision | P6 GSD plugin closure decision: KEEP installed with documented staleness (removing kills future GSD adoption path; filing upstream deferred until GSD is actually used). Closure requires either filing upstream or retiring GSD entirely. | recorded | tooling |
| NOTE-20261010-workflow-tool-bug | `workflow(name: "codebase-audit", args: {checks: [...]})` validator rejects multi-element `<item>` arrays. 9 attempts rejected. Worked around with direct bash sweep (which also caught P11). Not filed upstream from this session. | recorded | tooling |
| NOTE-20261010-archive-policy | Archive retention: 30-day window after session date unless wiki iteration / audit regression / explicit user ask fires the keep trigger. First eligible prune for today's archives: 2026-11-09. | recorded | tooling |
| NOTE-20261010-workflows-dir | Created `~/.agents/workflows/` for project-level JS workflow scripts. Why top-level rather than under bin/, wiki/, or `~/.pi/`: see note. Wired into AGENTS.md Part 5 file tree + wiki Layout table. | recorded | tooling |
| NOTE-20261010-part6-gsd-added | AGENTS.md Part 6 (Project Workflow / GSD) added: 5 universally-phrased rules covering milestone directory layout, marker-file convention, sync_version.sh integration, and the deprecation of flat milestone layouts. Operational rather than engineering-standard; kept as separate Part to preserve Part 1's universal framing. | recorded | tooling |
| NOTE-20261010-karpathy-skill-slimmed | karpathy-engineer skill slimmed 78→65 lines (Path A user choice). Removed 4 core-principle sections duplicating AGENTS.md Part 1; kept format, `<thinking>` block, 50-line cap, anti-macro, Chinese persona. Version 1.0.0→2.1.0; lock-file re-hashed. | recorded | tooling |
| NOTE-20261010-copilot-major-and-specialists | Created 10 VS Code Copilot custom agents at `~/.copilot/agents/`: `major` (entry-point orchestrator that uses the `agent` tool to dispatch) + 9 specialists (architect, coder, debugger, reviewer, researcher, tester, doc-writer, laptop-admin, software-maintainer). Each specialist is a thin stub referencing its canonical role at `~/.agents/opencode/subagent/<name>.md` or `~/.agents/agents/<name>.md`. Two dispatch paths: orchestrate via `major`, or pick a specialist directly. | recorded | tooling |
| NOTE-20261010-agent-architecture-simplified | Simplified agent architecture from 3 layers to 2. Merged the 9 specialist wrappers into the L1 role files by adding `tools:` and `color:` frontmatter (OpenCode ignores the new fields, Copilot reads them). Replaced the 9 wrappers at `~/.copilot/agents/` with symlinks to L1. `major.agent.md` stays as a real file (no L1 equivalent — Major is the Copilot-only orchestrator). Original wrappers backed up at `~/.agents/.archive/audit-fix-2026-10-10/l2-wrappers-before-symlink/`. Adding a new specialist now: write L1 file with frontmatter, drop a symlink at `~/.copilot/agents/`. | recorded | tooling |
| NOTE-20261010-clear-tech-comm-skill-v1.0 | Built the `clear-technical-communication` Copilot skill per `~/Downloads/clear-technical-communication-design-plan.md` MVP (plan §14). 5 files (372 lines) at `~/.copilot/skills/clear-technical-communication/` (later moved to `~/.agents/skills/` in v1.2). 12-line global-instructions addendum at `~/.copilot/copilot-instructions.md`. v1.0 shipped 5-deliverable MVP + extensions (templates, strict-mode toggle, CHANGELOG). | recorded | tooling |
| NOTE-20261010-clear-tech-comm-skill-v1.1 | v1.1 after user said "implement all unfinished tasks". Closed all remaining plan items: 5 missing §11 test prompts, all 8 §13 decisions in `DECISIONS.md`, P4-02 cross-check (PASS), P4-04 rollback-exercise (PASS), P3-01..P3-08 via 10 parallel `copilot -p` runs scored against the 8-dimension rubric in `references/eval-results-2026-10-10.md`. **Verdict: PASS** at grand average 4.76/5. One borderline (P9 interactive artifact, completeness=3) noted. Skill at 14 files, 1309 lines. | recorded | tooling |
| NOTE-20261010-clear-tech-comm-skill-v1.2 | User pointed out the new skill was at `~/.copilot/skills/` (per design plan's literal path) instead of `~/.agents/skills/` (where all 55 version-tracked skills live). v1.2: moved to canonical home, added to `.skill-lock.json` (56 skills now), updated the global addendum and all internal path references. Folder hash computed with sha1 of sorted file contents (original installer algorithm no longer in tree; `_note` field documents the deviation). Copilot still discovers it — CLI scope includes `~/.agents/skills/`. Architectural mistake: followed the plan literally without verifying the actual system convention. | recorded | tooling |
