#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal


Phase = Literal["lint", "test", "build", "all"]


@dataclass
class ModuleConfig:
    name: str
    path: str
    lint_cmd: list[str] = field(default_factory=lambda: ["make", "lint"])
    test_cmd: list[str] = field(default_factory=lambda: ["make", "test"])
    build_cmd: list[str] | None = None
    coverage_cmd: list[str] | None = None
    enabled: bool = True
    coverage_exclusions: list[str] = field(default_factory=list)
    min_total_coverage: float = 85.0
    min_file_coverage: float = 70.0
    targeted_coverage_threshold: float | None = None

    # --- Generic runner additions (replaces writer/backend hardcoding) ---
    # Auto-fix commands tried in order when a phase fails. Each entry is a
    # `[cmd, arg, ...]` list executed in `module_path`. Empty list = no fix.
    auto_fix_lint: list[list[str]] = field(default_factory=list)
    auto_fix_test: list[list[str]] = field(default_factory=list)
    auto_fix_build: list[list[str]] = field(default_factory=list)
    # Env vars injected when running tests (e.g. {"DOTENV_IGNORE": "1"}).
    test_env: dict[str, str] = field(default_factory=dict)
    # Which policy gates to enforce. Defaults are generic; project-specific
    # checks (pydantic, contract) are opt-in.
    policy_checks: dict[str, bool] = field(
        default_factory=lambda: {
            "secrets": True,
            "iac": True,
            "log_secrets": True,
            "pydantic": False,
            "contract_first": False,
        }
    )
    # Targeted coverage allowlist: {"command": [...], "threshold": 90}.
    # Runs after tests; failure blocks test_ok.
    coverage_allowlist: dict[str, Any] | None = None
    # Coverage parsing: log file path + regex for total coverage line.
    coverage_log_path: str | None = None
    coverage_total_regex: str = r"Coverage:\s*(\d+\.\d+)%"
    coverage_file_regex: str = r"^(\d+\.\d+)%\s+\d+/\d+\s+(.+)$"
    # Extra ignore substrings for the policy-file scan.
    file_scan_ignores: list[str] = field(default_factory=list)


@dataclass
class CommandResult:
    command: list[str]
    cwd: str
    exit_code: int
    duration_s: float
    log_path: str
    stdout: str = ""
    stderr: str = ""

    @property
    def ok(self) -> bool:
        return self.exit_code == 0

    @property
    def error_count(self) -> int:
        combined = self.stdout + self.stderr
        return len([l for l in combined.splitlines() if "error" in l.lower()])

    @property
    def lint_issue_count(self) -> int:
        combined = self.stdout + self.stderr
        lines = combined.splitlines()
        count = 0
        for line in lines:
            if re.search(r"\b(error|warning|info)\b", line, re.IGNORECASE):
                count += 1
        return count


