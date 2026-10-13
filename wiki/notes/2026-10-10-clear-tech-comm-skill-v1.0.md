---
kind: session-note
date: 2026-10-10
session: clear-technical-communication skill v1.0
related:
  - PLAN ~/Downloads/clear-technical-communication-design-plan.md
  - NOTE-20261010-clear-tech-comm-skill-v1.1
  - NOTE-20261010-clear-tech-comm-skill-v1.2
---

# 2026-10-10 — `clear-technical-communication` Copilot skill (v1.0)

Built the MVP per the design plan at `~/Downloads/clear-technical-communication-design-plan.md`. Plan §14 recommended the MVP scope: 5 deliverables. All 5 delivered.

The v1.0 release shipped the **5-deliverable MVP + extensions** (templates, strict-mode toggle, CHANGELOG). v1.1 closed the remaining 13 plan items; v1.2 relocated the skill to the canonical home. See the v1.1 and v1.2 notes for the rest of the story.

## What's in v1.0

```
~/.agents/skills/clear-technical-communication/   (10 files at v1.0; was at ~/.copilot/skills/ until v1.2)
├── SKILL.md                                     main skill (frontmatter + objective / process)
├── README.md                                    verification + uninstall
├── CHANGELOG.md                                 version history
└── references/
    ├── ste-inspired-writing.md
    ├── representation-selection.md
    └── examples-and-evaluation.md
└── templates/                                   (added in v1.0 as an extension beyond MVP)
    ├── explanation.md
    ├── technical-design.md
    ├── comparison.md
    └── incident-report.md

~/.copilot/copilot-instructions.md               +6 bullets
```

## Adaptations from the original design plan

The design plan proposed YAML frontmatter using `tools:` / `color:`
fields. **I adapted to the actual Copilot skill convention in use on this
system**, which uses `name:` / `description:` / `allowed-tools:` with
body sections `<objective>`, `<execution_context>`, `<context>`, and
`<process>`. The plan itself said (§7) "Verify the current skill
discovery convention before implementation" — that's what I did, and
the verified convention won. Skills with the convention I used work
in VS Code 1.141.0; the plan's proposed format might not have.

## v1.0 still pending at release (closed in v1.1)

- 5 of 10 §11 test prompts (closed in v1.1)
- All 8 §13 open decisions (closed in v1.1)
- P4-02 cross-check + P4-04 rollback exercise (closed in v1.1)
- Actual P3-01..P3-08 runs in Copilot (closed in v1.1)

## Verification (manual, run in VS Code) at v1.0

```text
1. ⌘⇧P  →  "Developer: Reload Window"
2. Open Copilot Chat
3. Try: "Use the clear-technical-communication skill to explain Kubernetes Services"
4. Try with strict mode: "Use clear-technical-communication with strictness=strict to rewrite this for a regulator"
5. Try templates: "Use the clear-technical-communication skill to write a runbook for a failed deploy using the incident-report template"
```

## Rollback (still nothing destructive)

```bash
rm -rf ~/.agents/skills/clear-technical-communication
# Then in ~/.copilot/copilot-instructions.md, delete the
# "Default behavior for technical communication" section.
```

## v1.0 design notes

- The skill's `<process>` is 6 steps. Step 3 (STE-inspired writing)
  and Step 4 (representation selection) are the two that change the
  output style; the other steps are largely universal "good technical
  communication" hygiene.
- The skill is intentionally **not invoked** for trivial asks — the
  global addendum's "Trivial asks skip the skill" bullet, plus the
  skill's own `<when_to_invoke>` and `<do_not>`, both encode this.
- Strict mode is a heuristic switch in the skill's frontmatter
  `argument-hint`. It is not enforced by lint or a deterministic
  filter — the agent reading the prompt is what applies the strict
  rules. Both modes carry the same "not certified" disclaimer.

## Related

- `~/AGENTS.md` — universal engineering standards (consumed by all
  the listed tools via the symlink at `~/.agents/AGENTS.md`); the new
  skill pulls on Part 6 (Output Style) implicitly through its
  quality-gate step.
- Plan §13 open decisions resolved (in v1.1): scope = technical
  communication only; invocation = skill-based + global-default
  pointer; language = auto-follow user's request; visual artifacts
  = recommend-only.
- Plan §14 "Recommended MVP" — followed exactly in v1.0; remainder
  closed in v1.1.
