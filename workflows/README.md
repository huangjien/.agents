# Workflows

Custom JavaScript workflow scripts for the `workflow` tool. Each file
defines a multi-agent task flow using `agent()`, `parallel()`, and
`pipeline()`.

For the 5 *built-in* patterns (`codebase-audit`, `deep-research`,
`adversarial-review`, `code-review`, `multi-perspective`), see
`~/.pi/agent/npm/node_modules/@quintinshaw/pi-dynamic-workflows/skills/workflow-patterns/`.

## Files in this directory

| File | What it does | Codifies |
|---|---|---|
| `hub-audit.js` | 5-axis parallel audit on `~/.agents/` (tool registry, post-retirement paths, role consistency, skill loader, MCP shared-docs) | Today's manual audit codified as a runnable workflow |
| `tool-retire.js` | 5-phase tool retirement (identify → absorb → slim → drop → verify) | `PAT-20261010-absorbslim-ordering` (candidate) |
| `skill-loader-check.js` | Single-axis: each `~/.agents/skills/*/SKILL.md` has frontmatter `name:` matching its dir | `PAT-20261010-skill-renamer-broke-frontmatter` (promoted) |

## How a file is structured

The file is a top-level ES module (no `export default async function`
wrapper — the runtime wraps the body in an async function so a bare
top-level `return` works). Three sections:

```js
// 1. metadata (required, first non-comment statement)
export const meta = {
  name: 'audit_repo',                     // short_snake_case
  description: 'Run 4 parallel audit checks.',
  phases: [{ title: 'Discover' }, { title: 'Audit' }],  // optional
};

// 2. globals the runtime injects: args, agent, parallel, pipeline,
//    phase, budget, log, cwd, process.cwd()

// 3. body — at the end, return a plain-JSON-serializable result
phase('Discover');
const results = await parallel([
  () => agent('Audit tool registry.', { label: 'check:tool-registry' }),
  () => agent('Audit post-retirement paths.', { label: 'check:post-retirement' }),
]);
return { results };
```

## How a file is invoked

The `workflow` tool's `script:` parameter takes the **script body** as
a string — not a file path. So the caller must read the file and pass
its contents:

```js
workflow({
  script: require('fs').readFileSync('~/.agents/workflows/hub-audit.js', 'utf-8'),
  args: { scope: '~/.agents/' },
});
```

**Do NOT pass a path** — the runtime tries to interpret the value as
inline JS, hits a parse error on the first line (a `//` comment), and
fails with `Invalid regular expression flag`. Always read the file
first, then pass the contents.

Alternative: save the workflow once (the runtime has a "saved
workflows" mechanism, see `~/.pi/agent/npm/node_modules/@quintinshaw/pi-dynamic-workflows/dist/workflow-saved.js`)
and call it by `name:` thereafter.

## Conventions

- Lowercase, dash-separated file names (`<verb>-<noun>.js`)
- `meta.name` is snake_case
- No shell-out: don't `bash exec` scripts in `~/.agents/bin/`. Compose
  via `agent()` instead so the runner can track token budgets and
  surface failures
- Pure JavaScript, no transpile step — the `workflow` tool runs it
  directly
- No top-level return wrapped in a function — the runtime wraps the
  body in `async function() { ... }`, so bare `return` at the end is
  the right shape (matches the example files in
  `workflow-authoring/examples/`)

## Verifying a workflow without running it

`node --check` will fail with `Illegal return statement` on the
top-level `return` because plain Node parses the file as a script
(CommonJS) or module (ESM) and top-level return is not legal in
either. The workflow runtime uses Node's `vm` module to evaluate,
which *does* allow top-level return. So:

- `node --check file.js` will always fail on these files — that's a
  tooling limitation, not a real bug
- The canonical check is: invoke the workflow via the `workflow` tool
  and verify the result
- For local syntax-only checks, you can also pass the file contents
  via `cat file.js | head -50` and visually inspect

## When to use this directory instead of a SKILL

- A `SKILL.md` documents reasoning the agent should apply when *triggered*
- A workflow here runs an *executable* multi-agent process when
  invoked

If you're tempted to write a workflow, ask: could this also be a
skill trigger? If yes, prefer the skill (it's loaded as context, not
spawned as a subprocess). Reach for a workflow only when you need
**explicit multi-agent coordination** that the single-agent load
path can't do, like parallel reviewers or phased verification.
