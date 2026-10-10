---
name: quality-verification
description: Run a generic lint → test → build pipeline with configurable auto-fixes and policy gates for any project's submodules. Use when CI fails, before merging, or after refactors to converge the whole repo back to green.
metadata:
  author: local
  version: "1.1.0"
  last_reviewed: 2026-09-26
  source: internal://.agents/skills/quality-verification
  local_only: true
---

# Quality Verification

A generic, config-driven runner that executes `lint → test → build` over one or more submodules of your repo, applying user-declared auto-fixes between retries, then enforcing optional policy gates (secrets / IaC / logging / etc.). Not coupled to any specific language or framework — every project-specific command, regex, and gate is declared in `.quality-verification/config.json`.

## Quick Start

From the project root:

```bash
python3 .agents/skills/quality-verification/scripts/quality_verification.py
```

Write a machine-readable report:

```bash
python3 ... --json-out .quality-verification/report.json
```

The script exits non-zero if any configured module fails lint, test, or build.

## Configuration

Create `.quality-verification/config.json` at the project root. **Required** — if missing, the script prints a hint and exits cleanly.

```json
{
  "modules": [
    {
      "name": "frontend",
      "path": "packages/web",
      "lint_cmd": ["pnpm", "lint"],
      "test_cmd": ["pnpm", "vitest", "run"],
      "build_cmd": ["pnpm", "build"],
      "auto_fix_lint": [["pnpm", "format"]],
      "auto_fix_test": [["pnpm", "install"]],
      "policy_checks": {
        "secrets": true,
        "log_secrets": true,
        "iac": false,
        "pydantic": false,
        "contract_first": false
      },
      "file_scan_ignores": ["vendor/", "generated/"]
    },
    {
      "name": "backend",
      "path": "services/api",
      "lint_cmd": ["ruff", "check", "src"],
      "test_cmd": ["pytest", "-q"],
      "build_cmd": null,
      "test_env": { "DOTENV_IGNORE": "1" },
      "auto_fix_lint": [["ruff", "format", "src"], ["ruff", "check", "--fix", "src"]],
      "policy_checks": {
        "pydantic": true,
        "contract_first": true
      }
    }
  ]
}
```

### Module fields (all optional except `name` and `path`)

| Field | Type | Default | Notes |
|---|---|---|---|
| `name` | string | — | Display id; used in cache keys and reports |
| `path` | string | — | Relative to project root |
| `lint_cmd` | `string[]` | `["make", "lint"]` | Exit 0 = pass |
| `test_cmd` | `string[]` | `["make", "test"]` | Exit 0 + coverage thresholds met |
| `build_cmd` | `string[] \| null` | `null` | Optional; only run if set |
| `coverage_cmd` | `string[] \| null` | `null` | Run after a successful `test_cmd` |
| `enabled` | bool | `true` | |
| `coverage_exclusions` | `string[]` | `[]` | Substring match against file path |
| `min_total_coverage` | float | `85.0` | 0 = don't enforce |
| `min_file_coverage` | float | `70.0` | 0 = don't enforce |
| `targeted_coverage_threshold` | float \| null | `null` | Sugar for `coverage_allowlist.threshold` |
| `auto_fix_lint` | `string[][]` | `[]` | Commands tried in order on lint fail |
| `auto_fix_test` | `string[][]` | `[]` | Commands tried in order on test fail |
| `auto_fix_build` | `string[][]` | `[]` | Commands tried in order on build fail |
| `test_env` | `object` | `{}` | Env vars injected when running tests |
| `policy_checks` | `object` | (see below) | Toggles for each policy gate |
| `coverage_allowlist` | `object \| null` | `null` | `{"command": [...], "threshold": 90}` |
| `coverage_log_path` | `string \| null` | `test.log` | Path to coverage log (relative → project root) |
| `coverage_total_regex` | string | `Coverage:\s*(\d+\.\d+)%` | Override if your reporter uses a different format |
| `coverage_file_regex` | string | `^(\d+\.\d+)%\s+\d+/\d+\s+(.+)$` | Per-file line matcher |
| `file_scan_ignores` | `string[]` | `[]` | Extra substrings excluded from policy scans (in addition to defaults) |

### Policy check defaults

```json
{
  "secrets": true,
  "iac": true,
  "log_secrets": true,
  "pydantic": false,
  "contract_first": false
}
```

| Key | Detects |
|---|---|
| `secrets` | AWS access keys, private keys, `password=`/`api_key=`/`secret=` literal hard-coding |
| `log_secrets` | Log lines that include `password`/`secret`/`token`/`api_key` followed by a quoted value |
| `iac` | Terraform / K8s / YAML risky patterns (`0.0.0.0/0`, public ACLs, `runAsRoot`, etc.) |
| `pydantic` | (Python) backend routes lacking `from pydantic import BaseModel` |
| `contract_first` | (Python) backend API changes without contract tests |

### Default file-scan ignores

`.git`, `.dart_tool`, `build`, `node_modules`, `.venv`, `venv`, `.quality-verification`, `dist`, `.next`, `.turbo`, `.cache`, `coverage`, `.nyc_output`, `.omo`, `.opencode`. Add project-specific ones via `file_scan_ignores`.

## Command-Line Options

