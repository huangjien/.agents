# Skill Impact — audit trail of skill edits

Every skill edit compiled from wiki patterns is recorded here: target,
motivating patterns, unified diff, validation plan, and outcome
(accepted/rejected). A rejected edit is reverted in the skill using the
recorded diff; the wiki itself is never rolled back.

---

## #1 — 2026-09-06 — write-a-skill: add name==directory rule

- **Motivated by:** PAT-20260906-skill-name-dir-mismatch
- **Change:** add a rule to the "Draft the skill" step and the Skill
  Structure notes requiring frontmatter `name` to equal the directory
  name, since VS Code's loader silently drops mismatches.

```diff
 2. **Draft the skill** - create:
    - SKILL.md with concise instructions
+   - YAML frontmatter whose `name:` is byte-identical to the directory name — VS Code Copilot silently drops the skill otherwise
    - Additional reference files if content exceeds 500 lines

 ## Review Checklist
 - [ ] Description includes triggers ("Use when...")
+- [ ] Frontmatter `name:` byte-identical to directory name
 - [ ] SKILL.md under 100 lines
```

- **Validation plan:** rule already validated during the 2026-09-06
  migration (three skills failed to load until renamed / given
  frontmatter; all 35 load after the fix).
- **Outcome:** accepted (2026-09-06)

## #2 — 2026-09-19 — workspace/website/.agents/skills: symlink 3 Vercel duplicates

- **Motivated by:** PAT-20260919-skill-duplication-drift
- **Change:** replace three byte-identical skill copies in
  `/Users/huangjien/workspace/website/.agents/skills/` with symlinks to
  the global hub at `~/.agents/skills/`, so any future edit propagates
  automatically and the global copy stays canonical. Backups kept as
  `<skill>.bak-YYYYMMDD-HHMMSS` until verified on real task loads.

| Old (copy) | New (symlink) |
| --- | --- |
| `vercel-composition-patterns/` | `vercel-composition-patterns -> ~/.agents/skills/vercel-composition-patterns` |
| `vercel-react-best-practices/` | `vercel-react-best-practices -> ~/.agents/skills/vercel-react-best-practices` |
| `web-design-guidelines/` | `web-design-guidelines -> ~/.agents/skills/web-design-guidelines` |

- **Validation plan:** next React/Next.js task on this project should
  load exactly one copy of each skill (no `diff` noise); if the
  skill-wiki lookup shows the project copy and global copy diverging in
  a future session, the symlink silently broke and the wiki should be
  patched to recommend a Makefile / cron `diff -rq` audit.
- **Outcome:** accepted (2026-09-19)
