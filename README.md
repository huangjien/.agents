# Major Agent System

A cross-tool agent routing system with one entry point (**Major**) that
classifies user intent and dispatches to **seven domain specialists** via
routing rules in [`route.yaml`](./route.yaml).

`~/.agents/` is the canonical hub. Client-specific directories are adapters,
not separate sources of truth. Clients without native subagent support use the
shared rules and role definitions through their own instruction mechanism.

Works across **OpenCode** (native multi-agent), **Codex**, **pi**,
**VSCode + GitHub Copilot**, and **Gemini**. Clients without native
multi-agent support use instruction-based
role switching.

## Quick start

```bash
# 1. Install symlinks across all 3 tools
~/.agents/install.sh

# 2. (OpenCode) Switch to Major as your default agent
#    /agents → select "major"

# 3. (Optional) Set up VSCode Copilot settings globally:
#    See ~/.agents/copilot/copilot-instructions.md → "Setup notes"
```

## What you get

| Component | Purpose |
|-----------|---------|
| `AGENTS.md` | Cross-tool entry doc (read by all 3 tools) |
| `route.yaml` | Routing rules — the single source of truth for who-does-what |
| `opencode/agent/major.md` | Major agent definition (OpenCode; frontmatter merged so also Copilot-readable) |
| `opencode/subagent/*.md` | 7 standard specialists: architect, coder, debugger, reviewer, researcher, tester, doc-writer |
| `agents/laptop-admin.md`, `agents/software-maintainer.md` | 2 portable role definitions; same dual-consumer format as the standard roles |
| `copilot/copilot-instructions.md` | Copilot instructions template |
| `adapters/*.md` | Client integration notes |
| `bin/verify-global-agents` | Integration health check |
| `install.sh` | One-shot installer (idempotent) |

## How routing works

```
user message
     │
     ▼
┌─────────────────┐
│      MAJOR      │  ← reads route.yaml, classifies intent
└────────┬────────┘
         │
   ┌─────┴─────┬──────┬──────┬──────┬──────┬──────┐
   ▼           ▼      ▼      ▼      ▼      ▼      ▼
architect   coder  debugger reviewer researcher tester  doc-writer
```

Major never writes code, debugs, or reviews itself. It classifies and
dispatches. Simple things (greetings, identity questions, one-line
factoids) it handles directly.

## Editing the system

### Add a new subagent (OpenCode) / specialist (Copilot)

Each role file is a single source of truth for both OpenCode and VS
Code Copilot. The YAML frontmatter is dual-consumer: OpenCode reads
`name` / `description` / `model` / `mode`; Copilot reads `name` /
`description` / `tools` / `color`.

1. Write `~/.agents/opencode/subagent/{name}.md` (or
   `~/.agents/agents/{name}.md` for portable roles). Copy an existing
   role file as a template.
2. Register it in `route.yaml` under `subagents:`.
3. Add a route entry under `routes:` with triggers.
4. Re-run `~/.agents/install.sh` — it re-creates the OpenCode
   symlink (`~/.config/opencode/subagent/<name>.md`) and the Copilot
   discovery symlink (`~/.copilot/agents/<name>.agent.md → ~/.agents/...`).

### Change routing

Edit `route.yaml`. No code changes required. Re-run install (it just
refreshes symlinks — the YAML is read live by Major).

### Tune Major's behavior

Edit `~/.agents/opencode/agent/major.md`.

### Tune cross-tool behavior

Edit `~/.agents/AGENTS.md` (read by all tools) or
`~/.agents/copilot/copilot-instructions.md` (tool-specific).

## Tool-specific behavior

| Tool | Mechanism | Behavior |
|------|-----------|----------|
| OpenCode | Native multi-agent | Major invokes real subagent processes via `task()` |
| Codex | Reads `~/.codex/AGENTS.md` | Shared hub reference plus Codex-specific rules |
| pi | Reads `~/AGENTS.md` | Single-agent role switching |
| Gemini | Reads `~/.gemini/GEMINI.md` | Shared hub reference plus Gemini-specific rules |
| VSCode + Copilot | Reads `~/AGENTS.md` | Single-agent role switching |