@dataclass
class ModuleReport:
    name: str
    path: str
    skipped: bool = False
    lint_attempts: list[CommandResult] = field(default_factory=list)
    lint_fixes: list[str] = field(default_factory=list)
    test_attempts: list[CommandResult] = field(default_factory=list)
    test_fixes: list[str] = field(default_factory=list)
    build_attempts: list[CommandResult] = field(default_factory=list)
    build_fixes: list[str] = field(default_factory=list)
    coverage_result: CommandResult | None = None
    cache_hit: bool = False
    hash: str = ""
    total_coverage: float | None = None
    per_file_coverage: dict[str, float] = field(default_factory=dict)
    coverage_exclusions: list[str] = field(default_factory=list)
    min_total_coverage: float = 85.0
    min_file_coverage: float = 70.0
    targeted_coverage_ok: bool | None = None
    targeted_coverage_result: CommandResult | None = None
    policy_violations: list[str] = field(default_factory=list)

    @property
    def lint_ok(self) -> bool:
        if self.skipped:
            return True
        if not self.lint_attempts:
            return False
        last_attempt = self.lint_attempts[-1]
        return last_attempt.exit_code == 0 and last_attempt.lint_issue_count == 0

    @property
    def test_ok(self) -> bool:
        if self.skipped:
            return True
        if not self.test_attempts:
            return False
        if not self.test_attempts[-1].ok:
            return False
        return self._coverage_ok()

    @property
    def build_ok(self) -> bool:
        if self.skipped:
            return True
        if not self.build_attempts:
            return False
        return self.build_attempts[-1].ok

    def _coverage_ok(self) -> bool:
        # If targeted coverage check is configured, require it to pass.
        if self.targeted_coverage_ok is False:
            return False
        # If total coverage is available and a threshold is set, enforce it.
        if self.total_coverage is not None and self.min_total_coverage > 0:
            if self.total_coverage < self.min_total_coverage:
                return False
        # When targeted coverage is enabled, do not enforce blanket per-file thresholds.
        if self.targeted_coverage_ok is not None:
            return True
        # Fallback to per-file thresholds only when targeted coverage is not configured.
        if self.total_coverage is None:
            return True
        for file_path, coverage in self.per_file_coverage.items():
            if coverage < self.min_file_coverage and not self._is_excluded(file_path):
                return False
        return True

    def _is_excluded(self, file_path: str) -> bool:
        if not self.coverage_exclusions:
            return False
        for pattern in self.coverage_exclusions:
            if pattern in file_path:
                return True
        return False

    @property
    def total_duration(self) -> float:
        total = 0.0
        total += sum(a.duration_s for a in self.lint_attempts)
        total += sum(a.duration_s for a in self.test_attempts)
        if self.coverage_result:
            total += self.coverage_result.duration_s
        return total

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "path": self.path,
            "skipped": self.skipped,
            "cache_hit": self.cache_hit,
            "hash": self.hash,
            "lint": {
                "ok": self.lint_ok,
                "attempts": [a.__dict__ for a in self.lint_attempts],
                "fixes": self.lint_fixes,
                "total_duration_s": sum(a.duration_s for a in self.lint_attempts),
                "error_count": self.lint_attempts[-1].error_count
                if self.lint_attempts
                else 0,
                "issue_count": self.lint_attempts[-1].lint_issue_count
                if self.lint_attempts
                else 0,
            },
            "test": {
                "ok": self.test_ok,
                "attempts": [a.__dict__ for a in self.test_attempts],
                "fixes": self.test_fixes,
                "total_duration_s": sum(a.duration_s for a in self.test_attempts),
                "error_count": self.test_attempts[-1].error_count
                if self.test_attempts
                else 0,
                "total_coverage": self.total_coverage,
                "per_file_coverage": self.per_file_coverage,
                "low_coverage_files": [
                    {"path": fp, "coverage": cov}
                    for fp, cov in self.per_file_coverage.items()
                    if cov < 70.0 and not self._is_excluded(fp)
                ],
            },
            "build": {
                "ok": self.build_ok,
                "attempts": [a.__dict__ for a in self.build_attempts],
                "fixes": self.build_fixes,
                "total_duration_s": sum(a.duration_s for a in self.build_attempts),
                "error_count": self.build_attempts[-1].error_count
                if self.build_attempts
                else 0,
            },
            "coverage": self.coverage_result.__dict__ if self.coverage_result else None,
            "total_duration_s": self.total_duration,
        }


def _default_project_root() -> Path:
    here = Path(__file__).resolve()
    return here.parents[4]


def _load_config(project_root: Path) -> list[ModuleConfig]:
    config_path = project_root / ".quality-verification" / "config.json"
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            modules = []
            for m in data.get("modules", []):
                cfg = ModuleConfig(
                    name=m["name"],
                    path=m["path"],
                    lint_cmd=m.get("lint_cmd", ["make", "lint"]),
                    test_cmd=m.get("test_cmd", ["make", "test"]),
                    build_cmd=m.get("build_cmd"),
                    coverage_cmd=m.get("coverage_cmd"),
                    enabled=m.get("enabled", True),
                    coverage_exclusions=m.get("coverage_exclusions", []),
                    min_total_coverage=m.get("min_total_coverage", 85.0),
                    min_file_coverage=m.get("min_file_coverage", 70.0),
                    targeted_coverage_threshold=m.get(
                        "targeted_coverage_threshold", None
                    ),
                    auto_fix_lint=m.get("auto_fix_lint", []),
                    auto_fix_test=m.get("auto_fix_test", []),
                    auto_fix_build=m.get("auto_fix_build", []),
                    test_env=m.get("test_env", {}),
                    policy_checks=m.get(
                        "policy_checks",
                        {
                            "secrets": True,
                            "iac": True,
                            "log_secrets": True,
                            "pydantic": False,
                            "contract_first": False,
                        },
                    ),
                    coverage_allowlist=m.get("coverage_allowlist"),
                    coverage_log_path=m.get("coverage_log_path"),
                    coverage_total_regex=m.get(
                        "coverage_total_regex", r"Coverage:\s*(\d+\.\d+)%"
                    ),
                    coverage_file_regex=m.get(
                        "coverage_file_regex", r"^(\d+\.\d+)%\s+\d+/\d+\s+(.+)$"
                    ),
                    file_scan_ignores=m.get("file_scan_ignores", []),
                )
                # Targeted-coverage threshold sugar: allow
                # `targeted_coverage_threshold` to also fill
                # `coverage_allowlist.threshold` when not provided.
                if cfg.coverage_allowlist is None and cfg.targeted_coverage_threshold is not None:
                    cfg.coverage_allowlist = {
                        "command": None,
                        "threshold": cfg.targeted_coverage_threshold,
                    }
                modules.append(cfg)
            return modules
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
            raise SystemExit(1)

    # No config = nothing to do. Print a friendly hint and exit cleanly.
    print("No .quality-verification/config.json found.")
    print("Create one to declare modules. Example:")
    print('  {"modules": [{"name": "app", "path": ".", "lint_cmd": ["pnpm", "lint"],')
    print('                 "test_cmd": ["pnpm", "test"], "build_cmd": ["pnpm", "build"]}]}')
    raise SystemExit(0)


