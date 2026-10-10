# Copilot Instructions — Setup Helper (stub)

> Source: `~/.agents/copilot/copilot-instructions.md`
>
> **This file is not a duplicate of `~/AGENTS.md`.** It is a setup helper:
> it tells you how to wire Copilot up against the canonical sources, and
> what to copy into a project only when self-contained rules are needed.

## What Copilot actually loads (in this machine)

In the order VS Code presents them:

| File | What it does |
|---|---|
| `~/.copilot/copilot-instructions.md` | Communication & output style (ASD-STE100-lite), "choose best representation", "human in the loop" |
| `~/AGENTS.md` (→ `~/.agents/AGENTS.md`) | Universal engineering standards, safety rules, Major orchestrator |
| `~/.copilot/instructions/gsd-protocol.instructions.md` | 万能开发协议 (Chinese) + GSD integration block — applies only when the user invokes GSD |
| `~/.copilot/instructions/i-have-adhd.instructions.md` | ADHD-shaped output — opt-out with "stop adhd mode" |

If you don't touch anything, you already have all four running. That's the
right default for any project you work on locally.

## When you need per-project Copilot instructions

Only when shipping a project to people who don't have `~/.agents/`
installed. In that case, `cp` the four files above into
`<project>/.github/instructions/` (one `.instructions.md` per file)
so the project carries its own copy.

Don't paste this stub into a project — point collaborators at
`~/AGENTS.md`-style rules by referencing the canonical sources by URL.

## Setup notes (forcing Copilot to load the globals explicitly)

If you've disabled auto-discovery in VS Code settings, force it back via:

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    { "file": "~/.copilot/copilot-instructions.md" }
  ],
  "chat.instructionsFilesLocations": {
    "~/.copilot/instructions/*.md": true
  }
}
```

Or symlink this repo's canonical files into the locations Copilot scans:

```bash
ln -sf ~/.agents/AGENTS.md ~/AGENTS.md
ln -sf ~/.copilot/copilot-instructions.md ~/.copilot/instructions/global.instructions.md
ln -sf ~/.agents/skills ~/.copilot/instructions/skills   # optional
```
