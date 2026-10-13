---
applyTo: "**"
description: When the laya MCP server is connected, use its local decision tools for intent triage, routing pre-classification, and guardrail checks instead of spending an LLM call. Apply only when MCP tools laya_predict / laya_decide / laya_preset are exposed.
---

# Laya Decision Engine (laya-mcp-server)

Laya is a local, non-autoregressive decision engine (CPU, ~0.3 s warm, zero
output tokens) with calibrated probabilities. It answers structured questions
over text — it is not a chat model. Use it when the decision is
classification-shaped and does not need reasoning.

## When to use it

- **Intent triage / routing pre-check** — classify a prompt into a fixed
  set of intents before dispatch (e.g. the 9 in `~/.agents/route.yaml`).
  Keyword matching mis-routes prompts like "why is X popular?" to debugging.

Two ready-made commands wrap the daemon:

- `~/.agents/bin/laya-classify [--difficulty] "<prompt>"` — route intent +
  confidence (+ difficulty tier for model picking)
- `~/.agents/bin/laya-screen "<prompt>"` — privacy gate: credentials /
  personal data / internal paths, all checked locally before any cloud call
  Laya gets these right.
- **Binary gates** — "is this smalltalk?", "is this urgent?", "does this
  request contain credentials?" (`noul` questions).
- **Severity / difficulty scoring** — ordered levels in one pass (`score`).
- **Guardrails / moderation** — via `laya_preset` (`moderation`, `guard`).

Per AGENTS.md Part 1 rule 5: never spend an LLM call on a deterministic
local laya decision.

## Tool priority

1. `laya_preset` — built-in workflows: `triage`, `model_router`, `moderation`, `guard`, `email`
2. `laya_predict` — custom typed questions (`choice` / `score` / `noul`) in one forward pass
3. `laya_decide` — JSON-schema-shaped decision (structured output)
4. `laya_shortlist` — narrow a many-option choice to top-k before asking an LLM
5. `laya_status` / `laya_route` — diagnostics (device, checkpoint selection)

## Confidence handling

Answers include calibrated `answer_confidence` (probability of the chosen
option) and `confidence` (calibration-corrected). On low confidence:

- `answer_confidence < 0.5` → fall back to `route.yaml` keyword matching
- Smalltalk gate: `noul >= 0.8` → handle directly
- Both low or distribution flat → ask one clarifying question (matches the
  Major fallback rule in `route.yaml`)

These thresholds are eval-tuned (n=57): keywords alone 63%, laya alone 65%,
hybrid at T=0.5 70%. See `~/.agents/evals/routing/report.md`. Re-run the eval
after changing criteria or routes.

## When NOT to use it

- Anything requiring reasoning, code understanding, or multi-step logic — use an LLM
- Generation of any kind (it decides, it does not write)
- High-volume batch beyond ~64 questions per call (server caps) — chunk with `laya_predict_batch`

## HTTP fallback (no MCP session)

The same engine runs as a daemon: `curl -s localhost:8019/v1/systemone` with
`{"state": {"message": "..."}, "questions": {...}}`; health at `/health`.
Cold start on a new question shape can take ~7 s; warm calls are ~0.2–0.4 s.
