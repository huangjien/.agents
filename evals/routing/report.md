# Routing eval report

n=57 prompts (8 real / 49 synthetic). Labels: human judgment.

| Router | Accuracy |
|---|---|
| route.yaml keywords | 57/57 (100%) |
| laya (no threshold) | 38/57 (67%) |

## Laya-first hybrid (rejected: worse than keywords alone)

laya intent when confidence >= T, else keywords:

| T | Accuracy |
|---|---|
| 0.4 | 44/57 (77%) |
| 0.5 | 49/57 (86%) |
| 0.6 | 50/57 (88%) |
| 0.7 | 51/57 (89%) |
| 0.8 | 54/57 (95%) |

## Keyword-first hybrid (production rule)

Keyword router when a trigger or greeting matches; otherwise
laya (smalltalk gate, then intent at `answer_confidence >= 0.5`);
otherwise the keyword result stands (question-shortcut or
general fallback).

Accuracy: 57/57 (100%)

## Keyword-router errors


## Laya errors

- `implement @docs/v0.4-video-quality-plan.md , I am going to s` → laya=documentation, truth=implementation
- `what options do I have at style.theme ?` → laya=architecture, truth=investigation
- `when I use MiniMax-M3, which is default model, how to calcul` → laya=implementation, truth=investigation
- `go through current project, check what can I improve. focus ` → laya=architecture, truth=review
- `which model using right now?` → laya=architecture, truth=investigation
- `use 'paper-light' as default theme` → laya=laptop_administration, truth=implementation
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

Laya-first hybrid best: T=0.8 (54/57) — rejected.
Production rule: keyword-first with laya fallback (57/57).
