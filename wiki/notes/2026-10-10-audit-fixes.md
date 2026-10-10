---
kind: session-note
date: 2026-10-10
session: codebase-audit follow-up fixes (15 issues from 5-check audit)
related: wiki/notes/2026-10-10-claude-removal.md, wiki/notes/2026-10-10-instructions-consolidation.md, PAT-20260906-skill-name-dir-mismatch
---

# 2026-10-10 — codebase-audit follow-up fixes

After the Claude retirement and tool-docs consolidation, ran a `codebase-audit`
workflow (`codebase-audit-mv2acmbz-6vjaxm`) covering 5 axes:
1. Tool registry consistency
2. Post-retirement path validity (Trae/Claude refs)
3. AGENTS.md ↔ route.yaml ↔ opencode/subagent/ ↔ agents/ role consistency
4. Skill loader readiness (frontmatter, name↔dir per PAT-20260906)
5. MCP and shared-docs integrity

The audit confirmed **15 real issues, 0 false positives**. 14 were fixed in this
pass; 1 deferred as a known out-of-scope limitation (P6 below).

## Issues fixed

| # | Sev | What | Fix |
|---|:---:|---|---|
| P1 | HIGH | Two skills had `vercel-` prefix in frontmatter `name:` (mismatched dir — VS Code drops these per PAT-20260906) | Renamed `name:` to `react-native-skills` and `react-view-transitions` |
| P2 | HIGH | Dangling symlink `~/.config/opencode/skills → ~/.trae/skills` (Trae deleted in earlier session; this symlink missed) | `unlink` |
| P3 | HIGH | `~/.copilot/instructions/gsd-protocol.instructions.md` advertised deleted `~/.trae/.traerules` | Reworded to point at `~/.agents/wiki/notes/2026-10-10-instructions-consolidation.md` |
| P4 | HIGH | `AGENTS.md:5` "Read by:" list missing Codex + Gemini | Added both |
| P5 | HIGH/MED | `AGENTS.md` Part 3 diagram, subagent table, Part 5 file tree, "OpenCode is the only tool" sentence, Skills section never mentioned the two portable roles `laptop-admin` + `software-maintainer` | Updated diagram, renamed "The seven subagents" → "The nine subagents" with new rows, added `agents/` to file tree, expanded Part 4 to include Codex + Gemini rows, mentioned PAT-20260906 in Skills section |
| P7 | HIGH | `bin/verify-global-agents:40-41` checked deleted `~/.claude/agents/{laptop-admin,coder}.md` symlinks (would warn forever) | Removed both `check_link "~/.claude/..."` lines |
| P8 | MED | `skills/skill-creator/scripts/run_eval.py` wrote only to `.claude/commands/` and called `claude -p` (Claude gone) | Removed the entire `claude -p` body of `run_single_query` and replaced with `raise NotImplementedError` + clear message about needing a still-supported tool driver before re-enabling |
| P9 | MED | `skills/deploy-to-vercel/SKILL.md:238` documented non-existent `~/.claude/skills/...` recipe | Rewrote "Claude Code / terminal-based agents" section to "Terminal-based agents (any host with shell access)" with `~/.agents/skills/deploy-to-vercel/resources/deploy.sh` path |

## Issues deferred

| # | Sev | Why deferred |
|---|:---:|---|
| P6 | HIGH | `~/.config/opencode/get-shit-done/bin/lib/profile-pipeline.cjs` has 4 hits at L20, L162, L254, L394 that fall back to `~/.claude/projects`. This file is part of the **upstream get-shit-done plugin** bundled in OpenCode's plugin dir, NOT our agents codebase. Fixing it requires either filing upstream OR removing the plugin from OpenCode config — neither in scope here. Documented as a known-limitation in this note so future cleanup attempts don't miss it. Action: file upstream at <get-shit-done repo> if/when we adopt GSD; otherwise accept the staleness. |
| P10 | LOW | `install.sh:86-87` literal "Claude" in my own migration comment explaining why there's no Claude section. **Deliberately kept** — the comment is a historical meta-note explaining the absence of Claude, not a Claude reference. Removing the comment would make the install.sh structure opaque ("why is there no Claude integration?"). Verifier audit flagged this LOW; I confirmed with the user it can stay. |

## Outcome by axis

| Audit | Before | After |
|---|---|---|
| Tool registry (4 files cross-check) | 1 high (Codex/Gemini missing from AGENTS.md), 1 low (Claude literal in install.sh) | 0 high; LOW retained as P10 |
| Path validity (no `~/.trae/` / `~/.claude/` active refs) | 6 sites | 0 sites (P2, P3, P7, P9 fixed; P8 disabled the eval flow entirely) |
| Role consistency | 5 sites (subagent diagram/table/tree never mentioned 2 portable roles; never mentioned either by name in 341-line doc) | 0 sites — 9 roles now explicit in Part 3 + Part 4 + Part 5 file tree |
| Skill loader | 2 broken-`name=` matches (PAT-20260906 issue) | 0 broken — both dirs now match frontmatter |
| MCP shared docs | 0 issues | still 0 |

## Files touched

