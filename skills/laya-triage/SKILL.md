---
name: laya-triage
description: Classify prompts into the hub's route.yaml intents, gate smalltalk, or score severity using the local laya decision engine — no LLM call. Use when asked to triage a prompt, classify intent, pre-check routing, moderate content, or make a fast calibrated yes/no gate.
metadata:
  author: local
  version: "1.0.0"
  source: ""
  local_only: true
---

# Laya Triage (local decision engine)

Fast (~0.3 s warm, zero tokens, CPU) classification-shaped decisions from the
local laya daemon. Full decision shapes, thresholds, and limits live in
`~/.agents/mcp/laya-decisions.md` — read that first; this skill is the trigger.

## Quick path

```sh
~/.agents/bin/laya-classify "why is my build failing after the upgrade?"
# → "software_maintenance 0.71"   (appends LOW-CONFIDENCE when < 0.6, "smalltalk" when the gate fires)
```

## When to use

- Pre-checking which `route.yaml` intent a prompt belongs to (keyword matching
  mis-routes e.g. "why is X popular?" to debugging)
- Deciding whether a prompt is smalltalk / identity / meta (handle directly)
- Guardrail gates: urgent? spam? credentials present? (`noul`)
- Severity or difficulty scoring (`score`)

## Rules

- `answer_confidence >= 0.6` → trust the answer
- Below 0.6 → fall back to keyword matching or ask one clarifying question
- Never use laya for reasoning, code understanding, or generation — it decides,
  it does not think
- MCP session present? Prefer `laya_predict` / `laya_preset` over curl
- Daemon down? `curl -s localhost:8019/health`; everything degrades gracefully
  to normal routing
