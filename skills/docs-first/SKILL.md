---
name: docs-first
description: Verify library APIs against the installed version before writing code — read the lockfile, fetch current docs/changelog, cite what changed. Use when writing or reviewing code that calls a library or framework API, when upgrading dependencies, or when unsure whether an API in your memory is still current.
metadata:
  author: local
  version: "1.0.0"
  last_reviewed: 2026-09-26
  source: ""
  local_only: true
---

# Docs-First — current docs beat training data

Training data is stale; lockfiles are truth. Before generating code that
calls a library API, ground it in the version actually installed in the
project.

## Workflow

1. **Pin the installed version** — read it from the lockfile, never from
   memory:
   - Dart/Flutter: `pubspec.lock` (or `flutter pub deps`)
   - Python: `uv.lock` / `pyproject.toml`
   - JS/TS: `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml`

2. **Fetch current docs for that version**, first match wins:
   - A doc-retrieval MCP if connected (`gitmcp` — generic server or
     per-repo URLs like `https://gitmcp.io/simolus3/drift`; `context7`
     as fallback while its quota lasts)
   - Built-in web search/fetch against the official docs site, pinned to
     the installed version where the site supports it
   - The repo's `CHANGELOG.md` / migration notes for everything between
     your training cutoff and the installed version

3. **Diff your knowledge.** List what differs between the API you'd have
   written from memory and what the docs say: deprecations, renames,
   removed params, new idioms. If nothing differs, one line saying so is
   enough — don't pad the response with the verification process.

4. **Cite.** Name the source (URL or MCP tool + repo) and the version
   you verified against. If you could not verify, write
   "unverified against <version>" on the code that depends on it.

## Rules

- Never invent an API signature. If the docs don't confirm it, mark it.
- Major-version jumps and 0.x packages always get the
  changelog/migration check — 0.x minors are allowed to break.
- When helping with a dependency upgrade, run this per upgraded package
  to catch breakage before the test suite does.
- Pairs with curated static skills (e.g. `vercel-react-best-practices`):
  those provide depth, this provides freshness.
