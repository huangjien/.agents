# Representation Selection

**Use when:** The skill's process hits **Step 4 — Select the representation**.

Pick the **simplest representation** that makes the information easy to understand or use for the user's stated goal.

## Decision table

| User need / information shape                | Preferred representation         | Use when                                                              |
|---------------------------------------------|----------------------------------|----------------------------------------------------------------------|
| Direct answer                               | Short prose                      | The answer is simple and linear                                      |
| Ordered action the user must perform        | Numbered steps / checklist       | Sequence matters; verification steps implied                        |
| Comparison of several options               | Table                           | Options share comparable attributes; trade-offs deserve side-by-side  |
| Relationships, architecture, dependencies    | Diagram                         | Spatial or relational structure matters                             |
| Algorithm or exact behavior                 | Code or pseudocode              | Operational detail is easier to inspect formally than in prose       |
| Numeric trend or distribution               | Chart                           | The data supports meaningful visual comparison                       |
| Explore, filter, or manipulate              | Interactive HTML                 | Interaction materially helps; environment supports it                |
| Multi-stage learning or narrative          | Slide / explainer-video outline  | Visual sequencing and narration add value                           |
| Operational execution with checks + branches | Runbook / decision tree         | The user needs actions, gates, and decision points                    |

## Restraint rules

- Prefer **prose plus one supporting representation** when that is sufficient.
- **Tables are not a substitute for explaining important conclusions.** Follow the table with the takeaway.
- **Charts require meaningful data.** If the numbers aren't comparable, prose is better.
- **Do not propose interactive HTML** if the environment cannot deliver it or the user only needs text.
- **Treat video generation as a substantial deliverable.** It requires explicit user intent, suitable tooling, and usually review checkpoints.
- **Follow the user's requested format** when it is reasonable. Override only when their request would degrade clarity, correctness, or proportionality.

## Selection flow (use in order)

1. **Identify the user's information goal** — understand, compare, decide, implement, present.
2. **Match the goal to a row** in the decision table above.
3. **Apply restraint rules** — strip excess, don't over-format.
4. **Tie-break**: when two representations are equally well-suited, default to **prose plus one supporting format** (table OR diagram OR code, not multiple).
5. **Final check**: if the format adds visual weight without adding clarity, drop it.

## Worked examples (sketch, not rules)

- "What is X?" → short prose, maybe one example sentence.
- "Compare A vs B" → 1 paragraph of framing + a table of comparable dimensions + 2 sentences on trade-offs.
- "How does traffic flow through the system?" → 1 paragraph on the sequence + a diagram (if the environment supports it) + a footnote on edge cases.
- "Write a runbook for a failed deploy" → checklist of pre-checks + numbered diagnostic tree + escalation contacts + rollback criteria.
