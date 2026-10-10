---
kind: convention-note
date: 2026-10-10
session: project-level workflows directory creation
---

# 2026-10-10 — created `~/.agents/workflows/` for project-level workflow scripts

The five built-in workflow patterns (`codebase-audit`, `deep-research`,
`adversarial-review`, `code-review`, `multi-perspective`) come from the
pi-dynamic-workflows npm package at
`~/.pi/agent/npm/node_modules/@quintinshaw/pi-dynamic-workflows/`.

For *custom* project-specific workflows, the source files used to have
no home in `~/.agents/`. This session added one:

```
~/.agents/workflows/
└── README.md     ← convention + structure + when-to-use-vs-skill
```

**Future workflow files** go here, following `<verb>-<noun>.js`
lower-dash-case. They are invoked via the `workflow` tool's `script:`
parameter, which takes the **script body** as a string (not a file
path). The caller must read the file first and pass the contents:

```js
workflow({
  script: require('fs').readFileSync('~/.agents/workflows/<name>.js', 'utf-8'),
  args: {...},
});
```

**Do NOT pass a file path** — the runtime will fail with
`Invalid regular expression flag` because it tries to interpret the
path as inline JS. This is also documented in
`~/.agents/workflows/README.md`.

**Alternative**: save the workflow once (the runtime has a saved-workflow
mechanism under `~/.pi/agent/npm/node_modules/@quintinshaw/pi-dynamic-workflows/dist/workflow-saved.js`)
and call it by `name:` thereafter.

## Why top-level rather than nested

| Option | Verdict |
|---|---|
| `~/.agents/workflows/` (top-level, parallel to skills/) | ✓ chosen — discoverable, no symlink dance |
| `~/.agents/bin/workflows/` | rejected — `bin/` is for shell CLIs (symlinked to `~/.local/bin/`); workflows are not shell-callable |
| `~/.agents/wiki/workflows/` | rejected — wiki holds human-readable knowledge; workflows are executable scripts |
| `~/.pi/workflows/...` | rejected — that's the *runtime data dir* (saved runs, journals), not source |

## Integrate-as-you-go

This session also wired the new dir into the project doc surface so
future readers see it:

- `~/.agents/AGENTS.md` Part 5 file tree now lists `workflows/`
- `~/.agents/wiki/README.md` Layout table now lists the workflows dir
  (with a NOT-under-wiki qualifier since it's not part of the wiki)
- `~/.agents/workflows/README.md` documents the file-shape convention

When the first real workflow lands, copy the `README.md` skeleton
into the file as a starting point.

## Workflows created 2026-10-10 (same session)

Three starter workflows landed in the directory on the day it was
created. They were chosen to codify the patterns established during
the day's cleanups:

| File | Codifies | Invoke |
|---|---|---|
| `hub-audit.js` | The 5-axis audit we ran manually today (tool registry, post-retirement paths, role consistency, skill loader, MCP shared-docs) | `workflow({ script: "~/.agents/workflows/hub-audit.js" })` |
| `tool-retire.js` | PAT-20261010-absorbslim-ordering — 5-phase retirement (identify → absorb → slim → drop → verify) | `workflow({ script: "~/.agents/workflows/tool-retire.js", args: { tool: "Foo" } })` |
| `skill-loader-check.js` | PAT-20261010-skill-renamer-broke-frontmatter — single-axis `name:` ↔ dir match check | `workflow({ script: "~/.agents/workflows/skill-loader-check.js" })` |

All three follow the API documented in
`workflow-authoring/examples/` (top-level script, global `args`/`agent`/
`parallel`/`phase`, structured output via JSON schema, return plain JSON
at the bottom). All pass `node --check`.

## Related

- `~/.agents/workflows/README.md` — file convention
- `wiki/notes/2026-10-10-workflow-tool-bug.md` — known issue with
  the validator accepting single-check arrays but rejecting multi-check
  ones (relevant only for using built-in patterns, not custom scripts)
