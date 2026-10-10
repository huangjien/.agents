---
id: PAT-20260919-skill-duplication-drift
status: promoted
models: []
domain: tooling
created: 2026-09-19
last-touched: 2026-09-19
---

# Identical skills in global + project dirs silently drift after first edit

## Symptom
Three Vercel skills exist byte-identical in both `~/.agents/skills/` and
in `/Users/huangjien/workspace/website/.agents/skills/`
(`vercel-composition-patterns`, `vercel-react-best-practices`,
`web-design-guidelines`). All 11 / 60 / 1 files match by md5 today, but
the first edit applied to one copy will fork them silently — no warning,
no error. The skill-wiki pattern loader picks one copy based on tool
precedence; whichever copy loses becomes invisible until the next reload.

## Root cause
Skills were copied from the global hub into a project during initial
setup to enable project-local discovery, with no symlink or sync
mechanism. Once duplicated, the two copies have no enforced relationship:
`diff` returns nothing today only because no one has touched one without
the other. The same drift risk applies to any future skill copy.

## Rule / workaround
Project-level skill directories that hold byte-identical content from the
global hub MUST be symlinks to the global directory, not copies. When a
skill legitimately needs a project-specific override, that override lives
in a *different* skill directory (different name) so the inheritance
chain is explicit. A pre-commit or weekly `diff -rq` between the global
hub and every project's `.agents/skills/` catches any new drift before
it matters.

## Evidence
2026-09-19, skill-conflicts investigation. `comm -12` between global and
project skill lists showed three names; `find -type f -exec md5` for
each pair showed all files byte-identical. Both copies of each skill
were created on different dates (global Mar 3 2026; project Sep 19 2026)
showing the copy-paste was a deliberate project setup step, not an
accident.

## Related
Skills: skill-wiki, write-a-skill · Patterns: PAT-20260906-skill-name-dir-mismatch