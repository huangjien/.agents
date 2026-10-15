---
name: laya-screen
description: Run a local privacy screen on content before sending it to a cloud LLM. Use when handling user-supplied prompts, file paths, or command output that may contain credentials, PII, or internal system info.
metadata:
  author: local
  version: "1.0.0"
  source: ""
  local_only: true
---

# Laya Screen

`bin/laya-screen` is a local-only privacy gate. Checks a string for
credentials, personal data, and internal system paths via the laya daemon —
nothing leaves the laptop.

## When to use

- Echoing user input back into a tool call (logs, telemetry, traces)
- Storing user-supplied content (file paths, env values, command output)
- Forwarding error messages or stack traces to a remote LLM
- Anything about to be `cat`'d, `curl`'d, or written to a remote API

## When NOT to use

- Pure code you wrote yourself (no user data mixed in)
- Public docs or README content
- You are about to run a local command (laya doesn't need to screen those)
- The string is empty

## How (use the bin; it's faster than the HTTP API for this)

```sh
echo "$USER_INPUT" | ~/.agents/bin/laya-screen
# CLEAN
# or
# RISK CREDENTIALS (p=0.95)
# RISK PERSONAL-DATA (p=0.72)
# RISK
```

Exit code is always 0 on success (the gate is informational, not blocking).
Exit 1 = daemon unreachable. Exit 2 = usage error.

## Response protocol

| Output | Action |
|---|---|
| `CLEAN` | Send as-is |
| `RISK CREDENTIALS` | Redact secrets, then send. Or ask the user. |
| `RISK PERSONAL-DATA` | Strip or hash PII, then send. |
| `RISK INTERNAL-PATHS` | Replace with relative paths, then send. |
| `RISK` (multiple) | Refuse to send; show the user the trigger. |
| Daemon unreachable | Fall back to manual review. Do not send blind. |

## Caveats

- Laya's confidence is calibrated, not perfect. `p=0.4` for credentials
  still warrants a look. Treat anything `>= 0.5` as actionable.
- The screen reads the raw text. Encoded / encrypted content is not
  decoded — screen the unencoded form.
- Running it on a Codex session is automatic via the `UserPromptSubmit` hook
  in `~/.codex/config.toml`. For other clients, invoke it yourself.
