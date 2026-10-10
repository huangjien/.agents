# clear-technical-communication

Copilot Chat skill + global-instructions amendment that helps an AI coding
agent communicate technical information clearly and pick an appropriate
representation for the task.

**Current version:** v1.1 — full Plan §14 scope + 10 §11 test prompts, all 8 §13 decisions logged, P4 audits complete.

## Quick verification in VS Code Copilot

```text
1. ⌘⇧P  →  "Developer: Reload Window"     (so Copilot re-discovers skills)
2. Open Copilot Chat (Agent mode)
3. Try one of these prompts:
   - "What is a Kubernetes Service?"
   - "Compare PostgreSQL pgvector and Qdrant for self-hosted semantic search"
   - "Explain how traffic flows through ingress controller, Service, and Pods"
   - "Write a runbook for a failed deployment"

Expected: the skill applies the workflow (you may see structured progress
in the chat), the response uses prose + an appropriate supporting
representation (table for comparison, possibly a diagram for the
architecture question), and caveats are preserved.

If the skill doesn't auto-trigger, you can explicitly invoke it by name —
e.g., "Use the clear-technical-communication skill to explain…".
```

## File layout

```
~/.copilot/skills/clear-technical-communication/
├── README.md                                    ← this file
├── SKILL.md                                     ← main skill (frontmatter + objective / process)
├── CHANGELOG.md                                 ← version history
├── DECISIONS.md                                 ← §13 open decisions, all 8 logged
├── references/
│   ├── ste-inspired-writing.md                   ← practical writing heuristics
│   ├── representation-selection.md              ← decision table for choosing format
│   ├── examples-and-evaluation.md               ← 10 test prompts + scoring rubric
│   └── eval-results-2026-10-10.md               ← actual Copilot CLI runs + scores
├── templates/                                    ← OPTIONAL starting structures (skill doesn't force them)
│   ├── explanation.md
│   ├── technical-design.md
│   ├── comparison.md
│   └── incident-report.md
└── audits/                                       ← Phase 4 audits
    ├── p4-02-cross-check.md
    └── p4-04-rollback-exercise.md
```

Plus one addendum at `~/.copilot/copilot-instructions.md` (6 bullets) that establishes
the always-on default behavior.

## Mode flag

The skill supports a `strictness` mode flag passed in the chat invocation:

- **Default (`approximate`)** — informal heuristic, ~80% toward ASD-STE100. Apply the writing rules as guidance.
- **`strict`** — tighter application: shorter sentences, no contractions, every acronym spelled out in full on first use, no hedging adverbs, etc.

Example invocations:

```text
Use the clear-technical-communication skill to explain Kubernetes Services
                                          # default: approximate mode

Use the clear-technical-communication skill with strictness=strict to rewrite this paragraph for a regulator
                                          # explicit: strict mode
```

**Important:** *Neither mode certifies formal ASD-STE100 compliance.* They
are heuristic settings; the writing rules in `ste-inspired-writing.md`
remain informal. If true formal compliance matters, use a dedicated
validated STE compliance process instead.

## Versioning

See `CHANGELOG.md` for the version history. Versioning follows roughly
<major>.<minor>: major = structural change (rewriting rules, scope, etc.);
minor = additive (new templates, new references, etc.).

## Uninstall

```bash
rm -rf ~/.copilot/skills/clear-technical-communication
# Then in ~/.copilot/copilot-instructions.md, delete the
# "Default behavior for technical communication" section.
```

The skill is fully self-contained, so removing its directory tree is
sufficient — no other state to clean up.
