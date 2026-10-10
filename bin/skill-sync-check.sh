#!/usr/bin/env bash
# ~/.agents/bin/skill-sync-check.sh
# Detect skill duplication drift between global hub and any project skills dir.
# Run from a project root that contains .agents/skills/.
#
# Exit codes:
#   0 — no drift (all matching skills are either symlinks or byte-identical)
#   1 — drift found (printed; not auto-fixed)
#   2 — usage error

set -euo pipefail

GLOBAL_DIR="${HOME}/.agents/skills"
PROJECT_DIR="${1:-${PWD}/.agents/skills}"

if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "no project skills dir at $PROJECT_DIR" >&2
  exit 2
fi

drift=0

# Compare every skill name that exists in both
for proj_skill in "$PROJECT_DIR"/*/; do
  [[ -L "$proj_skill" ]] && continue   # symlink — already resolves
  name="$(basename "$proj_skill")"
  global_skill="${GLOBAL_DIR}/${name}"
  [[ -d "$global_skill" ]] || continue  # project-only — skip

  # byte-by-byte compare, ignoring identical symlinks (which would just be the same target)
  if ! diff -rq "$proj_skill" "$global_skill" >/dev/null 2>&1; then
    echo "DRIFT: ${name}"
    echo "  global: $global_skill"
    echo "  project: $proj_skill"
    drift=1
  fi
done

if [[ "$drift" -eq 0 ]]; then
  echo "skill-sync-check: OK (no drift between $GLOBAL_DIR and $PROJECT_DIR)"
fi
exit $drift