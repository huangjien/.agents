---
kind: session-note
date: 2026-10-10
session: Claude tool retirement + cross-tool docs standardization
related: PAT-20260919-skill-duplication-drift, wiki/notes/2026-10-10-instructions-consolidation.md
---

# 2026-10-10 — Claude retirement + tool-docs standardization

After the 2026-10-10 instructions consolidation removed `major-routing.instructions.md`
and slimmed Copilot docs, the same redundancy was still present across Claude,
Codex, and Gemini native docs: each carried its own copy of the Communication
& Output Style rules and codebase-memory-mcp instructions. Retiring Claude was
the trigger for a full cross-tool cleanup.

## What changed

| Action | Effect |
|---|---|
| **Deleted** `~/.claude/` (Claude Desktop app data + our agent-system symlinks) | Claude removed from the agent tool registry; backups preserved |
| **Absorbed** Communication & Output Style, Choose Best Representation, Explain Before You Elaborate, Human in the Loop into `~/.agents/AGENTS.md` Part 1 (new `## Output Style` section) | One canonical declaration; removes 3 duplicates in Codex + Gemini + Claude docs that didn't get cleaned in the previous round |
| **Extracted** codebase-memory-mcp instructions (duplicated and drifted between Codex and Gemini) into `~/.agents/mcp/codebase-memory.md` | Single source; both tool-native docs reference it now |
| **Slimmed** `~/.codex/AGENTS.md` (72 → 11 lines) and `~/.gemini/GEMINI.md` (31 → 11 lines) to thin pointers | Both docs now: "rules live in ~/AGENTS.md, mcp extras live in ~/.agents/mcp/codebase-memory.md" |
| **Slimmed** `~/.copilot/copilot-instructions.md` further (220 → 12 lines) | Communication & Style content removed since now in AGENTS.md |
| **Dropped** Claude rows from `install.sh`, `route.yaml` header, `README.md`, `adapters/README.md` | Re-run is clean (1 Major + 9 subagents + 2 portable roles in OpenCode; no Claude portable-role section) |

## Tool-native doc line counts after consolidation

| File | Before | After |
|---|---|---|
| `~/.copilot/copilot-instructions.md` | 220+ | 12 |
| `~/.codex/AGENTS.md` | 72 | 11 |
| `~/.gemini/GEMINI.md` | 31 | 11 |
| `~/.claude/CLAUDE.md` | (deleted) | 0 |

## New observation (refines the prior reusable rule)

The instructions-consolidation note from earlier today (2026-10-10) described
a 4-step cleanup rule: "find canonical → list duplicates → keep one +
slim others → verify". Applying it to Claude surfaced one ordering issue:
**absorb first, slim second.**

If you only slim per-tool docs without first absorbing tool-specific content
into the canonical hub, you lose content. Here's the corrected ordering:

1. **Identify content unique to the retired tool** — anything that doesn't
   exist in the canonical hub yet (Communication & Style, MCP tool
   priority, skill triggers, etc.).
2. **Absorb those pieces into the canonical hub** — promoted to a top-level
   section in `~/.agents/AGENTS.md` or to a new `~/.agents/<topic>/` doc.
3. **Slim the surviving per-tool docs** to thin pointers to the canonical
   hub plus tool-specific extras (if any).
4. **Drop all references** to the retired tool from `install.sh`,
   `route.yaml`, `README.md`, `adapters/README.md`.
5. **Verify**: re-run install, scan for stray references, check tool-native
   doc line counts.

When retiring a tool you don't use anymore, this order is what prevents
unintended content loss — every previously-tool-specific rule either gets
promoted to the canonical or stays in the now-defunct tool; nothing falls
through the cracks.

## Reusable principle to consider for promotion (future PAT candidate)

Two patterns matter here:

- **Tool retirement absorb-slim-ordering**: the 5-step rule above.
  Promote when a third retirement has used this rule without modification —
  probably not yet, this is only the second application
  (instructions consolidation was the first).
- **Cross-tool docs for the same rule must die in the same pass**: a partial
  cleanup leaves redundant copies that look correct but aren't.
  Same validation bar — needs more than two instances before promotion.

## Restore path

All originals backed up to `~/.agents/.archive/claude-removal-2026-10-10/`:
```
AGENTS.md.bak                  install.sh.bak               route.yaml.bak
README.md.bak                  adapters-README.md.bak
copilot-instructions.md.bak    codex-AGENTS.md.bak          gemini-GEMINI.md.bak
claude-CLAUDE.md.bak           (note: the rest of ~/.claude/ is gone, not backed up)
```

To bring Claude back as an agent tool: restore `claude-CLAUDE.md.bak` to
`~/.claude/CLAUDE.md`, restore the deleted install.sh section, and restore
the Claude rows in route.yaml/README.md/adapters/README.md. The Claude
app's own state (transcripts, costs) cannot be restored.

## Other work in same session (continuing from earlier today)

- Trae retirement fallout cleanup (earlier in same session)
- `write-a-skill` duplicate deletion (skill-creator fork with no unique value)
- Skill lock orphan cleanup (find-skills, grill-me removed)
- 37 untracked local skills registered in skill-lock.json with proper
  GitHub source attribution and folder hash

These earlier items remain scoped to their respective PATs/notes; this
note covers only the Claude retirement + cross-tool docs standardization
that happened after them.
