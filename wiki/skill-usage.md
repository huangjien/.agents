# Skill usage log

One row per delivered use of a skill. Agents appending here follow the
rule in `~/.agents/AGENTS.md` ("Skills" section).

Review protocol: after 2–4 weeks of rows, run the cull review described
in `wiki/notes/2026-10-13-skill-cull-candidates.md`. Skills with zero
rows and overlapping scope become cull or merge candidates.

| Date | Skill | Tool |
|---|---|---|
| 2026-10-18 | video | omp (Claude) |
| 2026-10-18 | research-methods | ZCode |
| 2026-10-24 | software-maintenance | omp (MiniMax-M3) |
- 2026-10-26 | system-design | pi (cross-model judging design + apply)
- 2026-10-26 | video | opencode (MiniMax-M3) — 矛盾的解决之道: draft→make, fixed placeholder props + fabricated numbers in visual-builders
- 2026-10-26 | video | opencode (MiniMax-M3) — youtube --upload now generates+sets the thumbnail itself; pruned all projects/**/*.mp4 (15G→934M), masters backed up to scratch
- 2026-10-26 | video | opencode (GLM-5.3) — conflicts-resolution-en: en-US whiteboard hybrid (4 sketches + 12 diagram components), 87.2/B best-of-8 draft
- 2026-10-26 | video | pi — seven-basic-plots engine picker added to chinese-storybook draft+review profile blocks, pinned by channel-profile tests
- 2026-10-27 | diagnose | pi (MiniMax-M3) — reproduced and fixed PyPI wheel omission of core.persona.persona with a release-path regression test
- 2026-10-27 | improve-codebase-architecture | pi (MiniMax-M3) — audited NovelScribe release contract, quality gates, dual Pipeline ownership, domain context, and repository hygiene
- 2026-10-27 | karpathy-engineer | pi (MiniMax-M3) — implemented novelscribe public facade + release contract + quality gate as vertical slices with think/action/verify format
- 2026-10-27 | grill-with-docs | pi (MiniMax-M3) — 12-decision grill session for PyPI library surface; ADR-0014 + CONTEXT.md/CONTEXT-MAP.md updated inline
- 2026-10-27 | grill-with-docs | pi (MiniMax-M3) — candidate #4 domain repair: created frontend/CONTEXT_studio.md glossary, fixed context map/root CONTEXT/AGENTS.md stale layers, archived GAPS+REVIEW_REPORT, added root README
- 2026-10-27 | grill-with-docs | pi (MiniMax-M3) — candidate #3 grill: 4 decisions (canonical Python asset tree, rsync+pytest drift gate, two-layer conformance contract w/ non-goals table, shared CI-verified fixture) → ADR-0015
- 2026-10-27 | karpathy-engineer | pi (MiniMax-M3) — candidate #3 implementation: sync target + 3 pytest vectors + mirrored Dart vector + symlink-deference fix, red/green at every slice
- 2026-10-27 | karpathy-engineer | pi (MiniMax-M3) — candidate #5: segment-based repo-hygiene guard (red→green), 9 local-state paths staged for untrack incl. re-added OPENAI_API_KEY + 2×15MB SQL backups the audit missed
- 2026-10-27 | karpathy-engineer | pi (MiniMax-M3) — committed 3-commit series (library+gate+hygiene / conformance / domain docs) after fixing check_project_health.sh for packages.find + discovering pre-commit stash semantics force self-consistent commits
- 2026-10-28 | improve-codebase-architecture | OpenCode (GLM-5.3) — dual-surface friction survey (Python+Dart explore agents) → 5 deepening candidates; user skipped grilling, all candidates consolidated into v8.5 milestone (marker+design+tasks+index row)
- 2026-10-28 | karpathy-engineer | OpenCode (GLM-5.3) — v8.5 P1 dead-surface purge executed: −10,650 lines across 44 files, 7 greps clean, make check green @96.97% cov; restored live SuggestionOrchestrator suite the survey mislabeled as deprecated-Orchestrator tests
- 2026-10-28 | karpathy-engineer | OpenCode (GLM-5.3) — v8.5 P2 runtime seam: entry gate deleted, AgentRuntime folded into RuntimeKernel (one facade, _child_config single reconstruction), store-before-engine bug fixed w/ regression test, subagent dup gone, ADR-0017 + CONTEXT.md updated; make check green
- 2026-10-28 | karpathy-engineer | OpenCode (GLM-5.3) — v8.5 complete (44/44 tasks): Python Executor→3 modules + one runtime facade (ADR-0017, checkpoint bug fixed) + honest quality + 175-patch farm removed; Dart local-run lifecycle closed + one catalog/asset-path/message-tier vocabulary + dead surfaces purged; version 8.5.0; make check green (6987 py) + flutter analyze clean / 2205 dart
- 2026-10-28 | diagnose | OpenCode (MiniMax-M3.1-Flash) — "Pi couldn't start" in Orca: global pi package (pi-novel-scribe) threw at extension registration when cwd lacked config/route.yaml → pi exit 1; fixed by lazy call-time route load + 3 regression tests (red→green)
