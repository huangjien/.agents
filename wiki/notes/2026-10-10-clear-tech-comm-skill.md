---
kind: session-note
date: 2026-10-10
session: clear-technical-communication skill MVP shipped
related: PLAN ~/Downloads/clear-technical-communication-design-plan.md
---

# 2026-10-10 — `clear-technical-communication` Copilot skill (MVP shipped)

Built the MVP per the design plan at `~/Downloads/clear-technical-communication-design-plan.md`. Plan §14 recommended the MVP scope: 5 deliverables. All 5 delivered. **v1.1 (this session, later) closed the remaining 13 plan items** (5 missing §11 prompts, 8 §13 decisions, 2 Phase 4 audits, 1 eval-results file). **v1.2 (this session) relocated the skill to the canonical home** after the user pointed out the architectural mistake. See v1.1 and v1.2 sections at the bottom.

## What's in the MVP

```
~/.copilot/skills/clear-technical-communication/   (5 files, 372 lines total)
├── SKILL.md                                     143 lines, main skill
├── README.md                                     61 lines, verification + uninstall
└── references/
    ├── ste-inspired-writing.md                    51 lines
    ├── representation-selection.md               43 lines
    └── examples-and-evaluation.md                74 lines (5 test prompts + rubric)

~/.copilot/copilot-instructions.md               +12 lines (24 total, was 12)
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

## v1.0 — full Plan §14 scope (this session, after MVP)

Added beyond the 5-deliverable MVP:
- **4 templates** at `templates/` (per Plan §4.1):
  - `explanation.md`, `technical-design.md`, `comparison.md`,
    `incident-report.md`
  - Skill recommends them but does not force them
- **`strictness` mode flag** (`approximate` | `strict`) added to the
  skill's `argument-hint` frontmatter. Closes Plan §13 open decision
  #8 (strict STE mode toggle). Both modes remain informal heuristics;
  strict mode just tightens the rules (no contractions, target
  ≤ 20-word sentences, every acronym spelled out, no hedging
  adverbs, etc.)
- **`CHANGELOG.md`** at skill root — version history
- README updated with strict-mode invocation examples

## Still deferred (truly can't be done from this terminal)

- **Phase 3 actual test runs in Copilot** — still requires user to
  reload VS Code and invoke manually
- **Phase 4 P4-01 fix evaluation failures** — depends on Phase 3
  output
- **Visual artifacts / interactive HTML generation tooling** —
  not added; the skill recommends formats when appropriate but
  delegates actual generation to whatever the environment supports

## v1.1 — full plan closure (this session, after "implement all")

The user said "implement all unfinished tasks". What shipped:

- **5 missing §11 test prompts** added to `examples-and-evaluation.md`:
  #5 rewrite (with sample paragraph), #6 uncertainty (with stub),
  #8 visual artifact, #9 interactive artifact, #10 formal customer-facing
- **`DECISIONS.md`** at skill root — formally records all 8 §13 open
  decisions (target client, global location, invocation model, scope,
  language, visual artifacts, version control, strictness). Each with
  date, choice, rationale, limitation.
- **`audits/p4-02-cross-check.md`** — global addendum vs `SKILL.md`
  cross-check; **PASS**, no conflict.
- **`audits/p4-04-rollback-exercise.md`** — exercised the documented
  rollback recipe on a `/tmp` copy. **PASS.** Recommends a more
  robust Python-based one-liner as the recipe.
- **`references/eval-results-2026-10-10.md`** — actual `copilot -p`
  runs of all 10 §11 prompts via the Copilot CLI, with the 8-dimension
  rubric scored per prompt. **Verdict: PASS at the self-assessment
  level.** Grand average **4.76/5**; no score below 3 on correctness,
  completeness, or honesty.
- **CHANGELOG and README** updated to v1.1.

### One borderline item found in the eval

**P9 (interactive HTML) got a 3 on completeness.** The skill asked a
clarifying question instead of producing a usable alternative (a
static table or written recommendation) as §11 expected. Per the
skill's process step 1, asking a clarifying question is allowed, but
the §11 expected behavior is "produce the artifact OR state the
limitation AND offer a usable alternative". The current response
delivered the first half (asked) but not the second (no alternative
yet). Improvement noted in `eval-results-2026-10-10.md` — easy add:
step 5 should produce a small static alternative inline before/while
asking the clarifying question.

### Self-assessment limitation

The scorer is the same agent that ran the prompts. The scoring is
honest per the rubric, but treat as self-graded. An independent
second pair of eyes is recommended before promoting to "ready for
normal use" in the wiki index.

## Verification (manual, run in VS Code)

```text
1. ⌘⇧P  →  "Developer: Reload Window"
2. Open Copilot Chat
3. Try: "Use the clear-technical-communication skill to explain Kubernetes Services"
4. Try with strict mode: "Use clear-technical-communication with strictness=strict to rewrite this for a regulator"
5. Confirm the 6-step workflow appears in the response
```

Expected: structured workflow applied; appropriate representation
chosen (prose / table / diagram / etc.); caveats preserved.

Files at v1.1 (current):
```
~/.copilot/skills/clear-technical-communication/
├── SKILL.md              159 lines
├── README.md              92 lines
├── CHANGELOG.md           43 lines
├── DECISIONS.md          119 lines (8 §13 decisions logged)
├── references/
│   ├── ste-inspired-writing.md     51 lines
│   ├── representation-selection.md 43 lines
│   ├── examples-and-evaluation.md  117 lines (10 test prompts)
│   └── eval-results-2026-10-10.md 305 lines (actual CLI runs + scores)
├── templates/
│   ├── explanation.md               41 lines
│   ├── technical-design.md          80 lines
│   ├── comparison.md                60 lines
│   └── incident-report.md           74 lines
└── audits/
    ├── p4-02-cross-check.md         49 lines
    └── p4-04-rollback-exercise.md   76 lines
