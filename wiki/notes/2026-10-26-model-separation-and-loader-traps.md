---
kind: addition-note
date: 2026-10-26
session: model separation for review/QA agents across pi, OpenCode, Copilot
related: AGENTS.md "Model separation" section, bin/_check_model_separation
---

# 2026-10-26 — Review on a different model than the author; three loader traps

Goal: reviewer runs on a different model family than the authoring
session, on every surface (pi, OpenCode, Copilot). Motivation: several
reviewers on the author's own model share that model's blind spots, so
their agreement is not verification.

## What landed

| Surface | Author model | Reviewer model | Where pinned |
|---|---|---|---|
| pi | session model (zai-coding-cn/glm-5.3) | openai/gpt-5.4 | `~/.pi/agent/settings.json` `subagents.agentOverrides` + `agentOverridesByProvider` (swap when parent is OpenAI) |
| OpenCode | zhipu/glm-5.3 (default) | openai/gpt-5.4 | `opencode/subagent/reviewer.md` frontmatter |
| Copilot | session default | mai-code-1.1-flash → gpt-6-luna | `copilot/agents/reviewer.agent.md` model array |

Verified with real launches both ways: parent glm-5.3 → reviewer child
ran openai/gpt-5.4:high; parent openai/gpt-5.4 → reviewer child ran
zai-coding-cn/glm-5.3:high (child meta files record parent and child).

Same-day bump: reviewer/evidence-auditor pin moved from gpt-5.4 to
`openai/gpt-6-astra` (current flagship per OpenAI docs; 6.1-sol is the
1/5-price near-flagship alternative). Re-verified: parent glm-5.3 →
child ran openai/gpt-6-astra:high. OpenCode note: an agent file with an
unknown model id fails to load ENTIRELY — a stale pin deletes the role,
it does not fall back.

Same-day final: user chose the cheaper tier — pin is
`openai/gpt-6.1-sol` (near-Astra intelligence, 1/5 the token price,
$0.10/1M cached input).

`bin/_check_model_separation` (in `bin/test-hub`) enforces the rule;
negative-tested for pi and Copilot.

## Pattern 1 — OpenCode never scanned `~/.config/opencode/subagent/`

`install.sh` linked spawn roles into `subagent/`; `opencode debug
agents` never listed them. Probes (with the background service
stopped — it caches) show OpenCode scans `agent/` and `agents/` only.
Roles were silently invisible to the `task()` tool for weeks.

Fix: `install.sh` now links into `agents/` and removes `subagent/`.

## Pattern 2 — one role file cannot serve OpenCode and Copilot

Probed frontmatter shapes, one variable at a time:

| Key shape | OpenCode | Copilot |
|---|---|---|
| `tools: [...]` array | FAILS to load | loads |
| `tools:` object | loads | FAILS to load |
| `color: blue` | FAILS to load | loads |
| `color: success`/`info` | loads | loads |
| `model: inherit` | loads (null) | warn: not available |
| `model: provider/id` | loads, resolves | warn: not available |
| `model: [names]` | — | loads |

The old shared files (`tools: ['read','edit','execute','search']` +
`color: blue`) failed to load in OpenCode on two keys at once, which
hid pattern 1. Fix: per-dialect files — `opencode/subagent/*.md`
(OpenCode) and `copilot/agents/*.agent.md` (Copilot). Documented in
AGENTS.md "Editing the system".

## Pattern 3 — pi-subagents scans `~/.agents` recursively and shadows builtins

pi-subagents treats `~/.agents` as a user agent dir. The hub's
OpenCode-dialect `reviewer.md` shadowed pi's builtin `reviewer`, whose
tools exist in pi — the launch died with "requested unavailable child
tools: ['read','edit','execute','search']".

Fix: `agentExcludeDirs: ["~/.agents/opencode", "~/.agents/copilot"]`
in `~/.pi/agent/settings.json`. Any future hub dir with agent-ish .md
files needs the same exclusion.

## Copilot model-name gotcha

Copilot accepts neither `provider/id` nor upstream model names
(gpt-5.4, gpt-6-luna, claude-*) in agent `model:` on this account —
every probe warned "not available; using auto". Only its own catalog
ids work (here: `mai-code-1.1-flash`, from session-store history).
Unknowable offline: read `modelId` values from `~/.copilot/session-state/`,
or open `/model` in an interactive CLI run.
