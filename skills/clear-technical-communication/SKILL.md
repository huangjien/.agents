---
name: clear-technical-communication
description: "Helps an AI coding agent communicate technical information clearly and choose an appropriate representation. Use for substantial communication tasks: explaining a technical concept or system, rewriting or reviewing documentation, creating design proposals / plans / runbooks / incident reports, comparing architectures or product options, explaining workflows, dependencies, or system relationships, choosing a representation for complex information, or producing learning material. Triggers: 'explain X', 'document this', 'compare A vs B', 'write a runbook', 'rewrite for clarity', 'technical design', 'incident report'."
argument-hint: "[strictness=approximate|strict] [task]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

<objective>
Produce technical communication that is clear, accurate, and proportionate.
Help the user understand, compare, decide, implement, or present.
Output the simplest useful representation for the task and the user's goal.
Preserve technical correctness, important nuance, and the user's intended
meaning. Make assumptions and uncertainty visible. Verify the result
before returning.

This skill targets roughly "80% of the way to ASD-STE100" — it is an
informal heuristic, not a formal standard. It does NOT certify formal
STE compliance.
</objective>

<execution_context>
@~/.agents/skills/clear-technical-communication/references/ste-inspired-writing.md
@~/.agents/skills/clear-technical-communication/references/representation-selection.md
@~/.agents/skills/clear-technical-communication/references/examples-and-evaluation.md
</execution_context>

<when_to_invoke>
Use this skill for substantial communication tasks:

- Explaining a technical concept or system
- Rewriting or reviewing documentation for clarity
- Creating design proposals, plans, runbooks, or incident reports
- Comparing architectures, libraries, or product options
- Explaining workflows, dependencies, or system relationships
- Creating learning material for a specified audience
- Choosing a representation for complex information
- Producing diagrams, charts, interactive pages, or presentation outlines
  when requested or clearly useful

Use the LIGHTWEIGHT approach (no skill invocation) for:

- Simple factual questions
- Short command or syntax lookups
- Small code edits that do not require explanatory documentation
- Direct requests where the user already specified a complete format
- Conversational acknowledgements and trivial follow-ups
</when_to_invoke>

<process>
Execute steps 1 through 6 in order. Adapt depth to the request: a
trivial fact-check skips most of these; a runbook or design plan
runs all six.

**Mode flag (passed via the invocation argument):**
- `strictness=approximate` *(default)* — informal heuristic, ~80% toward
  ASD-STE100. Apply the writing rules as guidance. Suitable for all
  normal communications. *This skill does not certify formal STE
  compliance in either mode; strict mode just tightens the heuristics.*
- `strictness=strict` — tighter application of the writing rules: shorter
  sentences (target ≤ 20 words), no contractions, no idioms or
  metaphors, every acronym spelled out in full on first use, every
  sentence passive-voice-flagged unless active is shorter, no hedging
  adverbs (perhaps, somewhat, generally, typically). Same disclaimer
  applies — strict mode is a heuristic, not formal certification.

If the invoking prompt contains neither word, default to
`approximate`.

**Step 1 — Understand the request**

- Identify the user's outcome, audience, and explicit constraints (format, length, language, tone, deadline)
- If an essential ambiguity could materially change the result, ask ONE focused question
- Otherwise state a reasonable assumption and proceed

**Step 2 — Build an information outline**

- Main answer or recommendation
- Supporting facts and evidence (cite source paths when applicable)
- Steps, dependencies, and relationships
- Risks, exceptions, assumptions, and unresolved questions
- Put the most decision-relevant information first

**Step 3 — Apply STE-inspired writing discipline**

@~/.agents/skills/clear-technical-communication/references/ste-inspired-writing.md

Key heuristics (full list in the reference):
- Prefer common, concrete words; short, direct sentences; one main idea per sentence
- Active voice when the actor matters
- Consistent terms for the same concept
- Make actor, action, object, condition, and result explicit when ambiguous
- Replace vague references ("this", "it", "the above") when unclear
- Explain uncommon acronyms on first use when audience may not know
- Remove filler, repetition, empty transitions
- Keep caveats, qualifiers, and technical detail
- Do NOT claim formal STE compliance

**Step 4 — Select the representation**

@~/.agents/skills/clear-technical-communication/references/representation-selection.md

Match the user's information goal to a representation:
- Prose for direct answers
- Numbered steps / checklist for ordered actions
- Table for comparable items on shared dimensions
- Diagram for relationships, architecture, dependencies
- Code or pseudocode for algorithms or operational behavior
- Chart for numeric trends or distributions
- Interactive HTML only when the environment supports it AND the user benefits
- Slide / explainer-video outline for multi-stage narrative
- Runbook / decision tree for operational execution
- Smallest sufficient representation; do not generate several formats unless useful or requested

**Step 5 — Produce the artifact**

- Start with the answer, decision, or purpose
- Organize details in a logical order
- Use headings that communicate each section's content
- Examples when they add value
- Separate facts, assumptions, recommendations, and open questions when the distinction matters
- For plans: identifiable tasks, owners/role placeholders, dependencies, deliverables, acceptance criteria when requested
- **When asking a clarifying question for a substantial artifact (a long doc, an interactive page, a video outline, a large diagram), pair the question with a small inline alternative** — a one-paragraph recommendation, a 3-row table, a sketched outline, or a one-sentence starting point the user can iterate on. Clarifying questions are not a substitute for output; they are a way to improve the next iteration. (Without the alternative, the completeness dimension of the rubric drops below the threshold for substantial artifacts.)

**Step 6 — Run the quality gate**

Before returning the result, check:

1. Intent: does it answer the actual request?
2. Accuracy: did simplification change the meaning?
3. Clarity: actors, actions, conditions, outcomes clear?
4. Structure: reader can locate the main answer and next action quickly?
5. Terminology: correct and consistent?
6. Completeness: important constraints, risks, caveats retained?
7. Representation: chosen format appropriate and usable?
8. Evidence: uncertainty and unverified claims labelled?
9. Proportionality: effort and detail match task complexity?
10. User requirements: respects requested language, tone, format?

Revise material failures before returning. Do not show the long
internal checklist unless the user asks for an audit.
</process>

<do_not>
- Do not silently change the audience or tone
- Do not turn every answer into a formal document
- Do not generate several output formats for one request unless useful or requested
- Do not create a diagram just because a topic is technical
- Do not claim formal ASD-STE100 compliance — this skill is an informal heuristic
- Do not enforce an arbitrary word limit at the expense of meaning
- Do not skip the quality gate on "trivial" tasks if a one-line check is cheap
</do_not>

<success_criteria>
- Output is the simplest useful representation for the request
- Technical correctness is preserved; no claims of verification that did not happen
- Assumptions and unknowns are labelled, not hidden
- Output length and detail match the task complexity
- User's specified format and language take precedence when reasonable
- Filenames, paths, and identifiers in the output match actual project layout
</success_criteria>