```
Total: 14 files, 1309 lines

## Rollback (still nothing destructive)

```bash
rm -rf ~/.copilot/skills/clear-technical-communication
# Then in ~/.copilot/copilot-instructions.md, delete the
# "Default behavior for technical communication" section.
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

## Verification — what's done vs. what's pending

✅ Files exist on disk; YAML frontmatter parses; install.sh still OK;
verify-global-agents still 10 OK / 0 warnings; the 2-layer agent
architecture (`.agents/` + symlinks at `~/.copilot/agents/`) is intact.

⏳ **Skill discovery in Copilot** — not verified in VS Code this
session. Requires:
1. `⌘⇧P → Developer: Reload Window`
2. Open Copilot Chat
3. Type: "Use the clear-technical-communication skill to explain Kubernetes Services"
4. Confirm the skill's workflow appears in the response

See `~/.copilot/skills/clear-technical-communication/README.md` for
the full verification recipe (30 seconds).

The plan §15 "Completion Definition" requires this discovery check
before final release; right now this MVP is in the "files written,
awaiting human-in-the-loop verification" state.

## Backup / rollback

Nothing in this MVP is destructive:
- `~/.copilot/copilot-instructions.md` — added 12 lines at the bottom
  (full file is 24 lines); rollback = delete the addendum section
- `~/.copilot/skills/clear-technical-communication/` — net-new directory;
  rollback = `rm -rf` it

Both reversals are documented in the skill's `README.md`.

## Related

- `~/.agents/AGENTS.md` — universal engineering standards (consumed via
  `~/AGENTS.md` symlink); the new skill pulls on Part 6 (Output Style)
  implicitly through its quality-gate step
- Plan §13 open decisions: scope = technical communication only (vs
  general writing); invocation = skill-based + global-default
  pointer; language = auto-follow user's request; visual artifacts =
  recommend-only for MVP
- Plan §14 "Recommended MVP" — followed exactly

## v1.2 — relocated to canonical home (this session)

The user pointed out the new skill was at `~/.copilot/skills/` (where
it was originally placed per the design plan's literal directory path)
instead of `~/.agents/skills/` (where all 55 version-tracked skills
live). I followed the plan without re-checking the actual convention;
that was the architectural mistake.

**What was done:**

1. **Moved** `clear-technical-communication/` from
   `~/.copilot/skills/` → `~/.agents/skills/`.
2. **Added to `.skill-lock.json`** with `source: local`,
   `sourceType: filesystem`, `skillPath: skills/clear-technical-communication/SKILL.md`.
   The 55 → 56 skills count in the lock file.
3. **Updated the global addendum** in
   `~/.copilot/copilot-instructions.md` to point to the new path.
4. **Updated all internal path references** in `SKILL.md`, `README.md`,
   `audits/p4-02-cross-check.md`, `audits/p4-04-rollback-exercise.md`,
   `references/eval-results-2026-10-10.md`.
5. **CHANGELOG and README** updated to v1.2.

**Folder hash:** the original installer algorithm is no longer
present in the tree (the 55 existing entries were generated by an
external tool whose source is gone). I used a stable, documented
alternative: `sha1` of the sorted concatenation of file contents.
This is a deviation from the installer's algorithm; the field is
labeled with a `_note` documenting the choice. If a re-install of
this skill is later triggered, the installer will compute its own
hash and overwrite the `_note` field — the rest of the entry format
is the standard local-skill schema.

**Why Copilot still finds it:** the CLI's discovery scope lists
`Personal: ~/.copilot/skills/ or ~/.agents/skills/`, so moving the
dir to `~/.agents/skills/` keeps it discoverable for both VS Code
Copilot and the CLI. Verified with `copilot skill list` (inherited
skills include clear-technical-communication).

**PAT candidate:** PAT-20261010-skill-home-convention — "follow the
plan's literal directory path without checking the actual system
convention". One instance so far. Will track; promote at 3.
