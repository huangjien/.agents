---
name: skill-wiki
description: Maintain the skill-evolution wiki at ~/.agents/wiki/ — record failure/success patterns from sessions as root-caused pattern pages, then compile them into atomic, audited skill edits (WikiSkill-style). Use when the user says "record a pattern", "log this failure/success", "skill retro", "compile/evolve skills", or wants skills improved from accumulated experience instead of ad-hoc edits.
metadata:
  author: local
  version: "1.0.0"
  last_reviewed: 2026-09-26
  source: ""
  local_only: true
---

# Skill Wiki — accumulate patterns, evolve skills

A persistent wiki of failure patterns and workarounds sits between raw
session experience and the active skills in `~/.agents/skills/`. Skills
are only edited through atomic proposals compiled from wiki patterns,
with every diff and outcome audited. Full docs: `~/.agents/wiki/README.md`.

## Scope rule (read first)

The wiki is read **only** inside this skill. Never inject wiki content
into always-on context, instruction files, or task prompts — leaked
workarounds degrade task trajectories and future pattern quality.

## Workflow A — Record (Wiki Maintainer)

Run after a notable failure, surprise, or workaround, when the user asks
to log/record it or do a skill retro.

1. **Root cause first.** Name the mechanism, not the surface symptom.
   If you cannot state why it happened, say so and mark the pattern
   `status: candidate` with the open question.
2. **Write the pattern.** Copy `~/.agents/wiki/patterns/_TEMPLATE.md` to
   `patterns/PAT-YYYYMMDD-short-slug.md`. If a matching pattern already
   exists, patch it (append/replace the relevant span) — never rewrite a
   page wholesale.
3. **Tag models.** List which models exhibited/validated the pattern in
   `models:`. `[]` means tool/environment behavior. Single-model quirks
   stay in the wiki forever — never promote them into shared skills.
4. **Update the catalog.** One new line in `index.md`; one entry appended
   to `logs.md`.

The wiki is never rolled back. A bad pattern gets `status: rejected` or
is superseded by a refined pattern — deletion is not an option.

## Workflow B — Compile (Skill Proposer)

Run when the user asks to compile/evolve skills, or when several patterns
have accumulated (rule of thumb: ≥3 candidates targeting the same skill).

1. **Read** `index.md` and `skill-impact.md`. Avoid re-proposing rejected
   ideas verbatim; look for `superseded` chains worth refining instead.
2. **Pick one target.** One pattern (or small set motivating one change)
   → one skill in `~/.agents/skills/` → one atomic, patch-style edit
   (add/replace a span). No bulk rewrites.
3. **Record before applying.** Append to `skill-impact.md`: date, target
   skill, motivating pattern ids, unified diff, and a validation plan
   the user can execute on real tasks.
4. **Apply** the edit and set the pattern `status: promoted`.
5. **Announce** the validation plan in one or two sentences.

## Validation gate

The user validates on real tasks over the following days. When told the
outcome (or when asked to review pending proposals), update the entry's
**Outcome** in `skill-impact.md`. `rejected` → revert the skill using the
recorded diff; the pattern keeps its history. A `git init` in
`~/.agents` would make rollback trivial — only do it if the user asks.

## Anti-goals

- No wiki content in task-time context, ever.
- No model-specific workarounds in shared skills.
- No direct skill edits bypassing Workflow B.
- No rewriting pattern pages or skills wholesale.
