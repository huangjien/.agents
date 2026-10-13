# Routing eval report

n=57 prompts (8 real / 49 synthetic). Labels: human judgment.

| Router | Accuracy |
|---|---|
| route.yaml keywords | 36/57 (63%) |
| laya (no threshold) | 37/57 (65%) |

## Hybrid sweep (laya when confidence >= T, else keywords)

| T | Accuracy |
|---|---|
| 0.4 | 37/57 (65%) |
| 0.5 | 40/57 (70%) |
| 0.6 | 39/57 (68%) |
| 0.7 | 38/57 (67%) |
| 0.8 | 39/57 (68%) |

## Keyword-router errors

- `configure OMP to use ~/.agents/ resources` → kw=smalltalk, truth=laptop_administration
- `what options do I have at style.theme ?` → kw=smalltalk, truth=investigation
- `when I use MiniMax-M3, which is default model, how to calcul` → kw=general, truth=investigation
- `go through current project, check what can I improve. focus ` → kw=implementation, truth=review
- `which model using right now?` → kw=smalltalk, truth=investigation
- `use 'paper-light' as default theme` → kw=smalltalk, truth=implementation
- `why is Kubernetes popular with platform teams?` → kw=debugging, truth=investigation
- `explain how the laya router picks a checkpoint` → kw=review, truth=investigation
- `how do I use the quality-verification skill in CI` → kw=review, truth=investigation
- `fix the crash in my pytest fixture, it broke after the upgra` → kw=software_maintenance, truth=debugging
- `build a small CLI that lists stale worktrees` → kw=software_maintenance, truth=implementation
- `create a draft README for the evals directory` → kw=implementation, truth=documentation
- `update the README to document the new env vars` → kw=implementation, truth=documentation
- `add comments explaining the token budget logic` → kw=implementation, truth=documentation
- `is this SQL injection safe?` → kw=smalltalk, truth=review
- `add tests for the new classifier` → kw=implementation, truth=testing
- `write unit tests for the boundary cases in parse_args` → kw=implementation, truth=testing
- `configure the shell defaults for the agent tools` → kw=smalltalk, truth=laptop_administration
- `install an MCP server for the Codex client` → kw=software_maintenance, truth=laptop_administration
- `find out why the docs build regressed last week` → kw=implementation, truth=investigation
- `I want to understand the evaluation loop in evals_cli` → kw=software_maintenance, truth=investigation

## Laya errors

- `implement @docs/v0.4-video-quality-plan.md , I am going to s` → laya=documentation, truth=implementation
- `what options do I have at style.theme ?` → laya=architecture, truth=investigation
- `when I use MiniMax-M3, which is default model, how to calcul` → laya=implementation, truth=investigation
- `go through current project, check what can I improve. focus ` → laya=architecture, truth=review
- `which model using right now?` → laya=architecture, truth=investigation
- `use 'paper-light' as default theme` → laya=laptop_administration, truth=implementation
- `hi` → laya=architecture, truth=smalltalk
- `thanks, that worked` → laya=debugging, truth=smalltalk
- `why is Kubernetes popular with platform teams?` → laya=architecture, truth=investigation
- `explain how the laya router picks a checkpoint` → laya=documentation, truth=investigation
- `where is the config for the OpenCode Major agent defined?` → laya=laptop_administration, truth=investigation
- `how do I use the quality-verification skill in CI` → laya=review, truth=investigation
- `fix the crash in my pytest fixture, it broke after the upgra` → laya=testing, truth=debugging
- `tests used to pass, now they fail on CI, why is this happeni` → laya=testing, truth=debugging
- `add support for dark mode in the settings panel` → laya=architecture, truth=implementation
- `my disk is almost full, clean it up safely` → laya=architecture, truth=laptop_administration
- `uninstall the old homebrew python and fix the PATH` → laya=software_maintenance, truth=laptop_administration
- `install an MCP server for the Codex client` → laya=implementation, truth=laptop_administration
- `install a package for parsing TOML in the laya venv` → laya=laptop_administration, truth=software_maintenance
- `find out why the docs build regressed last week` → laya=debugging, truth=investigation

Best hybrid threshold: T=0.5 (40/57)
