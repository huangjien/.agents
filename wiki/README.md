# Skill Wiki

A persistent knowledge base of failure patterns and successful strategies,
sitting **between** raw session experience and the active skills in
`~/.agents/skills/`. Adapted from *WikiSkill: Compiling Agent Experience
into Persistent Knowledge for Skill Evolution* (arXiv 2608.27454).

```
session experience (raw, never stored here)
        │  Workflow A — record
        ▼
~/.agents/wiki/patterns/*.md      ← persistent, never rolled back
        │  Workflow B — compile (atomic, gated, audited)
        ▼
~/.agents/skills/<name>/SKILL.md  ← active skills (revertible via diffs)
```

## Layout

| Path | Purpose |
|------|---------|
| `patterns/PAT-*.md` | One page per pattern: symptom → root cause → rule → evidence |
| `patterns/_TEMPLATE.md` | Copy this to start a new pattern |
| `index.md` | Catalog — one line per pattern, with status |
| `notes/NOTE-*.md` | Dated session notes (consolidations, retirements, refactors). Underlying record for non-pattern observations |
| `audits/<topic>-YYYYMMDD.json` | Raw machine-output artifacts from `codebase-audit`-style runs. Human summary lives in the matching `notes/` entry |
| `logs.md` | Append-only maintenance log |
| `skill-impact.md` | Audit trail of every skill edit: diff, motivation, outcome |
| `~/.agents/workflows/<verb>-<noun>.js` (project-level, NOT under `wiki/`) | Custom JavaScript workflow scripts invoked by the `workflow` tool. Built-in patterns live in pi-dynamic-workflows npm pkg |

## The two workflows

Both live in the `skill-wiki` skill (`~/.agents/skills/skill-wiki/`):

- **Record** (after a notable failure/success): root-cause analysis →
  new or patched pattern page → update `index.md` → append `logs.md`.
- **Compile** (on request or when patterns accumulate): pick ONE pattern
  → ONE atomic edit to ONE skill → record the unified diff and validation
  plan in `skill-impact.md` → apply.

## PAT lifecycle

Each pattern carries a `status:` field in its frontmatter:

| Status | Meaning | Promotion criteria |
|---|---|---|
| `candidate` | Just observed; one application recorded but the rule isn't general enough to trust yet. Safe to read; **do NOT** act on as a rule yet | recorded only — needs more verified applications |
| `promoted` | Evidence threshold met; safe to treat as a rule in new work | either (a) ≥1 instance of a one-shot failure (e.g., the loader-side bug — single evidence is enough), or (b) ≥3 verified applications of a repetitive rule |
| `rejected` | Tried, didn't pan out; kept as a record of what doesn't work | kept for traceability; never edited into a skill |
| `superseded` | Replaced by a newer pattern (link via `supersedes:` field) | when a sharper/cleaner pattern emerges |

**Promotion example** — `PAT-20261010-skill-renamer-broke-frontmatter`:
- 2 prior instances from 2026-09-06 (taste-skill, redesign-skill,
  karpathy-engineer); 2 new instances caught 2026-10-10
  (react-native-skills, react-view-transitions). 5 total
  before promotion. Promoted.

**Candidate example** — `PAT-20261010-absorbslim-ordering`:
- Only 2 fully verified applications of the 5-step order
  (instructions-consolidation was partial because Claude/Codex
  Gemini docs weren't slimmed in the same pass; claude-removal
  was full). Threshold is 3 full-cycle applications. Stays
  `candidate` until next tool retirement.

## Ground rules (from the paper's ablations)

1. **The wiki never enters always-on context.** Task agents must not see
   it — leaked workarounds degrade trajectories and skill quality.
   It is read only during skill maintenance.
2. **The wiki is never rolled back.** A rejected skill edit does not
   delete its pattern; the pattern gets `status: rejected` or is refined
   by a superseding pattern.
3. **One atomic edit per compile.** No bulk rewrites of skills.
4. **Model-specific quirks stay in the wiki**, tagged `models:` — never
   in shared skills (negative transfer: one model's workaround measurably
   hurt a stronger model).
5. **Every skill edit is audited** in `skill-impact.md`; rejected edits
   are reverted using the recorded diff. (A `git init` in `~/.agents`
   would make rollback trivial — deliberately not done; ask the user
   first.)
