---
name: laya-shortlist
description: Narrow a many-option choice to its top 1-3 candidates using the local laya decision engine. Use when stuck between 10+ skills, libraries, files, or approaches and need a calibrated short list — before scanning each one yourself.
metadata:
  author: local
  version: "1.0.0"
  source: ""
  local_only: true
---

# Laya Shortlist

Laya's `shortlist` tool collapses a long candidate list to its top-k. Fast
(~0.3 s warm), local, zero tokens. Use it when the choice space is too big to
read each option but you still want calibration on the final pick.

## When to use

- 10+ skill candidates (e.g. picking one skill from 50)
- 10+ library / package options to choose from
- 10+ files or paths to investigate — narrow to a few first
- Choosing between many possible user approaches or designs
- You can articulate a `state.field` describing the candidates in one sentence

## When NOT to use

- Fewer than 5 options — read them yourself, faster
- Options have clear criteria the user already specified
- The "choice" is binary (yes/no) — use a `noul` question via `laya-predict`
- Reasoning is required — laya decides, it does not think

## How (prefer MCP, fall back to HTTP)

```python
# MCP (preferred when available)
result = mcp__laya__laya_shortlist(
    state={"candidates": ["skill-1", "skill-2", "..."]},
    criteria="best fit for routing prompts to subagents",
    k=3,
)
# → { "topk": ["laya-triage", "code-review", "brainstorming"], "probs": [...] }
```

```sh
# HTTP fallback
curl -s http://127.0.0.1:8019/v1/systemone \
  -H 'Content-Type: application/json' \
  -d '{"state": {"candidates": [...]}, "questions": {
        "shortlist": {"type": "shortlist", "instructions": "...",
                      "state_field": "candidates", "k": 3}
      }}'
```

## Caveats

- Same laya instance is also used for routing. Do not feed it a state that
  mixes "skills to pick" with "prompts to route" — separate calls.
- `k` should stay small (1-5). Asking for top-30 returns near-uniform scores.
- If the top-k all cluster around probability 0.1 (flat distribution), laya
  is saying "no clear winner" — fall back to reading the candidates.