def _compute_hash(
    module_path: Path, files_pattern: str = "**/*.{py,dart,ts,js}"
) -> str:
    file_hash = hashlib.sha256()
    for f in module_path.rglob("*"):
        if f.is_file() and not any(
            p in str(f) for p in [".git", "node_modules", ".dart_tool", "build", "venv"]
        ):
            try:
                file_hash.update(f.read_bytes())
            except (OSError, PermissionError):
                pass
    return file_hash.hexdigest()[:16]


def _load_cache(project_root: Path) -> dict[str, dict]:
    cache_path = project_root / ".quality-verification" / "cache.json"
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_cache(project_root: Path, cache: dict[str, dict]) -> None:
    cache_path = project_root / ".quality-verification" / "cache.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def _run(
    *,
    command: list[str],
    cwd: Path,
    log_dir: Path,
    label: str,
    env: dict[str, str] | None = None,
    dry_run: bool = False,
) -> CommandResult:
    log_dir.mkdir(parents=True, exist_ok=True)
    safe_label = re.sub(r"[^a-zA-Z0-9._-]+", "_", label).strip("_") or "run"
    stamp = time.strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"{stamp}__{safe_label}.log"

    if dry_run:
        print(f"[DRY-RUN] Would run: {' '.join(command)}")
        print(f"[DRY-RUN] Working directory: {cwd}")
        return CommandResult(
            command=command,
            cwd=str(cwd),
            exit_code=0,
            duration_s=0.0,
            log_path=str(log_path),
        )

    merged_env = os.environ.copy()
    if os.environ.get("FLUTTER_SDK") and "PATH" not in (env or {}):
        merged_env["PATH"] = f"{os.environ['FLUTTER_SDK']}/bin:" + merged_env.get(
            "PATH",
            "",
        )
    if env:
        merged_env.update(env)

    start = time.time()
    stdout_output = []
    stderr_output = []

    with log_path.open("w", encoding="utf-8") as f:
        f.write(f"$ (cd {cwd}) {' '.join(command)}\n\n")
        f.flush()
        proc = subprocess.Popen(
            command,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=merged_env,
        )
        assert proc.stdout is not None and proc.stderr is not None
        for line in proc.stdout:
            sys.stdout.write(line)
            stdout_output.append(line)
            f.write(line)
        for line in proc.stderr:
            sys.stderr.write(line)
            stderr_output.append(line)
            f.write(line)
        exit_code = proc.wait()
    duration_s = time.time() - start
    return CommandResult(
        command=command,
        cwd=str(cwd),
        exit_code=exit_code,
        duration_s=duration_s,
        log_path=str(log_path),
        stdout="".join(stdout_output),
        stderr="".join(stderr_output),
    )


