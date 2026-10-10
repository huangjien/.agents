---
kind: decision-note
date: 2026-10-10
session: P6 GSD plugin closure decision
related: wiki/notes/2026-10-10-audit-fixes.md
---

# 2026-10-10 — P6 closure: KEEP get-shit-done with documented staleness

The audit flagged P6 as HIGH (4 hits in `~/.config/opencode/get-shit-done/bin/lib/profile-pipeline.cjs` at L20, L162, L254, L394 falling back to `~/.claude/projects`). Two closure paths were offered:

A. **File upstream** at the get-shit-done repo so they fix the Claude fallback
B. **Remove the plugin** from OpenCode config entirely

We chose **neither today** — the plugin stays installed with the known-limitation
in `wiki/notes/2026-10-10-audit-fixes.md` already recording the file path, line
numbers, and what's needed to clean up. Why:

## Why we kept the plugin

`get-shit-done` is 1.3 MB on disk under `~/.config/opencode/get-shit-done/`
installed Mar 2026. It's the substrate the copilot-instructions.md
"gsd-protocol" reference points at; the wiki entries (2026-10-10
instructions-consolidation, this session's audit-fixes note) document
the GSD integration block as a loadable Copilot instructions file.
Removing the plugin would:

- **Kill the future GSD adoption path**: if the user later wants to use
  GSD via any tool that loads `.instructions.md` files, the plugin is
  the substrate that the workflow files run on. Without it, future GSD
  re-installation requires a fresh tool-specific setup.
- **Break the GSD integration doc**: `~/.copilot/instructions/gsd-protocol.instructions.md`
  contains the integration block that says "use `gsd-*` commands → load
  matching file from `.github/skills/gsd-*`". The plugin provides those
  underlying skills.

So removal is not a clean cut — it has hidden dependency on the
documented GSD integration.

## Why we didn't file upstream today

Filing upstream for the get-shit-done maintainer to fix the
`~/.claude/projects` fallback requires:

1. Locating the upstream repo (not in our agents codebase)
2. Confirming the maintainer is still active
3. Writing the issue/PR

Each of those is small but not zero, and they all require an explicit
"what's the upstream repo" lookup that the audit didn't surface.
Deferrable until we either (a) actually adopt GSD ourselves, or
(b) start seeing real breakage from the Claude fallback.

## What's actually broken now

Looking at the audit evidence: the 4 `~/.claude/projects` fallback
sites are in `profile-pipeline.cjs`. Three of them are default
arguments to a function — they only fire if no override is supplied:

```js
const searchedPath = overridePath || '~/.claude/projects';
```

If we never call this function without `overridePath`, those lines are
dead. If we do call it without one and Claude is gone, we'd get a
search miss (not a crash). Either way: low-impact on us today.

## Closure plan when we revisit

If/when:

1. We adopt GSD — file the upstream issue with our fork/repro. The
   fix is presumably 1 line per site (drop the Claude fallback or
   replace with OpenCode equivalent).
2. We retire GSD entirely — `rm -rf ~/.config/opencode/get-shit-done`
   + remove the gsd-protocol.instructions.md integration block + drop
   the wiki references.
3. Six months pass with no GSD usage — option 2.

For now: keep plugin, document staleness here, link from
audit-fixes note so the next cleanup pass sees the trail.
