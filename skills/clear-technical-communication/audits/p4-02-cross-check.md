# P4-02 Audit — Cross-check global addendum vs `SKILL.md`

**Date:** 2026-10-10
**Audit scope:** identify duplicates and conflicts between
`~/.copilot/copilot-instructions.md` (12-line "Default behavior for
technical communication" addendum) and
`~/.agents/skills/clear-technical-communication/SKILL.md` (process +
do-not).

## Method

Side-by-side comparison of:
1. The 6 bullets in the global addendum.
2. The 6 process steps + 7 do-not items in `SKILL.md`.
3. The 3 design principles in the design plan that both should reflect
   ("Smallest sufficient artifact", "Meaning before brevity", "No
   invented facts").

## Findings

| Topic | Global addendum says | `SKILL.md` says | Conflict / overlap |
|---|---|---|---|
| Plain language | "Prefer plain language and concrete terms…" | `<process>` step 3 (STE-inspired rules) and the reference doc | Intentional overlap — the global rule is a shorter form of step 3. The plan §4.1 explicitly directs this: "The global instruction should not duplicate the entire skill. It should establish the default and direct the agent to use the skill for substantial tasks." |
| Format selection | "Choose the simplest useful representation" | `<process>` step 4 + `representation-selection.md` reference | Intentional overlap; same reason. |
| Lead with answer | "Lead with the answer, decision, or purpose" | `<process>` step 5 (Produce the artifact) | Intentional overlap. |
| Mark assumptions | "Mark assumptions and unknowns; do not claim verification that did not happen" | `<process>` step 2 (outline) and quality-gate check 8 (evidence) | Intentional overlap. |
| Trivial asks skip skill | "Trivial asks… skip the skill and answer directly" | `<when_to_invoke>` and `<do_not>` "Do not skip the quality gate on trivial tasks" | **No conflict.** The global rule says "don't run the heavy process"; the skill's do-not says "if you do answer trivially, still apply the one-line check". They reinforce each other. |
| ASD-STE disclaimer | "Skill targets ~80% of the way to ASD-STE100; does not certify formal compliance" | Same disclaimer (mode-flag block in `<process>`) | Intentional overlap; same text in both. |

## Verdict

**PASS.** No conflicts, no unintentional duplication. The global
addendum is the always-on shorthand; the skill is the detailed
workflow. The 6 bullets in the addendum are the highest-level summary
of the 6 process steps in the skill, with one bullet per step. This is
the intended layering per plan §4.1.

## Action

No change required. If a future edit introduces a conflict, the rule is:
**the skill wins** for cases that the agent has invoked; the **global
addendum wins** for cases where the agent is not invoking the skill.

## Reverse direction

The global addendum could be cut down to 3 bullets (referencing the
skill for the rest) without losing meaningful information, since the
agent would still be following the skill's process. Kept as-is for
now because the 6-bullet form is short and self-contained.