def _git_changed_files(project_root: Path) -> set[str] | None:
    try:
        probe = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=str(project_root),
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except FileNotFoundError:
        return None
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        return None

    commands = [
        ["git", "diff", "--name-only"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ]
    changed: set[str] = set()
    for cmd in commands:
        res = subprocess.run(
            cmd,
            cwd=str(project_root),
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        if res.returncode != 0:
            continue
        for line in res.stdout.splitlines():
            p = line.strip()
            if p:
                changed.add(p)
    return changed


def _read_tail(path: Path, *, max_lines: int = 80) -> str:
    if not path.exists():
        return ""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return ""
    tail = lines[-max_lines:]
    return "\n".join(tail)


def _detect_common_environment_issue(log_tail: str) -> str | None:
    patterns = [
        (
            "engine.stamp.*Operation not permitted",
            "Flutter/Dart tried to write into the Flutter SDK directory, but the environment "
            "does not permit it. Use a writable Flutter SDK (e.g., CI-installed SDK under $HOME) "
            "or run in an environment without filesystem sandboxing.",
        ),
        (
            "module.*not found|cannot import|ImportError",
            "Module dependency issue. Try running dependency install (flutter pub get, pip install, npm install).",
        ),
        (
            "No such file or directory.*flutter",
            "Flutter SDK not found or not in PATH. Set FLUTTER_SDK environment variable.",
        ),
        (
            "ruff.*command not found|python.*not found",
            "Python/ruff not found. Ensure Python and ruff are installed.",
        ),
        (
            "permission denied|Permission denied",
            "File permission issue. Check file permissions and try running with appropriate privileges.",
        ),
        (
            "dart.*not found|flutter.*not found",
            "Dart/Flutter not found in PATH. Ensure Flutter SDK is installed and accessible.",
        ),
        (
            "pytest.*not found|python.*pytest",
            "pytest not found. Run 'pip install pytest' or ensure Python environment is set up.",
        ),
        (
            "memory.*error|out of memory|killed",
            "Out of memory error. Try increasing available memory or running tests in smaller batches.",
        ),
    ]

    for pattern, hint in patterns:
        if re.search(pattern, log_tail, re.IGNORECASE):
            return hint
    return None


def _parse_coverage(
    output: str,
    *,
    total_regex: str = r"Coverage:\s*(\d+\.\d+)%",
    file_regex: str = r"^(\d+\.\d+)%\s+\d+/\d+\s+(.+)$",
) -> tuple[float | None, dict[str, float]]:
    total_coverage = None
    per_file_coverage: dict[str, float] = {}

    total_rx = re.compile(total_regex)
    file_rx = re.compile(file_regex)

    for line in output.splitlines():
        line = line.strip()

        match_total = total_rx.search(line)
        if match_total:
            total_coverage = float(match_total.group(1))

        match_file = file_rx.search(line)
        if match_file:
            coverage = float(match_file.group(1))
            file_path = match_file.group(2).strip()
            per_file_coverage[file_path] = coverage

    return total_coverage, per_file_coverage


def _auto_fix_strategies(
    config: ModuleConfig,
    module_path: Path,
    report: ModuleReport,
    phase: Literal["lint", "test", "build"],
) -> bool:
    if phase == "lint":
        strategies = config.auto_fix_lint
    elif phase == "test":
        strategies = config.auto_fix_test
    elif phase == "build":
        strategies = config.auto_fix_build
    else:
        strategies = []

    for cmd in strategies:
        desc = " ".join(cmd)
        print(f"[{config.name}] Attempting auto-fix: {desc}")
        if phase == "lint":
            report.lint_fixes.append(desc)
        elif phase == "test":
            report.test_fixes.append(desc)
        else:
            report.build_fixes.append(desc)
        res = _run(
            command=cmd,
            cwd=module_path,
            log_dir=module_path.parent / ".quality-verification" / "logs",
            label=f"{config.name}__{phase}_fix__{desc.replace(' ', '_')}",
        )
        if res.ok:
            return True

    return False


def _smart_retry_backoff(attempt: int, max_attempts: int) -> bool:
    if attempt >= max_attempts:
        return False

    if attempt == 1:
        return True

    wait_time = min(2 ** (attempt - 1), 10)
    print(f"[RETRY] Waiting {wait_time}s before attempt {attempt + 1}...")
    time.sleep(wait_time)
    return True


def _print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def _run_module_phase(
    config: ModuleConfig,
    module_path: Path,
    phase: Phase,
    project_root: Path,
    log_dir: Path,
    cache: dict[str, dict],
    dry_run: bool,
    max_iterations: int,
) -> ModuleReport:
    report = ModuleReport(name=config.name, path=str(module_path))
    report.hash = _compute_hash(module_path)
    report.coverage_exclusions = config.coverage_exclusions
    report.min_total_coverage = config.min_total_coverage
    report.min_file_coverage = config.min_file_coverage

    if not module_path.exists():
        print(f"[{config.name}] SKIP: {module_path} does not exist")
        report.skipped = True
        return report

    cache_key = f"{config.name}_{phase}_{report.hash}"
    if cache_key in cache and cache[cache_key]["status"] == "success":
        print(f"[{config.name}] CACHE HIT: skipping {phase} (no changes)")
        report.cache_hit = True
        if phase == "lint":
            report.lint_attempts.append(
                CommandResult(
                    command=config.lint_cmd,
                    cwd=str(module_path),
                    exit_code=0,
                    duration_s=0.0,
                    log_path="",
                )
            )
        else:
            report.test_attempts.append(
                CommandResult(
                    command=config.test_cmd,
                    cwd=str(module_path),
                    exit_code=0,
                    duration_s=0.0,
                    log_path="",
                )
            )
        return report

    if phase in ("lint", "all"):
        for attempt in range(1, max_iterations + 1):
            print(f"\n[{config.name}] {' '.join(config.lint_cmd)} (attempt {attempt})")
            res = _run(
                command=config.lint_cmd,
                cwd=module_path,
                log_dir=log_dir,
                label=f"{config.name}__lint__attempt_{attempt}",
                dry_run=dry_run,
            )
            report.lint_attempts.append(res)

            if res.exit_code == 0 and res.lint_issue_count == 0:
                changed = _git_changed_files(project_root)
                policy_findings = _policy_checks(config, module_path, project_root, changed)
                if policy_findings:
                    report.policy_violations = policy_findings
                    fake = CommandResult(
                        command=["policy", "checks"],
                        cwd=str(module_path),
                        exit_code=2,
                        duration_s=0.0,
                        log_path="",
                        stdout="\n".join([f"error: {m}" for m in policy_findings]),
                        stderr="",
                    )
                    report.lint_attempts.append(fake)
                cache[cache_key] = {"status": "success", "timestamp": time.time()}
                break

            if not _smart_retry_backoff(attempt, max_iterations):
                break

            did_fix = _auto_fix_strategies(config, module_path, report, "lint")
            if not did_fix:
                break

    if phase in ("test", "all"):
        for attempt in range(1, max_iterations + 1):
            print(f"\n[{config.name}] {' '.join(config.test_cmd)} (attempt {attempt})")
            env = dict(config.test_env) if config.test_env else None
            res = _run(
                command=config.test_cmd,
                cwd=module_path,
                log_dir=log_dir,
                label=f"{config.name}__test__attempt_{attempt}",
                dry_run=dry_run,
                env=env,
            )
            report.test_attempts.append(res)

            if not dry_run:
                # Generic coverage parsing: read a configured log path
                # (defaults to project_root/test.log for back-compat) and
                # extract total / per-file coverage with configurable regexes.
                if config.coverage_log_path:
                    log_path = Path(config.coverage_log_path)
                    if not log_path.is_absolute():
                        log_path = project_root / log_path
                else:
                    log_path = project_root / "test.log"
                tail = _read_tail(log_path)
                if tail:
                    total_coverage, per_file_coverage = _parse_coverage(
                        tail,
                        total_regex=config.coverage_total_regex,
                        file_regex=config.coverage_file_regex,
                    )
                    report.total_coverage = total_coverage
                    report.per_file_coverage = per_file_coverage

                    if total_coverage is not None:
                        print(f"\n[{config.name}] Total coverage: {total_coverage:.2f}%")
                        if total_coverage < report.min_total_coverage:
                            print(
                                f"[{config.name}] COVERAGE FAIL: Total coverage {total_coverage:.2f}% is below {report.min_total_coverage:.0f}% threshold"
                            )

                # Targeted coverage allowlist — runs only if the module
                # config has a `coverage_allowlist.command` to invoke.
                if (
                    config.coverage_allowlist
                    and config.coverage_allowlist.get("command")
                ):
                    cmd = list(config.coverage_allowlist["command"])
                    threshold = config.coverage_allowlist.get("threshold")
                    if threshold is not None:
                        cmd.append(str(int(threshold)))
                    print(
                        f"\n[{config.name}] Running targeted coverage check: {' '.join(cmd)}"
                    )
                    tgt_res = _run(
                        command=cmd,
                        cwd=module_path,
                        log_dir=log_dir,
                        label=f"{config.name}__targeted_coverage",
                    )
                    report.targeted_coverage_result = tgt_res
                    report.targeted_coverage_ok = tgt_res.ok
                    if not tgt_res.ok:
                        print(
                            f"[{config.name}] TARGETED COVERAGE FAIL: allowlist thresholds not met"
                        )

            if res.ok and report._coverage_ok():
                cache[cache_key] = {"status": "success", "timestamp": time.time()}
                break

            if not _smart_retry_backoff(attempt, max_iterations):
                break

            did_fix = _auto_fix_strategies(config, module_path, report, "test")
            if not did_fix:
                break

    if (
        config.coverage_cmd
        and phase in ("test", "all")
        and report.test_ok
        and not dry_run
    ):
        print(f"\n[{config.name}] Running coverage: {' '.join(config.coverage_cmd)}")
        coverage_res = _run(
            command=config.coverage_cmd,
            cwd=module_path,
            log_dir=log_dir,
            label=f"{config.name}__coverage",
        )
        report.coverage_result = coverage_res

    if config.build_cmd and phase in ("build", "all") and not dry_run:
        print(f"\n[{config.name}] Running build: {' '.join(config.build_cmd)}")
        for attempt in range(1, max_iterations + 1):
            print(f"\n[{config.name}] {' '.join(config.build_cmd)} (attempt {attempt})")
            build_res = _run(
                command=config.build_cmd,
                cwd=module_path,
                log_dir=log_dir,
                label=f"{config.name}__build__attempt_{attempt}",
            )
            report.build_attempts.append(build_res)

            if build_res.ok:
                cache[cache_key] = {"status": "success", "timestamp": time.time()}
                break

            if not _smart_retry_backoff(attempt, max_iterations):
                break

            did_fix = _auto_fix_strategies(config, module_path, report, "build")
            if not did_fix:
                break

    return report


def _summarize(reports: list[ModuleReport], *, project_root: Path) -> dict:
    # Coverage summary: take the first module that reports coverage.
    coverage_total = next(
        (r.total_coverage for r in reports if r.total_coverage is not None), None
    )
    coverage_targeted = next(
        (r.targeted_coverage_ok for r in reports if r.targeted_coverage_ok is not None),
        None,
    )
    summary: dict = {
        "project_root": str(project_root),
        "timestamp": time.time(),
        "modules": [r.to_dict() for r in reports],
        "summary": {
            "total_modules": len(reports),
            "skipped_modules": sum(1 for r in reports if r.skipped),
            "cache_hits": sum(1 for r in reports if r.cache_hit),
            "lint_passed": sum(1 for r in reports if r.lint_ok),
            "test_passed": sum(1 for r in reports if r.test_ok),
            "build_passed": sum(1 for r in reports if r.build_ok),
            "total_duration_s": sum(r.total_duration for r in reports),
            "coverage": {
                "total_coverage": coverage_total,
                "targeted_ok": coverage_targeted,
            },
        },
    }
    return summary


def _iter_candidate_files(root: Path, extra_ignores: list[str] | None = None) -> Iterable[Path]:
    default_ignores = [
        ".git",
        ".dart_tool",
        "build",
        "node_modules",
        ".venv",
        "venv",
        ".quality-verification",
        # Common build / state dirs that don't represent source code:
        "dist",
        ".next",
        ".turbo",
        ".cache",
        "coverage",
        ".nyc_output",
        ".omo",
        ".opencode",
    ]
    if extra_ignores:
        default_ignores = list(default_ignores) + list(extra_ignores)
    for f in root.rglob("*"):
        if not f.is_file():
            continue
        s = str(f)
        if any(x in s for x in default_ignores):
            continue
        yield f


def _read_text_safely(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _scan_secrets(root: Path, extra_ignores: list[str] | None = None) -> list[str]:
    patterns = [
        r"AKIA[0-9A-Z]{16}",
        r"ASIA[0-9A-Z]{16}",
        r"(?i)BEGIN\s+(RSA|EC|OPENSSH)?\s*PRIVATE\s+KEY",
        r"(?i)\bsecret[\s_:-]*(key|token|value)\b\s*[:=]\s*['\"][^'\"\n]+['\"]",
        r"(?i)\bapi[\s_:-]*key\b\s*[:=]\s*['\"][^'\"\n]+['\"]",
        r"(?i)\bpassword\b\s*[:=]\s*['\"][^'\"\n]+['\"]",
        r"(?i)\bclient[\s_:-]*secret\b\s*[:=]\s*['\"][^'\"\n]+['\"]",
        r"(?i)\baccess[\s_:-]*token\b\s*[:=]\s*['\"][^'\"\n]+['\"]",
    ]
    ignore_substrings = [".example", ".sample", "testdata", "fixtures"]
    compiled = [re.compile(p) for p in patterns]
    findings: list[str] = []
    for f in _iter_candidate_files(root, extra_ignores=extra_ignores):
        s = str(f)
        if any(x in s for x in ignore_substrings):
            continue
        text = _read_text_safely(f)
        if not text:
            continue
        for rx in compiled:
            if rx.search(text):
                findings.append(f"Secret-like content in {s}")
                break
    return findings


def _scan_iac(project_root: Path) -> list[str]:
    findings: list[str] = []
    iac_files = []
    for folder in ["supabase", "infra", "infrastructure", "."]:
        base = project_root / folder
        if not base.exists():
            continue
        for ext in ("*.tf", "*.yaml", "*.yml", "*.json"):
            iac_files.extend(list(base.rglob(ext)))
    risky = [
        (re.compile(r"0\.0\.0\.0/0"), "Wide-open CIDR 0.0.0.0/0"),
        (re.compile(r"(?i)public[-_]?read|public[-_]?write"), "Public ACL"),
        (re.compile(r"(?i)allowPrivilegeEscalation:\s*true"), "K8s privilege escalation enabled"),
        (re.compile(r"(?i)runAsUser:\s*0|runAsRoot:\s*true"), "K8s running as root"),
    ]
    for f in iac_files:
        s = _read_text_safely(f)
        if not s:
            continue
        for rx, msg in risky:
            if rx.search(s):
                findings.append(f"IaC risky pattern in {str(f)}: {msg}")
    return findings


def _scan_logging_secrets(root: Path, extra_ignores: list[str] | None = None) -> list[str]:
    findings: list[str] = []
    rx = re.compile(
        # Word-boundary match: a logging call followed (anywhere on the same
        # line) by a secret-like name AND an actual literal value (quotes
        # or backticks, 3+ chars). The earlier open-ended regex matched
        # benign usage like `console.log('cost=$0 tokens=1234')`.
        r"(?i)\b(log|logger|print|console\.log)\s*\([^)]*\b"
        r"(password|secret|token|api[_-]?key)\b\s*[=:]\s*['\"`][^'\"`\n]{3,}"
    )
    for f in _iter_candidate_files(root, extra_ignores=extra_ignores):
        text = _read_text_safely(f)
        if not text:
            continue
        if rx.search(text):
            findings.append(f"Potential secret logging in {str(f)}")
    return findings


def _backend_contract_changed(project_root: Path, changed: set[str] | None) -> bool:
    if changed is None:
        return True
    return any(p.startswith("backend/src/authorconsole_api/") for p in changed)


def _check_contract_first(project_root: Path, changed: set[str] | None) -> list[str]:
    if not _backend_contract_changed(project_root, changed):
        return []
    tests = list((project_root / "backend" / "tests").rglob("*.py"))
    has_contract = False
    for t in tests:
        txt = _read_text_safely(t)
        if "contract" in t.name.lower() or re.search(r"(?i)contract", txt):
            has_contract = True
            break
    return [] if has_contract else ["Backend API changes without contract tests detected"]


def _check_input_validation(project_root: Path) -> list[str]:
    routes_dir = project_root / "backend" / "src" / "authorconsole_api"
    if not routes_dir.exists():
        return []
    py_files = list(routes_dir.rglob("*.py"))
    uses_pydantic = False
    for f in py_files:
        txt = _read_text_safely(f)
        if re.search(r"from\s+pydantic\s+import\s+BaseModel|import\s+pydantic", txt):
            uses_pydantic = True
            break
    return [] if uses_pydantic else ["Backend routes lack explicit Pydantic validation imports"]


def _policy_checks(
    config: ModuleConfig,
    module_path: Path,
    project_root: Path,
    changed: set[str] | None,
) -> list[str]:
    flags = config.policy_checks or {}
    findings: list[str] = []
    if flags.get("secrets", True):
        findings.extend(_scan_secrets(project_root, extra_ignores=config.file_scan_ignores))
    if flags.get("log_secrets", True):
        findings.extend(
            _scan_logging_secrets(project_root, extra_ignores=config.file_scan_ignores)
        )
    if flags.get("iac", True):
        findings.extend(_scan_iac(project_root))
    if flags.get("pydantic", False):
        findings.extend(_check_input_validation(project_root))
    if flags.get("contract_first", False):
        findings.extend(_check_contract_first(project_root, changed))
    return findings


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="quality_verification.py",
        description="Run lint + tests for configured modules with parallel execution, caching, and smart auto-fixes.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=_default_project_root(),
        help="Project root directory (defaults to repo root inferred from script location).",
    )
    parser.add_argument(
        "--phase",
        choices=["lint", "test", "all"],
        default="all",
        help="Which phase(s) to run.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Max iterations per phase per module",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Optional path to write a JSON summary report.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would run without executing.",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run modules in parallel for faster execution.",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching and force fresh runs.",
    )
    parser.add_argument(
        "--modules",
        nargs="+",
        help="Specific modules to run (default: all configured modules).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    project_root: Path = args.root.resolve()
    log_dir = project_root / ".quality-verification" / "logs"
    phase: Phase = args.phase

    configs = _load_config(project_root)
    configs = [c for c in configs if c.enabled]

    if args.modules:
        configs = [c for c in configs if c.name in args.modules]

    if not configs:
        print("No modules configured or enabled.")
        return 0

    changed = _git_changed_files(project_root)
    changed_by_module: dict[str, bool] = {c.name: True for c in configs}
    if changed is not None and not args.no_cache:
        for c in configs:
            changed_by_module[c.name] = any(
                path == c.path or path.startswith(f"{c.path}/") for path in changed
            )

    cache = {} if args.no_cache else _load_cache(project_root)

    reports: list[ModuleReport] = []

    if args.parallel and not args.dry_run:
        _print_section(f"Running {len(configs)} modules in parallel")
        with ThreadPoolExecutor(max_workers=min(len(configs), 4)) as executor:
            futures = {}
            for config in configs:
                if not changed_by_module[config.name]:
                    reports.append(
                        ModuleReport(
                            name=config.name,
                            path=str(project_root / config.path),
                            skipped=True,
                        )
                    )
                    continue

                module_path = project_root / config.path
                future = executor.submit(
                    _run_module_phase,
                    config,
                    module_path,
                    phase,
                    project_root,
                    log_dir,
                    cache,
                    args.dry_run,
                    args.max_iterations,
                )
                futures[future] = config

            for future in as_completed(futures):
                report = future.result()
                reports.append(report)
                if not report.lint_ok or not report.test_ok:
                    for f in futures:
                        f.cancel()
    else:
        for config in configs:
            if not changed_by_module[config.name]:
                reports.append(
                    ModuleReport(
                        name=config.name,
                        path=str(project_root / config.path),
                        skipped=True,
                    )
                )
                continue

            module_path = project_root / config.path
            report = _run_module_phase(
                config,
                module_path,
                phase,
                project_root,
                log_dir,
                cache,
                args.dry_run,
                args.max_iterations,
            )
            reports.append(report)

            if report.lint_attempts and not report.lint_ok:
                last_lint = report.lint_attempts[-1]
                issue_count = last_lint.lint_issue_count
                print(
                    f"\n[{config.name}] LINT FAILED with {issue_count} issues. See log: {last_lint.log_path}"
                )
                tail = _read_tail(Path(last_lint.log_path), max_lines=40)
                hint = _detect_common_environment_issue(tail)
                if hint:
                    print(f"[{config.name}] Hint: {hint}")
                if not args.parallel:
                    return 1

            if phase in ("test", "all") and not report.test_ok:
                print(
                    f"\n[{config.name}] TESTS FAILED. See log: {report.test_attempts[-1].log_path}"
                )
                tail = _read_tail(Path(report.test_attempts[-1].log_path), max_lines=40)
                hint = _detect_common_environment_issue(tail)
                if hint:
                    print(f"[{config.name}] Hint: {hint}")
                if (
                    report.total_coverage is not None
                    and report.min_total_coverage > 0
                    and report.total_coverage < report.min_total_coverage
                ):
                    print(
                        f"[{config.name}] Total coverage {report.total_coverage:.2f}% is below {report.min_total_coverage:.0f}% threshold"
                    )
                low_count = sum(
                    1
                    for fp, c in report.per_file_coverage.items()
                    if c < report.min_file_coverage and not report._is_excluded(fp)
                )
                if low_count > 0:
                    print(
                        f"[{config.name}] {low_count} files below {report.min_file_coverage:.0f}% coverage threshold"
                    )
                if not args.parallel:
                    return 1

    if not args.dry_run and not args.no_cache:
        _save_cache(project_root, cache)

    _print_section("Summary")
    summary = _summarize(reports, project_root=project_root)
    for r in reports:
        if r.skipped:
            print(f"- {r.name}: SKIPPED (no git changes)")
        elif r.cache_hit:
            print(f"- {r.name}: CACHE HIT (unchanged)")
        else:
            lint_status = "OK" if r.lint_ok else "FAIL"
            test_status = "OK" if r.test_ok else "FAIL"
            duration = f"{r.total_duration:.1f}s"
            lint_issues = ""
            if r.lint_attempts and not r.lint_ok:
                issue_count = r.lint_attempts[-1].lint_issue_count
                lint_issues = f" ({issue_count} issues)"

            parts = [f"lint={lint_status}{lint_issues}"]
            if phase in ("test", "all"):
                parts.append(f"test={test_status}")
                if r.total_coverage is not None and r.min_total_coverage > 0:
                    coverage_status = (
                        "OK" if r.total_coverage >= r.min_total_coverage else "FAIL"
                    )
                    parts.append(f"coverage={coverage_status}")
                if r.min_file_coverage > 0 and r.per_file_coverage:
                    low_files = sum(
                        1
                        for fp, c in r.per_file_coverage.items()
                        if c < r.min_file_coverage and not r._is_excluded(fp)
                    )
                    if low_files > 0:
                        parts.append(f"files=FAIL ({low_files})")
            parts.append(f"time={duration}")
            print(f"- {r.name}: {', '.join(parts)}")

    print(f"\nTotal duration: {summary['summary']['total_duration_s']:.1f}s")
    print(
        f"Cache hits: {summary['summary']['cache_hits']}/{summary['summary']['total_modules']}"
    )

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"\nWrote JSON report: {args.json_out}")

    failed = any(
        not (r.lint_ok and r.test_ok) and not r.skipped and not r.cache_hit
        for r in reports
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
