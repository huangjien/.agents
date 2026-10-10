---
name: karpathy-engineer
description: Karpathy-style output format for code work. Use the `<thinking>` block + Action + Verification structure; respect the 50-line new-code cap, comment-preservation rule, and anti-macro/anti-metaprogramming rule. Use when writing code, refactoring, fixing bugs, or designing systems.
metadata:
  author: personal
  version: "2.1.0"
  last_reviewed: 2026-10-10
  source: ""
  local_only: true
  note: "Core principles (think-before-code, simplicity, surgical diffs, verification-driven) now live in `~/AGENTS.md` Part 1. This skill keeps only the output-format + negative-constraint layer those rules don't carry."
---

# Skill: Karpathy-Style Engineering (KSE) — Format & Constraints

## 触发条件 (Activation)

When the user asks for: 编写代码 (Coding)、重构 (Refactor)、修复缺陷
(Bug Fix)、系统设计 (Architecture). In agent/automation mode, default-on.

## 响应模版 (Response Format)

Every code/diff response is structured in three parts, in this order:

```text
1. Thinking:    <thinking> ... </thinking>
2. Action:      [the surgical code change]
3. Verification:[the command or test that proves the change works]
```

The `<thinking>` block goes **before** the code block. It contains:

- Confirmation of the requirement (no ambiguity left)
- 2–3 implementation options with their tradeoffs
- Why the simplest option wins (mirrors `~/AGENTS.md` Rule 2)
- For non-trivial changes: a one-sentence statement of **what was deliberately *not* changed** and why (mirrors `~/AGENTS.md` Rule 3)

## 负向约束 (Negative Constraints — DO NOT)

- **Never delete existing comments without explaining why** in the
  preceding `<thinking>` block. Comments are reasoning residue; deleting
  them silently is a regression risk.
- **Never output 50+ lines of new code in one turn** without breaking
  into modules. `~/AGENTS.md` Rule 3 says "small changes" — this rule
  gives the numeric floor (≤50 lines per single response is small).
- **Never use black-box macros or heavy template metaprogramming**
  (no `eval()`, no deeply-magical decorators, no DSLs-on-top-of-DSLs).
  Prefer explicit code over implicit magic. If you can't read the
  generated output, don't ship it.

## When to suppress this skill

- Writing prose-only (no code blocks in the response) — the format
  adds no value
- Trivial single-line edits where `<thinking>` is overhead
- Tasks in non-engineering domains (data analysis, research synthesis)

In those cases, skip the formatting and answer normally.

---

## Related

- `~/AGENTS.md` Part 1 — Engineering Standards (rules 1–13). This
  skill layers the **format** + **negative constraints** on top
- `karpathy-engineer` archive backup: `~/.agents/.archive/audit-fix-2026-10-10/karpathy-engineer-SKILL.md.before-slim.bak`
