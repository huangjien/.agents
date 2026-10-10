---
kind: addition-note
date: 2026-10-10
session: VS Code Copilot custom agents created (Major + 9 specialists)
related: PAT-20261010-absorbslim-ordering
---

# 2026-10-10 — VS Code Copilot custom agents created (Major + 9 specialists)

Ten `.agent.md` files now live at `~/.copilot/agents/`, making the
agents-system entry-points selectable from VS Code Copilot Chat's
agent dropdown.

## What's in the dropdown

| Agent | Color | Tools | Source of full role |
|---|---|---|---|
| `major` | cyan | read, edit, execute, search, **agent** | orchestrator (entry-point) |
| `architect` | purple | read, edit, execute, search | `~/.agents/opencode/subagent/architect.md` |
| `coder` | green | read, edit, execute, search | `~/.agents/opencode/subagent/coder.md` |
| `debugger` | red | read, edit, execute, search | `~/.agents/opencode/subagent/debugger.md` |
| `reviewer` | blue | read, edit, execute, search | `~/.agents/opencode/subagent/reviewer.md` |
| `researcher` | indigo | read, edit, execute, search, **web** | `~/.agents/opencode/subagent/researcher.md` |
| `tester` | yellow | read, edit, execute, search | `~/.agents/opencode/subagent/tester.md` |
| `doc-writer` | teal | read, edit, execute, search | `~/.agents/opencode/subagent/doc-writer.md` |
| `laptop-admin` | orange | read, edit, execute, search | `~/.agents/agents/laptop-admin.md` |
| `software-maintainer` | magenta | read, edit, execute, search | `~/.agents/agents/software-maintainer.md` |

## Two dispatch paths from Copilot Chat

Now that all 10 files exist, the user has two working patterns:

**Path A — orchestrate via `major` (recommended for non-trivial work):**
1. Pick `major` from the agent dropdown
2. Type the request
3. Major classifies against AGENTS.md Part 3 and uses the `agent`
   tool to spawn the right specialist, passing the specialist's
   canonical role path as context

**Path B — pick the specialist directly** (when the user already
knows the role):
1. Pick `coder` / `debugger` / `architect` / etc. directly
2. Type the request
3. The specialist file references its full role definition at the
   canonical path; the agent reads it on first turn

Both paths land at the same specialist role definitions. Path A is
default for open-ended requests; Path B skips the routing layer
when the user's intent is already clear.

## Why thin stubs (46-58 lines each) instead of full role inlining

The existing gsd-* agent files inline full role content (~200 lines each).
For these agents we kept stubs that:
- Reference the canonical role path for the *actual* persona definition
- List the routing triggers inline so the agent file is self-describing
  in the Copilot dropdown
- Cross-reference AGENTS.md Parts 1, 2, 3 (so all 10 files consistently
  cite the universal standards doc)

This keeps the Copilot-facing files concise while making
`~/.agents/opencode/subagent/*.md` and `~/.agents/agents/*.md`
the single source of role truth. Edit the canonical file → the
agent in VS Code picks up the change next session.

## Activation

Reload VS Code (`⌘⇧P` → "Developer: Reload Window") for Copilot
to pick up the new agent files. They'll appear in the chat input
dropdown under the names listed above.

## Compatibility with prior work

- The `~/.agents/AGENTS.md` Part 4 Tool Integration table still reads
  correctly: Copilot is single-agent emulation, with Major as the
  in-chat pickable dispatcher
- `~/.agents/AGENTS.md` Part 5 file tree stays accurate — no
  changes needed there
- `~/.agents/bin/install.sh` does not need to be modified; the
  agents dir is user-local (under `~/.copilot/`), not part of
  the agents-system hub at `~/.agents/`

## Backups

None created (these are net-new files; nothing to back up). The
9 role definitions being referenced were already backed up to
the prior day's archive for the whole `~/.agents/` state.

## Related

- `~/.copilot/agents/major.agent.md` — entry-point orchestrator
- `~/.copilot/agents/gsd-*.agent.md` (33 files already there) —
  prior pattern this session's 10 files match
- `~/.agents/AGENTS.md` Part 3 — the routing table Major consults
- `~/.agents/opencode/subagent/` and `~/.agents/agents/` — the
  canonical role sources the 10 stubs reference
