---
id: PAT-20261010-absorbslim-ordering
status: candidate        # candidate | promoted | rejected | superseded
models: []
domain: tooling
created: 2026-10-10
last-touched: 2026-10-10
---

# Tool-retirement migrations need an absorb-then-slim order, not slim-then-absorb

## Symptom

After retiring a tool, the per-tool native docs and the canonical
hub drift in two directions at once: the canonical hub stays
unchanged (so the new slim tool docs point at content that doesn't
exist yet), and the per-tool docs become thin wrappers around content
that LOST its only home. Net result: content vanishes, and a
follow-up audit finds the rules are thinner than they should be.

## Root cause

When retiring a tool we don't use anymore, the temptation is to start
by slimming the per-tool docs (the "low-hanging fruit" since they're
redundant). But the canonical hub doesn't have the content yet. The
reordering that avoids loss is:

1. **Identify** content unique to the retired tool — anything that
   doesn't already exist in the canonical hub (`~/.agents/AGENTS.md`
   or a shared doc under `~/.agents/<topic>/`).
2. **Absorb** those pieces into the canonical hub — promote a section
   into `AGENTS.md` (universal standards warrant this) or extract to a
   `~/.agents/<topic>/<doc>.md` (tool-agnostic but not universal
   standard).
3. **Slim** the surviving per-tool docs to thin pointers to the
   canonical hub plus tool-specific extras.
4. **Drop** all references to the retired tool from install scripts,
   routing config, README tables, and adapters README.
5. **Verify**: re-run the installer, grep for stray references, sanity-
   check the per-tool doc line counts dropped.

If you only do steps 3-4, you lose content. If you only do steps 1-2,
the per-tool docs still drift. The order matters.

## Rule / workaround

When retiring a tool, **absorb first, slim second**. Never slim per-tool
docs without first identifying where the retired tool's content will
live post-retirement.

A short verification checklist before closing out a tool retirement:

- [ ] No per-tool doc still has a content section that has no home in
      the canonical hub
- [ ] All `~/.trae/`, `~/.claude/`, or similar retired paths have been
      either replaced with `~/.agents/...` paths or removed entirely
      (excluding wiki notes and archive backups, which are
      intentional historical record)
- [ ] `install.sh` has no orphan section for the retired tool
- [ ] Every per-tool native doc is a thin pointer (typical: <20 lines)

## Evidence

Two verified full-cycle applications:

1. **2026-10-10 — Trae → Copilot instructions consolidation** (PARTIAL):
   identified duplication (steps 1-2), absorbed engineering rules into
   `AGENTS.md` (step 2 partial), slimmed `copilot-instructions.md`
   (step 3 partial), dropped Trae refs from `install.sh` etc (step 4),
   verified (step 5). **Incomplete because Claude/Codex/Gemini
   docs were not slimmed in the same pass** — they were left
   carrying the same redundant content. The Claude retirement (next
   instance) caught these.

2. **2026-10-10 — Claude retirement**: identified (Communication/Style
   content, codebase-memory-mcp instructions), absorbed into
   `AGENTS.md` Part 1 + new `~/.agents/mcp/codebase-memory.md`,
   slimmed all 4 remaining tool docs to thin pointers, dropped
   Claude from every config file, verified. **Complete 5-step
   application.**

   Plus: The instructions-consolidation was re-applied as a
   follow-up when audit-fixes showed Claude/Codex/Gemini still had
   redundant content.

## Promotion bar

Mark this PAT as `promoted` when the pattern is verified in **3
separate full-cycle applications**, not counting partial ones. We
have 1.5 verified (the instructions-consolidation only covered
Copilot; the Claude retirement covered all 4 tools + 1 wiki + 7
config files). Promote at the next tool retirement that's a clean
full cycle.

## Related

Skills: — · Patterns: — · Notes:
  - wiki/notes/2026-10-10-instructions-consolidation.md
  - wiki/notes/2026-10-10-claude-removal.md
  - wiki/notes/2026-10-10-audit-fixes.md
