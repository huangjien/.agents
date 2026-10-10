# Template: Technical Design

> **Use when:** the user asks for an architecture, a design proposal, a
> "how should we structure X", or a change plan. This template gives the
> proposal a stable shape that survives review.

---

## TL;DR

Two or three sentences. The decision, the recommended path, the one
trade-off that matters most.

## Context

- **What's the problem / opportunity?** One short paragraph.
- **Who is affected?** (users, developers, ops, finance — be specific)
- **Why now?** (the trigger, the cost of waiting)
- **Out of scope.** One line each on the non-goals.

## Goals and non-goals

- **Goals** (3–5 bullets): observable outcomes, not implementation steps.
- **Non-goals** (3–5 bullets): what we explicitly are NOT solving here.
- **Success metric:** one measurable signal. If we can't name one, the
  goal isn't sharp enough yet.

## Options considered

Present the meaningful alternatives in a comparison table. Columns should
be comparable on the same axes for every row.

| Option | Description | Pro | Con | Cost / effort | Risk |
|---|---|---|---|---|---|
| A. <name> | <one-line> | <one-line> | <one-line> | <S/M/L> | <one-line> |
| B. <name> | | | | | |
| C. <name> | | | | | |

Mark the recommended option with a ✓ in the row's leftmost cell.

## Recommended approach

The choice and the rationale. State the trade-off you accepted in one
sentence ("We lose X to gain Y") and the precondition that would flip the
recommendation ("If [condition], revisit and consider Z instead").

## Detailed design

Walk the reader through the proposed system at the level needed for
review. Use subsections that map to the comparison axes above. Where a
diagram materially helps (architecture, dependencies, data flow), include
one; otherwise prose is fine.

## Migration plan

If the proposal changes existing systems, describe the rollout: phases,
backwards compatibility, feature flags, monitoring, and rollback criteria.

## Open questions

Bulleted list. Mark which ones block approval and which can be deferred.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| <description> | Low / Med / High | Low / Med / High | <one-line> |

## Decision record

A short log entry the reader can copy-paste into whatever ADR file the
project uses. Format below; adapt the path to the project's convention.

```text
[YYYY-MM-DD] <title of this design>
- Decision: <one-line summary of the choice>
- Status: proposed | accepted | rejected | superseded
- Context: <link or one-paragraph summary>
- Consequences: <what becomes easier / harder>
```
