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

## #3 — 2026-10-26 — video: channel profiles are the narrative-grammar extension point

- **Motivated by:** PAT-20261026-channel-profile-grammar-block
- **Change:** one atomic insertion into
  `~/workspace/ai-video-factory/.agents/skills/video/SKILL.md` (the
  `~/.agents/skills/video` copy is a symlink to it), between the command
  table's closing line and "### Visual components". Also bumps the
  frontmatter `last_reviewed` to 2026-10-26. Adds an 8-line subsection:
  profile block PAIRS under `packages/prompts/prompts/` are the zero-code
  extension point for cross-video story grammar; judge criteria stay in
  the profile's review block (scoped, regeneration-coupled cost);
  story-shape changes never touch storyboard generation; pin with
  `toContain` tests, `pnpm build`, smoke `video prompts show`.

```diff
--- a/.agents/skills/video/SKILL.md
+++ b/.agents/skills/video/SKILL.md
@@ frontmatter @@
-  last_reviewed: 2026-10-17
+  last_reviewed: 2026-10-26
@@ after "Every command accepts `--cwd <dir>` … updates `state.yaml`." @@
+### Channel profiles are the narrative-grammar extension point (zero code)
+
+Cross-video story grammar — narrator voice, pacing, arc, plot engine —
+extends via channel-profile prompt block PAIRS in `packages/prompts/prompts/`:
+`draft-<profile>.md` (drafter rules) + `review-<profile>.md` (judge
+criteria), appended only when the article declares the profile. Zero
+TypeScript. Rules: judge criteria live in the profile's review block, never
+the global judge prompt (findings cost regeneration cycles — scope them);
+story-shape changes never touch storyboard generation (`article.md` is the
+source of truth, the storyboard re-derives); keep vocabulary consistent
+with published films (the seven plot engines in `chinese-storybook` reuse
+the naming from `projects/故事的7种基本情节`). Workflow: edit the pair → pin
+new content with `toContain` tests in
+`packages/draft/src/channel-profile.test.ts` → `pnpm build` → smoke
+`video prompts show <block>`.
+
```

- **Validation plan:** next channel-profile change (new profile, arc or
  engine edit, or a story-channel draft) should be doable as a prompt-pair
  edit with no TypeScript; the session doing it should find the rule in
  the video skill and not re-derive the mechanism from source. If a
  future session instead reaches for the global draft prompt or the
  storyboard generator, the span is misplaced or too weak — refine rather
  than revert.
- **Outcome:** pending
