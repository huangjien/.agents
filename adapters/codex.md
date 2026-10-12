# Codex Global Adapter

Use the shared agent system at `~/.agents/` as the canonical source.

- Apply `~/.agents/AGENTS.md` as the universal engineering contract.
- Use `~/.agents/route.yaml` for Major routing when the task is complex.
- Treat `~/.agents/agents/*.md` as reusable role definitions.
- Prefer project-local `AGENTS.md` instructions when they are more specific.
- Do not assume that a role file can spawn a subagent unless the current Codex client exposes that capability.

The installer preserves the existing `~/.codex/AGENTS.md`. It contains Codex-specific project tooling instructions.