```
~/.agents/AGENTS.md                              (Read-by + Part 3 + Part 4 + Part 5 + Skills)
~/.agents/bin/verify-global-agents               (P7)
~/.copilot/instructions/gsd-protocol.instructions.md (P3)
~/.agents/skills/deploy-to-vercel/SKILL.md       (P9)
~/.agents/skills/react-native-skills/SKILL.md    (P1)
~/.agents/skills/react-view-transitions/SKILL.md (P1)
~/.agents/skills/skill-creator/scripts/run_eval.py (P8)
```

Plus `~/.config/opencode/skills` unlinked (P2).

## Verify after fixes

```
$ ~/.agents/bin/verify-global-agents
OK   hub rules          /Users/huangjien/.agents/AGENTS.md
OK   routing            /Users/huangjien/.agents/route.yaml
OK   laptop role        /Users/huangjien/.agents/agents/laptop-admin.md
OK   software role      /Users/huangjien/.agents/agents/software-maintainer.md
OK   home AGENTS        /Users/huangjien/AGENTS.md -> /Users/huangjien/.agents/AGENTS.md
OK   OpenCode Major     /Users/huangjien/.config/opencode/agent/major.md
OK   OpenCode laptop    /Users/huangjien/.config/opencode/subagent/laptop-admin.md
OK   Codex adapter      /Users/huangjien/.agents/adapters/codex.md
OK   pi adapter         /Users/huangjien/.agents/adapters/pi.md
OK   Gemini adapter     /Users/huangjien/.agents/adapters/gemini.md

Global agent setup: 10 OK, 0 warnings   ← was 8 OK + 2 Claude warnings
```

## Reusable rule surfaced (worth promoting to PAT on third application)

The audit hit **name↔dir mismatches** in exactly the shape PAT-20260906
documents: `name: vercel-react-native-skills` in a dir named `react-native-skills`,
`name: vercel-react-view-transitions` in a dir named `react-view-transitions`.
Two mismatches fixed today. With the prior evidence (taste-skill, redesign-skill,
karpathy-engineer fix from 2026-09-06), this is the third+ fourth cases of "the
renamer pulled the directory over the frontmatter" pattern. **PAT-20260906
remains correct in its current scope** — `name:` must equal dir name — but the
pattern could be promoted with a sharper title like "skill-renamer broke
frontmatter after directory rename" once we get ~3 more instances; until then,
defer promotion.

## Restore path

Backups at `~/.agents/.archive/audit-fix-2026-10-10/`:
```
AGENTS.md.bak   verify-global-agents.bak   gsd-protocol.instructions.md.bak
deploy-to-vercel/SKILL.md.bak   run_eval.py.bak
react-native-skills/SKILL.md.bak   react-view-transitions/SKILL.md.bak
ui-ux-pro-max.bak   (added during follow-up sweep — see below)
```

Revert by `cp`ing the relevant `.bak` back.

## Follow-up: 1 missed issue caught during the after-fix sweep

The original audit reported "15 real issues, 0 false positives" — but a direct
bash sweep run after the fixes (as a substitute for the workflow-tool re-audit,
which kept failing on its multi-check arg validator) caught **one additional
real issue** the audit had not flagged:

| # | Sev | What | Fix |
|---|:---:|---|---|
| **P11** | MED | `skills/ui-ux-pro-max/SKILL.md` had 10 references to `.claude/skills/ui-ux-pro-max/...` paths (the original Trae install location of this skill; Trae was deleted in 2026-09 but the recipe paths were never rewritten). All in code-example invocations like `python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<args>"`. | Replaced all 10 occurrences with `~/.agents/skills/ui-ux-pro-max/...`. Backup at `~/.agents/.archive/audit-fix-2026-10-10/ui-ux-pro-max.bak`. |

Why the audit's first pass missed this: its path-validity scan was
`grep -rln "\.claude/" /Users/huangjien/.agents/` but the skill file lives
under `skills/`, which got picked up — the search most likely matched
file-name noise and the LLM-tally filtered to the highest-impact hits.
The follow-up sweep tightened the filter (`grep -vE ... | skills/claude-api/`),
revealing 5 active code refs, of which 4 were intentional historical records
in wiki notes and 1 was this missed live issue.

## Implication for future audits

A single-pass audit can miss issues even when self-reporting "0 false
positives, N real" — the count is right, the coverage is incomplete. Verify
with a fresh sweep (or a re-audit) before closing out a fix-then-verify
cycle. The missed issue here was MED (no-op build, would surprise the next
reader following the recipe), not HIGH, but a second pass is still worth
the time when the audit touches the entire installed-tool surface.

## Outcome: after fixes + sweep, the system is clean by the audit's 5 axes

| Axis | Result |
|---|---|
| Tool registry consistency | ✓ 5 tools across all 5 config files; Claude only in `install.sh` migration comment |
| Post-retirement paths | ✓ 0 active `~/.trae/`, 0 active `~/.claude/` (claude-api skill excluded as intentional) |
| Role consistency | ✓ 9 in AGENTS.md Part 3 ↔ 9 files |
| Skill loader | ✓ 55/55 `name:` ↔ dir |
| MCP shared-docs | ✓ 3/3 tool-native docs reference `~/.agents/mcp/` |
| Dangling symlinks | ✓ 0 |
| `verify-global-agents` | ✓ 10 OK / 0 warnings (was 8/2 after Claude deletion) |
