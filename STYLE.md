# STYLE.md — Code Style Standard

> Gap-filling default for every agent and subagent. A repo's own linter/formatter
> ALWAYS wins over this doc (AGENTS.md rule 11). This doc applies when a repo has
> no tooling, or a decision isn't mechanically enforced.

## Naming

| Language | Functions/vars | Types/Classes | Constants | Files |
|---|---|---|---|---|
| Python | `snake_case` | `PascalCase` | `UPPER_SNAKE` | `snake_case.py` |
| JS/TS | `camelCase` | `PascalCase` | `UPPER_SNAKE` | `camelCase.ts` (workflows: `verb-noun.js`) |
| Bash | `snake_case` | — | `UPPER_SNAKE` | `kebab-case` (`laya-classify`) |
| Markdown | — | — | — | `UPPER-snake` dir names stay as-is (`SKILL.md`, `AGENTS.md`) |

- `_leading_underscore` = private/module-internal, everywhere.
- Names say the job: `classify_intent`, not `process_data2`.
- Booleans read as predicates: `is_ready`, `has_errors`, `should_retry`.
- Skills: frontmatter `name:` byte-identical to the directory name (hub rule).

## Size limits

Hard defaults; exceeding one requires a one-line justification in review.

| Unit | Cap | Fix when exceeded |
|---|---|---|
| Function/method | 40 lines (excl. comments/docstring) | split by sub-responsibility |
| Parameters | 4 | take an options object/dict |
| File | 400 lines | split by responsibility |
| Nesting depth | 3 levels | guard clauses / early returns |
| Line width | 100 chars (soft) | break at operators |

- A function longer than 40 lines is only OK if it is one flat sequence with no
  conditionals worth extracting (e.g. a config table builder).
- If you cannot name the halves of a function, it is one job — don't split it.

## Patterns

- **Errors**: loud > silent. Raise/throw with context (`ValueError(f"...{got}")`),
  never a bare `except:`; no swallowing to "keep going". Fail fast at boundaries.
- **Guard clauses first**: validate inputs and return/raise at the top; the happy
  path sits unindented at the bottom.
- **No boolean flag parameters** — `render(x, is_mobile=True)` becomes two names.
- **Magic numbers** become named constants at module top, with the unit in the
  name (`MAX_RETRY_SECONDS = 30`).
- **Comments explain why**, never what. Delete commented-out code. Git keeps
  the history. TODOs carry an owner and a date or get deleted.
- **Imports**: stdlib → third-party → local, one group per blank line, no
  wildcards.
- **Docstrings**: exported/public functions get at least a one-liner that states
  the contract, not the implementation.
- **Bash**: `set -euo pipefail`, quote all `"$var"` expansions, document exit
  codes in the header (see `bin/` scripts for the house shape).
- **JS/TS async**: `await` over promise chains; no `await` inside loops unless
  order is required — batch with `Promise.all` (matches `parallel()` in workflows).

## Commits

- Subject: imperative mood, ≤ 50 chars, no period — `add laya gate to workflows`
- Body (when non-trivial): what changed + why, wrapped at 72.
- One logical change per commit; never mix refactor + feature.

## Review hooks

`reviewer` and `tester` check size caps and naming against this doc. A
violation with no justification is a blocking comment, not a nitpick.

Testing (full standard = AGENTS.md rule 9): every bug fix ships with its
failing-first regression test. Report changed-file coverage. Justify any
drop in one sentence.

## Documentation — 80% ASD-STE100

Apply to every hub document (READMEs, SKILL.md bodies, role files, mcp/ docs,
AGENTS.md prose). Full ASD-STE100 is overkill for an agents hub. This subset
gives most of the clarity at a fraction of the rules.

### Vocabulary

- Prefer small verbs: use, make, put, show, check, test, start, stop, keep,
  add, remove, run, write, read, find, fix, follow, allow, prevent.
- One word, one meaning. Do not rotate synonyms — pick "check" or "verify",
  not both, within one document.
- Replace wordy forms: "utilize" → "use", "prior to" → "before",
  "in order to" → "to", "carry out" → "do", "make sure" → "check".
- Keep identifiers, paths, and flags byte-exact as they appear in code.

### Sentences

- Max 20 words. One topic per sentence. Split instead of join.
- Active voice. Imperative for instructions. Present tense ("the server
  restarts", not "the server will restart").
- No "-ing" instruction forms ("Checking..." → "Check...").
- Requirements stay modal-plain: MUST / DO NOT, or a direct imperative.
  Never soften a requirement with "should probably".

### Structure

- Paragraph ≤ 6 sentences, one purpose. Three or more items → a list.
- No stacked relative clauses ("the function that returns the value that...").
  Split into two sentences.
- Tables, code blocks, frontmatter, and headings keep their exact content;
  this section governs prose only.
