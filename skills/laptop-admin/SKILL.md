---
name: laptop-admin
description: Manage this macOS laptop and the agents hub safely — software/services/env inventory, agent-tool configuration, hub role/skill wiring, disk cleanup. Inspect first, prefer reversible changes, confirm destructive actions. Use when the user says "laptop", "fix my machine", "configure", mentions permissions/env/defaults/system settings, or asks to change the ~/.agents setup itself.
metadata:
  author: local
  version: "1.0.0"
  last_reviewed: 2026-10-16
  source: ""
  local_only: true
---

# Laptop Admin

Manage the user's laptop, local developer tools, agent tools, and configuration.

## Operating rules

- Inspect the exact target before changing it.
- Explain the expected effect before making a system-level change.
- Prefer reversible actions: backups, symlinks, and dry runs.
- Use the smallest scope that solves the request.
- Verify the result with a command after each change.
- Report what changed, what was preserved, and any remaining limitation.

## Common tasks

- Inventory software, services, paths, environment variables, and disk usage.
- Configure agent tools through their native global adapter.
- Keep shared instructions under `~/.agents/` (single source of truth).
- Add a skill: create `~/.agents/skills/<name>/SKILL.md` (frontmatter `name:` must match the dir name), then register it in `route.yaml` if it should be a dispatch target.
- Add a spawn role: write `~/.agents/opencode/subagent/<name>.md` with dual-consumer YAML frontmatter, add the `~/.copilot/agents/<name>.agent.md` symlink, re-run `~/.agents/install.sh`.
- Run `~/.agents/bin/verify-global-agents` after changing the setup.

## Destructive operations

Before a destructive operation (delete, overwrite, uninstall, reset, broad migration), show:

1. Exact paths or resources affected.
2. The command or action.
3. A recovery or rollback method.

Then ask for confirmation. Do not infer confirmation from the original request unless the user explicitly named the destructive operation.

Never expose, copy, or commit secrets from shell history, keychains, `.env` files, or credential stores.
