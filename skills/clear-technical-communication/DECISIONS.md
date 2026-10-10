# Decisions Log

Resolves the §13 "Open Decisions for Review" checklist from
`~/Downloads/clear-technical-communication-design-plan.md`. Each entry
records the date, the chosen option, the rationale, and any limitations
or follow-ups.

## 13.1 — Target clients

**Date:** 2026-10-10
**Decision:** VS Code Copilot only. Plus Copilot CLI (where available) for smoke tests.
**Rationale:** the user's primary working environment is VS Code. CLI
support is opportunistic (it discovers `~/.copilot/skills/`) but is
not the primary target. Other clients (JetBrains, Copilot Web, etc.)
are not validated.
**Limitation:** skill content should be portable, but visual / HTML
artifacts may not be discoverable in all clients.

## 13.2 — Global location

**Date:** 2026-10-10
**Decision:** `~/.copilot/copilot-instructions.md` (existing 12-line
slim-pointer file).
**Rationale:** it is the file VS Code Copilot reads for always-on
behavior, and the system already uses it. Editing it preserves the
existing structure (a thin pointer to `~/AGENTS.md` plus the GSD
instructions link).
**Change made:** appended a 12-bullet "Default behavior for technical
communication" section under a new `## Default behavior for technical
communication` heading. The existing pointer and the GSD reference are
untouched.

## 13.3 — Invocation model

**Date:** 2026-10-10
**Decision:** both, where supported. Auto-discovery through the skill
description (long trigger list in the `description:` frontmatter field);
explicit invocation by name when the user types
"Use the clear-technical-communication skill to …" or appends
"with strictness=strict" to switch mode.
**Rationale:** auto-discovery handles the common case without forcing
the user to name the skill; explicit invocation handles the strict-mode
case and any case where the agent's auto-trigger missed the trigger.
**Limitation:** trigger phrases are best-effort; if the user reports
the skill is not auto-triggering on a substantial request, the trigger
list may need widening.

## 13.4 — Scope

**Date:** 2026-10-10
**Decision:** technical communication only. General writing and
learning material are out of scope.
**Rationale:** keeps the skill's process and examples focused;
avoids overlap with `internal-comms` (general status reports),
`docx` / `pdf` / `pptx` (specific file types), and
`doc-coauthoring` (general doc drafting workflow).

## 13.5 — Language

**Date:** 2026-10-10
**Decision:** follow the user's request language automatically.
**Rationale:** the user's `AGENTS.md` and the `gsd-protocol` are
mixed-language friendly; the skill itself is written in English but
its `<process>` is language-neutral. No language switch is hard-coded.

## 13.6 — Visual artifacts

**Date:** 2026-10-10
**Decision:** recommend only. The skill advises when a diagram, chart,
or interactive HTML would help, but does not auto-generate them. The
agent that runs the skill (Copilot Chat, CLI, etc.) decides what it
can produce.
**Rationale:** the skill runs in different Copilot environments with
different rendering capabilities; mandating diagram generation in the
skill would force the agent to fail or fake output in environments
that don't support it. Keep the skill environment-agnostic.

## 13.7 — Version control

**Date:** 2026-10-10
**Decision:** no Git repository is being created for `~/.copilot/`. The
changelog in this skill's `CHANGELOG.md` and the
`~/.agents/wiki/notes/2026-10-10-clear-tech-comm-skill.md` note serve
as the durable record.
**Rationale:** `~/.copilot/` is the user's personal config, not a
shared project; no team collaboration. A Git repo here would add
maintenance overhead without solving a coordination problem. If a team
adopts the skill later, the canonical location is `~/.agents/` (under
version control) and symlinks to `~/.copilot/skills/`.

## 13.8 — Strictness

**Date:** 2026-10-10
**Decision:** yes — the skill supports a `strictness=strict` mode
that tightens the writing rules (shorter sentences, no contractions,
every acronym spelled out, no hedging adverbs). Default is
`strictness=approximate`. Both modes are **informal heuristics**, not
formal STE compliance.
**Rationale:** Plan §13 specifically asked whether strict mode
should be a toggle. The user can opt in when the audience is more
formal (e.g., a regulator). Both modes carry the same "not certified"
disclaimer to prevent misuse.
**Frontmatter:** `argument-hint: "[strictness=approximate|strict] [task]"`.
**Limitation:** strict mode is enforced by the agent's reading of the
`<process>` step 3 rules, not by a deterministic filter. It is a
heuristic prompt, not a lint.

---

## Decision-style notes

- Decisions are recorded when made, not retroactively. Earlier wiki
  notes mention "VS Code only" as an implicit assumption; this file
  makes it explicit.
- Reversing a decision = editing this file + (if needed) the file the
  decision points to. Both are reversible.
- A future v2.0 of the skill may revisit §13.2 (move the global
  addendum to its own file at `~/.copilot/instructions/clear-comm.instructions.md`
  if the global file grows past 50 lines).
