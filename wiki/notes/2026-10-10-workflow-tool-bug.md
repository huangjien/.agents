---
kind: tool-issue-note
date: 2026-10-10
session: codebase-audit re-run via workflow tool
related: PAT-20261010-absorbslim-ordering
---

# 2026-10-10 — workflow tool's `codebase-audit` arg validator rejects multi-check arrays

Encountered while trying to re-audit the `~/.agents/` installation
after the audit-fix pass. The built-in `codebase-audit` workflow
requires `args.checks` to be a JSON array of strings per
`~/.pi/agent/npm/node_modules/@quintinshaw/pi-dynamic-workflows/skills/workflow-patterns/SKILL.md`.

## What was tried (9 attempts, all rejected with the same message)

```text
Built-in workflow "codebase-audit" requires args.checks to be a non-empty array of non-empty strings.
```

The first successful invocation in this session used a single check:

```xml
<args>
  <scope>~/.agents/</scope>
  <checks>
    <item>broken symlinks</item>
  </checks>
</args>
```

That worked. Subsequent attempts with 5 checks, each written as a
direct child `<item>...</item>` of `<checks>`, all rejected:

- Direct flat list: rejected
- Nested `<item>` wrapper around direct children: rejected
- Single combined string: rejected
- Even the previously-working single-item format: rejected after
  multi-item attempts were made

## Suspected cause

The validator doesn't grok multi-element arrays passed via the
`<item>` form once any nested wrapping is present. The session-level
context may also have shifted during the day — the validator had
different behavior on the first vs. later attempts.

This is likely a bug in pi-dynamic-workflows' argument parser
rather than something the user can fix locally.

## Workaround used

Switched to direct bash verification — same 5 axes (tool registry
consistency, post-retirement path validity, role consistency,
skill loader readiness, MCP shared-docs integrity), comparable
coverage, $0 cost instead of ~$0.54 per workflow run.

The bash sweep also caught **one issue the workflow-driven audit
had missed**: `skills/ui-ux-pro-max/SKILL.md` had 10 `.claude/skills/...`
path references (P11, fixed). Workflow-vs-direct-bash had different
coverage characteristics — both are useful.

## Action items

- **Upstream bug report**: file at
  `github.com/quintinshaw/pi-dynamic-workflows` (or wherever the
  repo is) — describe reproduction (pass `<item>` arrays to
  `workflow(name: "codebase-audit", args: {...})` via `subagent`'s
  workflow-tool integration; observe validator rejection). Not
  filed from this session.
- **Local workaround**: when you need a multi-axis check, do it as
  N separate single-check workflows (each ~$0.04 instead of the
  multi-axis `$0.54`) or fall back to a direct bash sweep.

## Related

- `wiki/notes/2026-10-10-audit-fixes.md` — the original audit pass
  that produced the 15 issues
- This note — the failed re-audit + the bash workaround that
  surfaced P11 (the audit-missed issue)
