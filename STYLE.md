# STYLE.md — Code Style Standard

> Gap-filling default for every agent and subagent. A repo's own linter/formatter
> ALWAYS wins over this doc (AGENTS.md rule 11). This doc applies when a repo has
> no tooling, or a decision isn't mechanically enforced.

## Agents first

加载本仓库的 agent(pi、OMP、OpenCode、Copilot、Codex、Gemini)是仓库内容
的主要使用者。每一个工件先服务 agent,再服务人。冲突时,agent 的可确定性
赢过人类的可读性。

### 选择

| 决策点 | 规则 |
|---|---|
| 语气 | 直白命令(`检查 X`);不用也许 / 你可以 |
| 结构 | 表格 > 散文;有结构数据就用 frontmatter |
| 例子 | 一个具体例子 > 一条抽象规则 |
| 长度 | 短,尽量紧,20 词是下限不是上限 |
| 冲突时 | agent 可确定性 > 人类阅读美感 |

### 例外 —— 这些地方人工优先

| 路径 | 谁优先 | 写给谁 |
|---|---|---|
| `README.md`、`install.sh` | 人工 | 安装者 |
| `wiki/notes/` | 人工 | 未来的审计者(带日期) |
| `wiki/patterns/` | **agent + 人工** | 双向 —— agent 按需查;`AGENTS.md` 已引用 |
| `wiki/audits/` | 人工 | 评审者 |
| `wiki/index.md`、`wiki/logs.md` | 人工 | 导航索引 |
| commit 信息 | 人工 | reviewer 概览 |

写入方式:patterns 必须可被 agent 加载(frontmatter + 引用),notes/audits
只人读。给 agent 喂 notes 会让 prompt 膨胀,还会让 agent 把今天为什么
这么做误读成必须这么做。

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
- **Type safety (TS)**: no `as any`, no `@ts-ignore`, no `@ts-expect-error`,
  no `// eslint-disable` for type errors. If the types are wrong, fix the
  types, not the suppression — use generics and narrowing.
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

The `code-review` skill checks size caps and naming against this doc. A
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
