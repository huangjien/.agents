# Major Agent System

A cross-tool agent routing system with one entry point: **Major**. Major
classifies user intent. It then dispatches to **seven domain specialists**
via routing rules in [`route.yaml`](./route.yaml).

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
| `AGENTS.md` | Cross-tool entry doc (read by all tools) |
| `route.yaml` | Routing rules — the single source of truth for who-does-what |
| `opencode/agent/major.md` | Major agent definition (OpenCode) |
| `opencode/subagent/*.md` | 2 spawn roles: reviewer (fresh-context verification), researcher (fan-out search) |
| `copilot/agents/*.agent.md` | Same 2 roles, Copilot frontmatter dialect |
| `copilot/copilot-instructions.md` | Copilot instructions template |
| `skills/` | ~70 skills — the dispatch layer route.yaml points at |
| `adapters/*.md` | Client integration notes |
| `bin/verify-global-agents` | Integration health check |
| `bin/test-hub` | Static harness: route schema, frontmatter, model separation, prose style |
| `.github/workflows/hub-ci.yml` | CI: test-hub + workflow scripts + shellcheck + routing eval + model-separation fixtures + fresh-HOME install |
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
         ▼ skills-first: load the matched skill in-context
   ┌───────────────────────────────────────────┐
   │ 9 route intents → skills/diagnose, tdd,   │
   │ code-review, system-design, doc-templates,│
   │ karpathy-engineer, research-methods, ...  │
   └───────────────────────────────────────────┘
         │ (only under spawn conditions)
         ▼ spawn for context isolation
   researcher (fan-out search)   reviewer (fresh verification,
                                  different model family than author)
```

Major never writes code, debugs, or reviews itself. It classifies and
dispatches. Simple things (greetings, identity questions, one-line
factoids) it handles directly.

## Editing the system

### Add a new spawn role (OpenCode / Copilot)

OpenCode and Copilot parse agent frontmatter differently, so each role
has two files. OpenCode wants `tools` as an object, a `permission`
block, and `model` as `provider/model-id`. Copilot wants `tools` as an
array and `model` as an array of model names.

1. Write `~/.agents/opencode/subagent/{name}.md` (OpenCode dialect).
2. Write `~/.agents/copilot/agents/{name}.agent.md` (Copilot dialect).
3. Register it in `route.yaml` under `spawn_roles:`.
4. Add a route entry under `routes:` with triggers.
5. Re-run `~/.agents/install.sh`. It links the OpenCode role into
   `~/.config/opencode/agents/` (the dir OpenCode actually scans).
   It links the Copilot role into `~/.copilot/agents/`.

Verification roles (`reviewer`) must run on a different model family
than authoring. `bin/_check_model_separation` (wired into
`bin/test-hub`) enforces this across pi, OpenCode, and Copilot.

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
│       ├── reviewer.md             spawn role: fresh-context verification
│       └── researcher.md           spawn role: fan-out search isolation
└── copilot/
    ├── copilot-instructions.md     Copilot instructions template
    ├── major.agent.md              Major template (Copilot)
    └── agents/                     Copilot-dialect spawn roles
        ├── reviewer.agent.md
        └── researcher.agent.md
```

After install, these symlinks exist:

```
~/.config/opencode/agent/major.md           → ~/.agents/opencode/agent/major.md
~/.config/opencode/agents/reviewer.md       → ~/.agents/opencode/subagent/reviewer.md
~/.config/opencode/agents/researcher.md     → ~/.agents/opencode/subagent/researcher.md
~/.copilot/agents/reviewer.agent.md         → ~/.agents/copilot/agents/reviewer.agent.md   (Copilot dialect — separate file)
~/.copilot/agents/researcher.agent.md       → ~/.agents/copilot/agents/researcher.agent.md
~/.copilot/agents/major.agent.md            (Major is Copilot-only — real file, no L1 equivalent)
~/AGENTS.md                                 → ~/.agents/AGENTS.md
```

## Skills

`~/.agents/skills/` is the single source of truth for agent skills. Each
skill gets one directory with a `SKILL.md`. Its frontmatter `name` must
match the directory name.

VS Code + GitHub Copilot discovers these natively (user-level skill
location, Agent Skills support). Copilot also reads `~/.copilot/skills/`.

To add a skill: create `~/.agents/skills/<name>/SKILL.md`. The frontmatter
`name: <name>` must match the directory.

To add a portable role: create `~/.agents/agents/<name>.md`, run
`~/.agents/install.sh`, then run `~/.agents/bin/verify-global-agents`.

Laptop administration roles must inspect first, prefer reversible changes, and
ask for confirmation before destructive operations.

### Skill evolution wiki

`~/.agents/wiki/` accumulates failure/success patterns. It compiles them
into audited skill edits (adapted from WikiSkill, arXiv 2608.27454).
The `skill-wiki` skill drives it. **Record** patterns after notable
sessions. **Compile** them one atomic edit at a time. Validate, then
revert via the diffs in `wiki/skill-impact.md` if needed. The wiki never
enters always-on context. See `wiki/README.md`.

Global rules live as VS Code instruction files in
`~/.copilot/instructions/`. Enable them via the
`chat.instructionsFilesLocations` setting:

- `gsd-protocol.instructions.md` — 万能开发协议

Copilot loads Major orchestrator routing via `~/AGENTS.md` (auto-discovered),
not via this directory.

## Uninstall

```bash
# Remove symlinks (source files in ~/.agents/ are untouched)
rm ~/.config/opencode/agent/major.md
rm ~/.config/opencode/agents/{reviewer,researcher}.md
rm ~/.copilot/agents/{reviewer,researcher}.agent.md
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
