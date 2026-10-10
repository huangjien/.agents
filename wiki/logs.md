# Maintenance Log

Append-only, one entry per maintenance action (newest last).

- 2026-09-06 — wiki created during Trae retirement migration; structure
  adapted from WikiSkill (arXiv 2608.27454).
- 2026-09-06 — recorded PAT-20260906-skill-name-dir-mismatch (evidence:
  taste-skill / redesign-skill / karpathy-engineer loader failures).
- 2026-09-06 — compiled PAT-20260906-skill-name-dir-mismatch into
  `write-a-skill` (see skill-impact.md entry #1).
- 2026-09-19 — recorded PAT-20260919-skill-duplication-drift (evidence:
  three Vercel skills byte-identical between global and project).
- 2026-09-19 — compiled PAT-20260919-skill-duplication-drift: replaced 3
  byte-identical Vercel skill copies in website/.agents/skills with
  symlinks to ~/.agents/skills/ (see skill-impact.md entry #2).
- 2026-10-10 — consolidated Copilot instructions layer: deleted
  major-routing.instructions.md, slimmed copilot-instructions.md
  (220 → 41 lines), absorbed GSD integration block into
  gsd-protocol.instructions.md, converted the per-project template
  into a setup-helper stub. Backups at
  `~/.agents/.archive/instructions-pre-consolidation-2026-10-10/`
  (note authored). No skills promoted or rejected this session.
- 2026-10-10 — retired Claude entirely (deleted ~/.claude/), absorbed
  Communication/Style/Rep/Explain/Human-in-Loop into AGENTS.md Part 1
  (new `## Output Style` section), extracted shared codebase-memory-mcp
  into `~/.agents/mcp/codebase-memory.md`, slimmed codex/gemini/copilot
  native docs to 11–12 line thin pointers. install.sh dropped the
  Claude portable-role section. Backups at
  `~/.agents/.archive/claude-removal-2026-10-10/`
  (note authored). Refines the absorb-slim-ordering rule from the
  earlier consolidation note; not yet promoted to a PAT — needs more
  instances.
- 2026-10-10 — codebase-audit (5 axes, 7 agents, $0.54, 465s) found 15
  real issues, 0 false positives. Fixed 9 high/med issues across
  AGENTS.md, verify-global-agents, gsd-protocol.instructions.md,
  deploy-to-vercel/SKILL.md, react-native-skills, react-view-transitions,
  run_eval.py, plus the dangling ~/.config/opencode/skills symlink.
  Deferred 2: P6 (GSD plugin out-of-scope, flagged in note) and P10
  (install.sh migration comment deliberately kept as historical
  meta-note). Backup at `~/.agents/.archive/audit-fix-2026-10-10/`
  (note authored).
- 2026-10-10 — follow-up sweep after the audit-fix pass caught 1 missed
  issue (P11): ui-ux-pro-max/SKILL.md had 10 references to
  `.claude/skills/...` paths (Trae was deleted in 2026-09 but the
  recipe paths were never rewritten). Replaced with
  `~/.agents/skills/ui-ux-pro-max/...`. Workflow-tool re-audit
  encountered arg-validator failures (9 attempts rejected); switched
  to direct bash verification — same 5 axes, equivalent coverage.
  wiki/notes/2026-10-10-audit-fixes.md updated to record P11 and the
  "single-pass audits can miss issues" lesson.
- 2026-10-10 — closure pass on the day's open items: (a) wiki/README.md
  Layout table updated to document `notes/` and `audits/` subdirs
  (created earlier today, never documented); (b) all 55 entries in
  .skill-lock.json now use the deterministic folder-hash algorithm
  uniformly — 23 entries updated (rest already matched); (c) P6 GSD
  plugin decision documented in
  wiki/notes/2026-10-10-audit-fixes-p6-decision.md: KEEP the plugin
  with known-staleness; closing requires either filing upstream or
  retiring GSD entirely (latter hidden-deps on the existing GSD
  integration in copilot-instructions.md + wiki references).
- 2026-10-10 — action on the day's deferred items: (a)
  PAT-20261010-absorbslim-ordering created as candidate (2 verified
  instances logged; promotion bar set at 3 full-cycle applications);
  (b) PAT-20261010-skill-renamer-broke-frontmatter promoted with 5
  instances, superseding the broader PAT-20260906 for the
  rename-drift cause (PAT-20260906 kept for non-rename causes);
  (c) wiki note documenting the workflow-tool arg-validator
  regression (9 attempts rejected) and the bash-sweep workaround
  that caught P11; (d) wiki note defining archive retention policy:
  30 days after session date, first eligible prune 2026-11-09.
- 2026-10-10 — wiki/README.md PAT lifecycle section added:
  documents the candidate/promoted/rejected/superseded status
  transitions with concrete promotion criteria (≥1 instance for
  one-shot failures, ≥3 verified applications for repetitive rules)
  and worked examples drawn from today's promoted/candidate PATs.
- 2026-10-10 — created `~/.agents/workflows/` for project-level
  workflow scripts (custom JS multi-agent flows); README.md in
  the dir documents file shape, naming, and skill-vs-workflow split.
  Wired into AGENTS.md Part 5 file tree and wiki Layout table;
  wiki note records the path decision (top-level rather than
  under bin/ or wiki/).
- 2026-10-10 — three starter workflows landed in `~/.agents/workflows/`:
  `hub-audit.js` (5-axis parallel audit), `tool-retire.js` (5-phase
  absorb-slim-order retirement per PAT-20261010-absorbslim-ordering),
  `skill-loader-check.js` (single-axis name↔dir check per
  PAT-20261010-skill-renamer-broke-frontmatter). All three
  pass `node --check`; follow the API from
  workflow-authoring/examples/ (top-level script with global
  `args`/`agent`/`parallel`/`phase`).
- 2026-10-10 — appended **Part 6 — Project Workflow (GSD)** to
  `~/.agents/AGENTS.md` with 5 universally-phrased rules covering
  milestone directory layout, marker-file convention,
  sync_version.sh integration, and the deprecation of flat
  milestone layouts. New Part is operational rather than
  engineering-standard; kept separate from Part 1 to preserve its
  "applies universally" framing. End-to-end test of
  `skill-loader-check.js` workflow returned `verdict: "CLEAN"`
  (✓ workflow runtime, ✓ args propagation, ✓ schema-enforced return).
- 2026-10-10 — slimmed `skills/karpathy-engineer/SKILL.md` (78 → 65
  lines). Removed the 4 core principles that duplicated AGENTS.md
  Part 1; kept the unique parts (output format, `<thinking>` block,
  50-line cap, anti-macro rule, Chinese persona). Skill version bumped
  1.0.0 → 2.1.0; lock-file entry re-hashed with the deterministic
  folder-hash algorithm. Backup at
  `~/.agents/.archive/audit-fix-2026-10-10/karpathy-engineer-SKILL.md.before-slim.bak`.
  User chose Path A (slim, keep skill) over Path B (fully absorb
  into AGENTS.md).
- 2026-10-10 — ran `update-skills` (dry-run then --apply on 5 of 6
  updateable). Pulled upstream content for `claude-api`, `docx`,
  `pdf`, `pptx`, `xlsx`. **Skipped `deploy-to-vercel`**: upstream
  reverts today's P9 audit fix (the `~/.claude/skills/` →
  `~/.agents/skills/` rewrite). 4 local-only skills stayed local.
  Lock-file hashes refreshed for the 5 updated entries; total tracked
  55, mismatches 0. All 5 updated files: frontmatter `name:` still
  byte-identical to parent dir (PAT-20261010-skill-renamer-broke-frontmatter
  pattern check).
- 2026-10-10 — created 10 VS Code Copilot custom agents at
  `~/.copilot/agents/`: `major` (entry-point orchestrator that
  dispatches via the `agent` tool) + 9 specialists (`architect`,
  `coder`, `debugger`, `reviewer`, `researcher`, `tester`,
  `doc-writer`, `laptop-admin`, `software-maintainer`). Each
  specialist is a thin stub that references its canonical role
  file at `~/.agents/opencode/subagent/<name>.md` or
  `~/.agents/agents/<name>.md`. User picks any of the 10 from the
  Copilot chat dropdown; reload VS Code to discover them.
  note: 2026-10-10-copilot-major-and-specialists.md.
- 2026-10-10 — shipped the **clear-technical-communication** Copilot
  skill MVP per
  `~/Downloads/clear-technical-communication-design-plan.md`:
  `~/.copilot/skills/clear-technical-communication/SKILL.md` plus
  3 reference docs (ste-inspired-writing, representation-selection,
  examples-and-evaluation) and a README with verification recipe.
  Adapted the plan's YAML to the actual Copilot-skill convention
  used on this system (`allowed-tools:`, `<objective>`,
  `<execution_context>`, `<process>` sections). 12-line
  concise-defaults addendum added to
  `~/.copilot/copilot-instructions.md`. Plan §14 (MVP) shipped all
  5 deliverables; templates / Phase 3 actual test runs / strict
  STE mode deferred. Awaiting human-in-the-loop Copilot discovery
  verification (reload VS Code → invoke skill → confirm workflow).
  note: 2026-10-10-clear-tech-comm-skill.md.
- 2026-10-10 — **v1.1 of clear-technical-communication**, after user
  said "implement all unfinished tasks". Closed all remaining plan
  items: 5 missing §11 test prompts, all 8 §13 decisions in
  `DECISIONS.md`, P4-02 cross-check (PASS), P4-04 rollback-exercise
  (PASS), P3-01..P3-08 via 10 parallel `copilot -p` runs scored
  against the 8-dimension rubric in
  `references/eval-results-2026-10-10.md`. **Verdict: PASS** at
  grand average 4.76/5; no score < 3 on correctness, completeness,
  honesty. One borderline (P9 interactive artifact, completeness=3)
  noted. Self-assessed; an independent second scorer is recommended
  before promoting to "ready for normal use" in the wiki index.
  Skill at 14 files, 1309 lines. note:
  2026-10-10-clear-tech-comm-skill.md (v1.1 section appended).
- 2026-10-10 — **simplified the agent-architecture from 3 layers to
  2**. Merged the 9 specialist wrappers at L2 into the L1 role
  files themselves by adding `tools:` and `color:` to L1 frontmatter
  (OpenCode ignores the new fields; Copilot reads them). Replaced
  the 9 wrapper files at `~/.copilot/agents/` with symlinks pointing
  at L1. `major.agent.md` stays a real file (no L1 equivalent —
  Major is the Copilot-only orchestrator). AGENTS.md Part 4 updated
  to describe the 2-layer structure (canonical content at
  `~/.agents/` + Copilot-discovery layer via symlinks). Original
  wrappers backed up at
  `~/.agents/.archive/audit-fix-2026-10-10/l2-wrappers-before-symlink/`.
- 2026-10-10 — updated the user-visible docs to reflect the
  2-layer architecture: AGENTS.md Part 5 file tree now lists
  `~/.copilot/agents/` symlinks alongside the canonical L1 tree,
  "Editing the system" teaches the L1+L2 pattern for adding a
  specialist; README.md "Add a new subagent" section explains the
  dual-consumer frontmatter; install.sh gained a "Copilot agent
  discovery layer" section that auto-creates the symlinks from
  `~/.agents/...` to `~/.copilot/agents/`, so a fresh machine run
  produces the same 2-layer state without manual setup. Verified by
  re-running `install.sh` — all 9 specialist symlinks already
  existed (idempotent), the new section emits clean output.
- 2026-10-10 — updated AGENTS.md Part 4 Tool Integration to
  reflect the new Copilot reality: VSCode + Copilot row now lists
  the 10 user-defined agents at `~/.copilot/agents/` and their
  dispatch path (major → agent tool → specialists reading canonical
  role files). Replaced the absolute "OpenCode is the only tool
  with real multi-agent" claim with a "Multi-agent spectrum"
  paragraph that ranks the 5 tools by how they delegate
  (OpenCode subprocesses > pi isolated-context > Copilot agent-tool
  > Codex/Gemini emulation), so the doc no longer overstates the
  isolation guarantees pi and Copilot now provide.