| Option | Default | Description |
|---|---|---|
| `--root PATH` | script location | Project root |
| `--phase {lint,test,all}` | `all` | Which phase(s) to run (build runs only when `build_cmd` is set) |
| `--max-iterations N` | `5` | Per-phase retry budget |
| `--json-out PATH` | none | Write JSON report |
| `--dry-run` | off | Preview without executing |
| `--parallel` | off | Run modules concurrently (max 4) |
| `--no-cache` | off | Bypass cache |
| `--modules NAME …` | all | Restrict to named modules |

## Workflow

1. **Detect** git changes; skip modules with no changes under their folder.
2. **Lint** all modules. If a phase fails and `auto_fix_<phase>` is configured, retry up to `--max-iterations` times, applying each fix in order.
3. **Test** — same retry/fix loop. Coverage parsing + allowlist runs after the test command.
4. **Build** — only if `build_cmd` is set; same retry/fix loop.
5. **Policy gate** — after a clean lint, scan the project for secret/IaC/log violations. Any finding is treated as a lint failure (exit 2).

## Policy Check Details

### Secrets scan

Detects: `AKIA…` / `ASIA…` AWS keys, `BEGIN … PRIVATE KEY`, and quoted assignments to `password` / `secret` / `api_key` / `client_secret` / `access_token`. Files whose path contains `.example`, `.sample`, `testdata`, or `fixtures` are skipped automatically.

### Log-redaction scan

Flags lines that combine a logging call (`log`, `logger`, `print`, `console.log`) with `password`/`secret`/`token`/`api_key` followed by a quoted value of 3+ characters. This is conservative — it doesn't fire on benign usage like `console.log('… tokens=1234')`.

### IaC scan

Recursively scans `supabase/`, `infra/`, `infrastructure/`, and the project root for `.tf` / `.yaml` / `.yml` / `.json` files and flags `0.0.0.0/0`, public ACLs (`public-read` / `public-write`), K8s `allowPrivilegeEscalation: true`, and `runAsUser: 0` / `runAsRoot: true`.

### Python-specific gates (opt-in)

- `pydantic`: if `backend/src/authorconsole_api/` exists, every `.py` file must import Pydantic.
- `contract_first`: changes under `backend/src/authorconsole_api/` require at least one test whose name or content contains `contract`.

> Adapt these to your own backend conventions by editing the matching `_check_*` function in `scripts/quality_verification.py`.

## Coverage Integration

After tests pass, the script reads the configured `coverage_log_path` and parses total + per-file coverage using the configured regexes. Defaults:

```text
Coverage:\s*(\d+\.\d+)%           # total
^(\d+\.\d+)%\s+\d+/\d+\s+(.+)$    # per-file
```

If `coverage_allowlist.command` is set, it runs and gates test_ok on exit code.

## Caching

Successful runs are cached to `.quality-verification/cache.json` keyed by `{module}_{phase}_{file_hash}`. Cache is invalidated on `--no-cache` or when git working-tree changes are detected. Cached modules print `CACHE HIT`.

## Error Detection

The script inspects the tail of failed logs and prints hints for common issues: missing Flutter SDK, missing pytest, permission errors, out-of-memory, etc. These are generic, language-agnostic regexes — extend `_detect_common_environment_issue` for your stack.

## Examples

A minimal monorepo config (TypeScript + pnpm):

```json
{
  "modules": [
    {
      "name": "app",
      "path": ".",
      "lint_cmd": ["pnpm", "lint"],
      "test_cmd": ["pnpm", "vitest", "run"],
      "build_cmd": ["pnpm", "build"],
      "auto_fix_lint": [["pnpm", "format"]]
    }
  ]
}
```

A polyglot config (Go API + React frontend):

```json
{
  "modules": [
    {
      "name": "api",
      "path": ".",
      "lint_cmd": ["go", "vet", "./..."],
      "test_cmd": ["go", "test", "./..."],
      "build_cmd": ["go", "build", "./..."],
      "test_env": { "GOFLAGS": "-mod=readonly" }
    },
    {
      "name": "web",
      "path": "web",
      "lint_cmd": ["pnpm", "lint"],
      "test_cmd": ["pnpm", "vitest", "run"],
      "build_cmd": ["pnpm", "build"],
      "coverage_allowlist": {
        "command": ["node", "scripts/check-coverage.mjs"],
        "threshold": 80
      }
    }
  ]
}
```

## Success Criteria

Finish only when all conditions are true:

- For each configured module with git changes:
  - `lint_cmd` exits 0 and policy checks pass.
  - `test_cmd` exits 0 and coverage thresholds are met (if configured).
  - `build_cmd` exits 0 (if configured).
- Modules without git changes are skipped (cache hit).

## Migration from Older Versions

If you previously relied on the `writer` + `backend` defaults:

1. Create `.quality-verification/config.json` with explicit module entries.
2. Move any Dart/Python auto-fix commands from the script body into the matching module's `auto_fix_*` field.
3. Set `policy_checks.pydantic` / `policy_checks.contract_first` to `true` on backend modules if you want them.
4. Set `policy_checks.iac` to `false` for projects that don't use Terraform / K8s.
5. Move any custom coverage-allowlist script invocation into `coverage_allowlist.command`.
