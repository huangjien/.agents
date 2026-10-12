# Global Agent Adapters

`~/.agents/` is the source of truth for shared agent behavior.

No single native agent format fits every client. Instead, the installer
connects the hub to each client. It does this only where the client
supports a compatible global convention.

## Shared layers

- `AGENTS.md`: universal engineering and safety rules.
- `route.yaml`: Major routing policy.
- `agents/`: portable role definitions.
- `skills/`: reusable workflows.
- `opencode/`: OpenCode-specific Major and subagents.
- `bin/`: local verification and maintenance commands.

## Adapter policy

- OpenCode receives native agent symlinks.
- Codex, pi, Gemini, and Copilot receive instruction adapters or their native global files when available.
- The installer preserves existing tool-specific files. It reports conflicts instead of silently replacing them.

## Add a role

1. Add `~/.agents/agents/<name>.md` with YAML frontmatter and a focused role description.
2. Run `~/.agents/install.sh`.
3. Run `~/.agents/bin/verify-global-agents`.
4. Test the role in each client that supports native subagents.
