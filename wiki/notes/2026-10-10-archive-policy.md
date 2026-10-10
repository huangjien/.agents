---
kind: policy-note
date: 2026-10-10
session: archive retention rules for ~/.agents/.archive/
---

# 2026-10-10 — archive retention policy

`~/.agents/.archive/` holds per-session backups of files modified
during cleanup / consolidation / retirement work. As of 2026-10-10
the directory holds 164 KB across 3 dated subdirs:

| Subdir | Size | Contents |
|---|---|---|
| `instructions-pre-consolidation-2026-10-10/` | 24 KB | Pre-consolidation originals of `copilot-instructions.md.bak`, `gsd-protocol.instructions.md.bak`, `major-routing.instructions.md.bak`, `copilot-template.md.bak` |
| `claude-removal-2026-10-10/` | 64 KB | Pre-retirement versions of `AGENTS.md`, `install.sh`, `route.yaml`, `README.md`, `adapters/README.md`, `~/.codex/AGENTS.md`, `~/.gemini/GEMINI.md`, `~/.copilot/copilot-instructions.md`, `~/.claude/CLAUDE.md` |
| `audit-fix-2026-10-10/` | 76 KB | Pre-fix versions of `AGENTS.md`, `verify-global-agents`, `gsd-protocol.instructions.md`, `deploy-to-vercel/SKILL.md`, `run_eval.py`, `react-native-skills/SKILL.md`, `react-view-transitions/SKILL.md`, `ui-ux-pro-max.bak` |

## Why backups exist

Per Rule 12 (Checkpoint Long Workflows): "An interruption should cost
minutes, not hours." Backups let us revert a session's changes if
something downstream breaks after we've moved on. They are NOT
long-term canonical record — wiki notes document *what* was done;
archives document *the pre-state* in case any verdict needs
re-checking.

## When to prune

A backup is eligible for removal **30 days after the session that
created it** unless any of these triggers fires:

- A wiki entry created during that session has been edited since
  (signals active iteration → keep the backup until the wiki
  stabilizes)
- A new audit or verifier run flagged a regression tied to that
  session's changes (signals the session's verdict may be wrong)
- The user explicitly asks to keep the backup longer

For 2026-10-10 archives, the **first eligible prune date is
2026-11-09** (30 days from the session date). The audit-fix
note, instructions-consolidation note, claude-removal note, and
P6-decision note are all currently stable (no edits since creation);
they qualify for the standard 30-day window.

## Trigger check before pruning

```bash
# For each archive subdir under ~/.agents/.archive/:
for d in ~/.agents/.archive/*/; do
  if [ -d "$d" ]; then
    name=$(basename "$d")
    echo "=== $name ==="
    echo "  Files: $(ls $d | wc -l | tr -d ' ')"
    echo "  Size:  $(du -sh $d | cut -f1)"
    # Wiki entries that reference this archive (should NOT be modified
    # since creation):
    grep -l "$(basename $name)" ~/.agents/wiki/notes/ ~/.agents/wiki/index.md 2>/dev/null \
      | xargs -I {} stat -f "%Sm %N" {} 2>/dev/null \
      | sort -r | head -3
  fi
done
```

If the most recent wiki edit touching the archive is >30 days ago,
prune. Otherwise keep.

## What NOT to do

- Don't `rm -rf ~/.agents/.archive/*` en masse — that's still in
  the rollback window for today's session; a regression tomorrow
  would lose the safety net.
- Don't keep archives forever ("disks are cheap"). The whole point
  of a backup is finite-validity + trigger-defined retention.

## Related

- `wiki/notes/2026-10-10-instructions-consolidation.md` — first
  archive made, the policy this note documents
- `wiki/notes/2026-10-10-claude-removal.md` — second archive
- `wiki/notes/2026-10-10-audit-fixes.md` — third archive
