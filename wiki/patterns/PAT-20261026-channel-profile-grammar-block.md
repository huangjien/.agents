---
id: PAT-20261026-channel-profile-grammar-block
status: promoted          # candidate | promoted | rejected | superseded
models: []               # repo mechanism, not model behavior ([] = tool/environment)
domain: "tooling"        # video-factory pipeline extension
created: 2026-10-26
last-touched: 2026-10-26  # promoted → video skill §Channel profiles (impact #3)
---

# Extend narrative grammar via channel-profile prompt blocks, not code

## Symptom
Adding story-structure rules (Booker's seven plot engines) to the AI
Video Factory draft pipeline looked like a code change. First instinct
pulls toward editing the global `draft-article.md` prompt (affects every
explainer topic) or touching storyboard generation.

## Root cause
The pipeline already separates three knobs that are easy to conflate:

1. **Cross-video grammar** — channel profile. Plain-markdown block pairs
   (`draft-<profile>.md` + `review-<profile>.md`) in
   `packages/prompts/prompts/`, loaded by name through the prompt
   registry and appended to the drafter's AND the judge's system prompts
   only when the profile is declared. Unknown values degrade to "no
   rules" — typo-tolerant by contract.
2. **Per-film art** — `image_style`, a separate frontmatter knob.
3. **Derived structure** — the storyboard re-derives from `article.md`
   on every `make`; narrative shape never belongs to storyboard
   generation because `article.md` is the source of truth.

So a narrative-grammar change is a prompt-file edit with zero
TypeScript, and its blast radius is scoped to drafts that declare the
profile. Judge criteria are regeneration-coupled (bar 90, up to 8
attempts), so scoping a criterion inside a profile's review block means
other drafts never pay for it.

## Rule / workaround
For any cross-video narrative/voice/pacing rule in the video factory:

1. Edit the profile block pair under `packages/prompts/prompts/` —
   drafter instruction in `draft-<profile>.md`, judge criterion in
   `review-<profile>.md`. Keep vocabulary consistent with already
   published films on the same subject.
2. Pin new content with a content-carrying test in
   `packages/draft/src/channel-profile.test.ts`
   (`expect(draft).toContain(...)` convention).
3. `pnpm build`, then smoke with `video prompts show <block-name>` —
   the CLI runs `dist/`, so the built registry must serve the edit.
4. Never touch storyboard generation for story-shape changes; never add
   narrative criteria to the global judge prompt where a profile can
   scope them; never force a plot archetype onto non-narrative topics.

## Evidence
2026-10-26 session (pi, repo `~/workspace/ai-video-factory`): added
"Plot engine — choose one, commit" to
`draft-channel-chinese-storybook.md` and "Uncommitted engine" to
`review-channel-chinese-storybook.md`; zero TypeScript changes beyond
tests; 1607/1607 repo tests green; `video prompts show` served both
edited blocks from the built CLI. Profile in production use:
`projects/玄武门` (`channel_profile: chinese-storybook` in article.md
frontmatter, set via `video draft --channel-profile`). Engine naming
kept identical to the published film `projects/故事的7种基本情节`.

## Related
Skills: video (~/workspace/ai-video-factory/.agents/skills/video) ·
Patterns: none yet