OpenCode is the only tool with real multi-agent infrastructure. The
others emulate by switching behavior based on the routing rules.

## Files at a glance

```
~/.agents/
├── AGENTS.md                       Cross-tool entry doc
├── route.yaml                      Routing rules
├── README.md                       This file
├── install.sh                      Installer script
├── agents/                          Portable roles
├── adapters/                        Client integration notes
├── bin/                             Verification and maintenance commands
├── opencode/
│   ├── agent/
│   │   └── major.md                Major agent (OpenCode)
│   └── subagent/
│       ├── architect.md
│       ├── coder.md
│       ├── debugger.md
│       ├── reviewer.md
│       ├── researcher.md
│       ├── tester.md
│       └── doc-writer.md
└── copilot/
    └── copilot-instructions.md     Copilot instructions template
```

After install, these symlinks exist:

```
~/.config/opencode/agent/major.md           → ~/.agents/opencode/agent/major.md
~/.config/opencode/subagent/architect.md    → ~/.agents/opencode/subagent/architect.md
... (one per subagent)
~/.copilot/agents/<name>.agent.md           → ~/.agents/opencode/subagent/<name>.md    (VS Code Copilot dropdown pickup — same role file, dual-consumer)
~/.copilot/agents/major.agent.md            (Major is Copilot-only — real file, no L1 equivalent)
~/AGENTS.md                                 → ~/.agents/AGENTS.md
```

## Skills

`~/.agents/skills/` is the single source of truth for agent skills (one
directory per skill, with a `SKILL.md` whose frontmatter `name` must match
the directory name).

Discovered natively by **VS Code + GitHub Copilot** (user-level skill
location, Agent Skills support). Copilot also reads `~/.copilot/skills/`.

To add a skill: create `~/.agents/skills/<name>/SKILL.md` (frontmatter
`name: <name>` matching the directory).

To add a portable role: create `~/.agents/agents/<name>.md`, run
`~/.agents/install.sh`, then run `~/.agents/bin/verify-global-agents`.

Laptop administration roles must inspect first, prefer reversible changes, and
ask for confirmation before destructive operations.

### Skill evolution wiki

`~/.agents/wiki/` accumulates failure/success patterns and compiles them
into audited skill edits (adapted from WikiSkill, arXiv 2608.27454).
The `skill-wiki` skill drives it: **record** patterns after notable
sessions, **compile** them one atomic edit at a time, validate, and
revert via the diffs in `wiki/skill-impact.md`. The wiki never enters
always-on context. See `wiki/README.md`.

Global rules live as VS Code instruction files in
`~/.copilot/instructions/` (enabled via the
`chat.instructionsFilesLocations` setting):

- `gsd-protocol.instructions.md` — 万能开发协议

Major orchestrator routing is loaded via `~/AGENTS.md` (which Copilot
also auto-discovers), not via this directory.

## Uninstall

```bash
# Remove symlinks (source files in ~/.agents/ are untouched)
rm ~/.config/opencode/agent/major.md
rm ~/.config/opencode/subagent/{architect,coder,debugger,reviewer,researcher,tester,doc-writer}.md
rm ~/AGENTS.md

# Optionally remove the source entirely
rm -rf ~/.agents/
```

## Design principles

1. **One source of truth** — everything in `~/.agents/`, tools read via
   symlink.
2. **Classify, don't guess** — Major never acts on complex requests
   without classifying first.
3. **Delegate, don't hoard** — anything matching a subagent's domain is
   delegated.
4. **Cost-aware** — tier hints in `route.yaml` guide model choice.
5. **No silent delegation** — always announce before invoking.
6. **Idempotent install** — re-running `install.sh` is always safe.
