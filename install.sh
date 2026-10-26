#!/usr/bin/env bash
# ================================================================== ==
# install.sh — Install the agents hub (skills-first) across OpenCode/VSCode
# Idempotent: safe to re-run after editing files in ~/.agents/
# ================================================================== ==

set -euo pipefail

AGENTS_DIR="${HOME}/.agents"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCODE_DIR="${HOME}/.config/opencode"
VSCODE_DIR="${HOME}/.vscode"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log()  { echo -e "${GREEN}[install]${NC} $*"; }
warn() { echo -e "${YELLOW}[warn]${NC} $*"; }
err()  { echo -e "${RED}[error]${NC} $*" >&2; }
info() { echo -e "${BLUE}[info]${NC} $*"; }

# ----- helpers --------------------------------------------------- --

# Create a symlink, replacing existing one if broken or stale
link() {
  local src="$1" dst="$2"
  if [[ -L "$dst" ]]; then
    local current
    current="$(readlink "$dst")"
    if [[ "$current" == "$src" ]]; then
      info "already linked: ${dst} → ${src}"
      return 0
    fi
    warn "replacing existing symlink: ${dst} (was → ${current})"
    rm "$dst"
  elif [[ -e "$dst" ]]; then
    warn "${dst} exists and is not a symlink. Backing up to ${dst}.bak"
    mv "$dst" "${dst}.bak"
  fi
  ln -s "$src" "$dst"
  log "linked: ${dst} → ${src}"
}

mkdirp() {
  local dir="$1"
  if [[ ! -d "$dir" ]]; then
    mkdir -p "$dir"
    log "created dir: ${dir}"
  fi
}

# ----- preflight ------------------------------------------------- --

if [[ ! -d "$AGENTS_DIR" ]]; then
  if [[ "$SCRIPT_DIR" != "$AGENTS_DIR" && -f "${SCRIPT_DIR}/route.yaml" ]]; then
    # Bootstrap: this script runs from a checkout elsewhere — install it.
    log "bootstrapping ${AGENTS_DIR} from ${SCRIPT_DIR}"
    if command -v rsync >/dev/null 2>&1; then
      rsync -a "${SCRIPT_DIR}/" "${AGENTS_DIR}/"
    else
      cp -R "${SCRIPT_DIR}/." "${AGENTS_DIR}/"
    fi
    log "hub installed to ${AGENTS_DIR} (git history included)"
  else
    err "Source directory ${AGENTS_DIR} does not exist."
    err "Copy the agents-system checkout to ${AGENTS_DIR}, or run this"
    err "script from inside that checkout, then re-run."
    exit 1
  fi
fi

# ----- 1. OpenCode integration ----------------------------------- --

log "=== OpenCode integration ==="
mkdirp "${OPENCODE_DIR}/agent"
mkdirp "${OPENCODE_DIR}/agents"

# Major agent
link "${AGENTS_DIR}/opencode/agent/major.md" "${OPENCODE_DIR}/agent/major.md"

# Spawn roles (the only subagents — skills carry the knowledge).
# OpenCode scans agent/ and agents/, NOT subagent/ — roles linked
# into subagent/ were silently invisible to the Task tool.
for sub in researcher reviewer; do
  src="${AGENTS_DIR}/opencode/subagent/${sub}.md"
  if [[ ! -f "$src" ]]; then
    warn "missing spawn role file: ${src} — skipping"
    continue
  fi
  link "$src" "${OPENCODE_DIR}/agents/${sub}.md"
done

# Prune broken agent symlinks (roles retired in the skills-first redesign)
for dst in "${OPENCODE_DIR}/agents/"*.md "${OPENCODE_DIR}/agent/"*.md; do
  [[ -L "$dst" && ! -e "$dst" ]] && { rm "$dst"; warn "pruned broken symlink: ${dst}"; }
done

# Remove the old subagent/ dir — OpenCode never scanned it.
if [[ -d "${OPENCODE_DIR}/subagent" ]]; then
  rm -f "${OPENCODE_DIR}/subagent/"*.md
  rmdir "${OPENCODE_DIR}/subagent" 2>/dev/null \
    && info "removed stale ${OPENCODE_DIR}/subagent (never scanned by OpenCode)"
fi

info "OpenCode: $(ls "${OPENCODE_DIR}/agent/" 2>/dev/null | wc -l | tr -d ' ') agents, $(ls "${OPENCODE_DIR}/agents/" 2>/dev/null | wc -l | tr -d ' ') spawn roles"
info "Switch to Major via /agents → 'major', or set as default in opencode.json"

