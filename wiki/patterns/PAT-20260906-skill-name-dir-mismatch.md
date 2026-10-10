---
id: PAT-20260906-skill-name-dir-mismatch
status: promoted
models: []
domain: tooling
created: 2026-09-06
last-touched: 2026-09-06
---

# VS Code silently skips skills whose frontmatter name ≠ directory name

## Symptom
Skills that exist on disk and have valid SKILL.md content simply do not
appear in VS Code Copilot's skill list (`/skills`, Chat: Open
Customizations). No error, no warning — the skill is just invisible.

## Root cause
VS Code's Agent Skills loader validates that the YAML frontmatter `name`
field matches the parent directory name and drops the skill on mismatch
(documented in code.visualstudio.com/docs/agent-customization/agent-skills).
Other loaders (Trae, ZCode) resolve by scanning and tolerate the
mismatch, so a skill can work in one tool while silently failing in
another — the failure only surfaces when you switch tools.

## Rule / workaround
When creating or renaming any skill: the frontmatter `name:` and the
directory name must be byte-identical. After any rename, verify the skill
still loads in every tool that consumes it. A skill with no frontmatter
at all fails the same way — always emit frontmatter.

## Evidence
2026-09-06, Trae→VS Code migration session: `~/.agents/skills/taste-skill`
(frontmatter `name: design-taste-frontend`) and `redesign-skill`
(`name: redesign-existing-projects`) would not load in VS Code 1.136.1
until the directories were renamed; `karpathy-engineer` had no frontmatter
and needed it added. After fixes, all 35 hub skills load.

## Related
Skills: write-a-skill, skill-wiki · Patterns: —
