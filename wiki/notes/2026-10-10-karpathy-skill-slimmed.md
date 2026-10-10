---
kind: skill-edit-note
date: 2026-10-10
session: karpathy-engineer skill slimmed (Path A)
related: PAT-20261010-absorbslim-ordering
---

# 2026-10-10 — karpathy-engineer skill slimmed (Path A)

`~/.agents/skills/karpathy-engineer/SKILL.md` reduced from 78 lines
to 65 lines. The 4 core principles that duplicated AGENTS.md Part 1
were removed. The unique-value parts — output format and negative
constraints — are kept.

## What was kept

Three sections survive:

- **触发条件 (Activation)** — when the skill loads (Chinese
  triggers for coding / refactor / bugfix / architecture)
- **响应模版 (Response Format)** — the `<thinking>` → Action →
  Verification structure. The `<thinking>` block before code is the
  single most valuable thing in this skill and is not in AGENTS.md.
- **负向约束 (Negative Constraints — DO NOT)** — three hard rules:
  - Never delete comments without explaining why in `<thinking>`
  - Never output 50+ lines of new code in one turn (the numeric
    floor that AGENTS.md Rule 3 leaves implicit)
  - Never use black-box macros or template metaprogramming
- **When to suppress** — short opt-out guidance (prose-only,
  trivial edits, non-engineering tasks)

## What was removed

The four numbered `核心原则` (Core Principles) sections that
duplicated AGENTS.md Part 1:

| Removed from karpathy-engineer | Already in AGENTS.md |
|---|---|
| 1. 深度思考阶段 (deep thinking before code) | Rule 1. Think Before Coding |
| 2. 极简主义实现 (micrograd-style, prefer native APIs) | Rule 2. Simplicity First |
| 3. 外科手术式修改 (limit diff scope) | Rule 3. Surgical Changes |
| 4. 验证驱动 (must be verifiable) | Rules 4, 9, 13 (Goal-Driven, Tests Mandatory, Run Don't Assume) |

Plus the meta section (## 元数据 — `ID:`, `Name:`, `Version:`, `Priority:`)
which duplicated the YAML frontmatter.

## Side effects

- `~/.agents/.skill-lock.json`: `karpathy-engineer` entry's
  `skillFolderHash` recomputed (folder-hash algorithm from
  `skill-loader-check.js`); `updatedAt` advanced to 2026-10-10.
- Skill version bumped: 1.0.0 → 2.1.0 (1.0 was installation, 2.0
  would have been a major rewrite, 2.1 reflects a content
  simplification).
- Backup at
  `~/.agents/.archive/audit-fix-2026-10-10/karpathy-engineer-SKILL.md.before-slim.bak`.

## Verifiable result

```
$ ~/.agents/bin/verify-global-agents
Global agent setup: 10 OK / 0 warnings
```

## Why Path A over Path B

User chose to keep the skill slim rather than fully absorbing the
`<thinking>`-block format and the hard 50-line cap into AGENTS.md.
Reasons:
- The Chinese persona + triggers are still useful for code work
  (and would lose their voice if merged into the English doc)
- The skill remains opt-in (description trigger), so non-engineering
  sessions aren't forced into `<thinking>` per response
- Slimming rather than absorbing means the universal rules in
  AGENTS.md stay pure (no format requirements leaking into every
  prose response)

## Future consideration

If AGENTS.md grows to include an "## Output Format" section that
mandates `<thinking>` blocks universally, this skill becomes
nearly empty and should be considered for full removal in a future
session. Not now.

## Related

- `~/AGENTS.md` Part 1 — Engineering Standards
- `wiki/notes/2026-10-10-audit-fixes.md` — last touched the skill
  metadata schema (frontmatter conventions)