# VS Code Copilot discovery layer: each spawn role file in
# copilot/agents/ becomes a symlink at ~/.copilot/agents/<name>.agent.md
# so VS Code Copilot's chat dropdown shows it. Copilot and OpenCode
# disagree on frontmatter dialect (tools array vs object, model names
# vs provider/model-id), so each surface needs its own file.
log "=== Copilot agent discovery layer ==="
mkdirp "${HOME}/.copilot/agents"
for src in "${AGENTS_DIR}"/copilot/agents/*.agent.md; do
  [[ -f "$src" ]] || continue
  name="$(basename "$src")"
  link "$src" "${HOME}/.copilot/agents/${name}"
done
# Prune broken Copilot symlinks that pointed at retired hub role files
# (leave non-hub files like gsd-*.agent.md untouched)
for dst in "${HOME}/.copilot/agents/"*.agent.md; do
  [[ -L "$dst" && ! -e "$dst" ]] && { rm "$dst"; warn "pruned broken symlink: ${dst}"; }
done
# major.agent.md is a real file seeded from the repo template
# (~/.agents/copilot/major.agent.md) on first install. An existing
# file is left untouched — users may have customized it.
if [[ ! -e "${HOME}/.copilot/agents/major.agent.md" ]]; then
  if [[ -f "${AGENTS_DIR}/copilot/major.agent.md" ]]; then
    cp "${AGENTS_DIR}/copilot/major.agent.md" \
       "${HOME}/.copilot/agents/major.agent.md"
    log "seeded ~/.copilot/agents/major.agent.md from repo template"
  else
    warn "no ${AGENTS_DIR}/copilot/major.agent.md template; create the file manually"
  fi
else
  info "major.agent.md present (left untouched; template: ${AGENTS_DIR}/copilot/major.agent.md)"
fi

# ----- 2. VSCode + Copilot integration --------------------------- --

log "=== VSCode + Copilot integration ==="

# ~/AGENTS.md — many Copilot versions auto-discover this
link "${AGENTS_DIR}/AGENTS.md" "${HOME}/AGENTS.md"

# Per-project template: copy (not symlink) so projects can be self-contained
# This creates a ready-to-copy template in the agents dir
template="${AGENTS_DIR}/copilot/copilot-instructions.md"
if [[ -f "$template" ]]; then
  info "Copilot template ready: ${template}"
  info "  To use per-project: cp ${template} <project>/.github/copilot-instructions.md"
  info "  To use globally: see ${template} for VSCode settings snippet"
fi

# ----- 3. Summary ------------------------------------------------ --

log "=== Summary ==="
echo
info "Agents hub installed (skills-first):"
echo "  ~/.agents/                          ← source of truth"
echo "  ~/.agents/skills/                   ← dispatch layer (route.yaml → dispatch.skill)"
echo "  ~/.config/opencode/agent/major.md   ← OpenCode entry point"
echo "  ~/.config/opencode/agents/*.md     ← 2 spawn roles (researcher, reviewer)"
echo "  ~/.copilot/agents/*.agent.md         ← VS Code Copilot (major + 2 spawn-role symlinks)"
echo "  ~/AGENTS.md                         ← pi / Codex / Gemini / Copilot (auto-discovered)"
echo "  ~/.agents/mcp/*.md                  ← Shared tool-specific instructions (e.g. codebase-memory)"
echo
info "Edit routing rules: ~/.agents/route.yaml"
info "Edit agent behavior: ~/.agents/opencode/agent/major.md"
info "Full docs: ~/.agents/README.md"
info "Verify integrations: ~/.agents/bin/verify-global-agents"
echo
log "Done. Re-run this script any time you edit files in ~/.agents/"

# ----- 4. Git hooks (repo-local) ---------------------------------- --

log "=== Git hooks ==="
if [[ -d "${AGENTS_DIR}/.git" ]]; then
  (cd "${AGENTS_DIR}" && git config core.hooksPath .githooks)
  log "core.hooksPath → .githooks (pre-commit runs bin/test-hub)"
else
  info "${AGENTS_DIR} is not a git checkout; skipping git hooks"
fi

# ----- 5. CLI tool wrappers -------------------------------------- --

log "=== CLI tool wrappers ==="
AGENTS_BIN="${AGENTS_DIR}/bin"
if [[ -d "$AGENTS_BIN" ]]; then
    # Primary: symlink into ~/.local/bin (already on PATH, user-writable)
    if [[ -d "${HOME}/.local/bin" ]]; then
        for tool in "$AGENTS_BIN"/*; do
            [[ -f "$tool" ]] || continue
            name="$(basename "$tool")"
            link "$tool" "${HOME}/.local/bin/${name}"
        done
    else
        warn "${HOME}/.local/bin does not exist; skipping primary wrapper install"
    fi
    # Secondary: remind user to add ~/.agents/bin to PATH (for direct invocation)
    if ! echo "${PATH:-}" | grep -q "${AGENTS_BIN}"; then
        info "Also consider adding ${AGENTS_BIN} to your shell PATH for direct invocation."
        info "  zsh: add 'export PATH=\"${AGENTS_BIN}:\$PATH\"' to ~/.zprofile"
    fi
else
    info "no ${AGENTS_BIN}/ directory; nothing to wrap"
fi
