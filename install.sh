#!/usr/bin/env bash
# ================================================================== ==
# install.sh — Install the Major agent system across OpenCode/VSCode
# Idempotent: safe to re-run after editing files in ~/.agents/
# ================================================================== ==

set -euo pipefail

AGENTS_DIR="${HOME}/.agents"
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
  err "Source directory ${AGENTS_DIR} does not exist."
  err "Clone or copy the agent system to ${AGENTS_DIR} first."
  exit 1
fi

# ----- 1. OpenCode integration ----------------------------------- --

log "=== OpenCode integration ==="
mkdirp "${OPENCODE_DIR}/agent"
mkdirp "${OPENCODE_DIR}/subagent"

# Major agent
link "${AGENTS_DIR}/opencode/agent/major.md" "${OPENCODE_DIR}/agent/major.md"

# Subagents
for sub in architect coder debugger reviewer researcher tester doc-writer; do
  src="${AGENTS_DIR}/opencode/subagent/${sub}.md"
  if [[ ! -f "$src" ]]; then
    warn "missing subagent file: ${src} — skipping"
    continue
  fi
  link "$src" "${OPENCODE_DIR}/subagent/${sub}.md"
done

info "OpenCode: $(ls "${OPENCODE_DIR}/agent/" 2>/dev/null | wc -l | tr -d ' ') agents, $(ls "${OPENCODE_DIR}/subagent/" 2>/dev/null | wc -l | tr -d ' ') subagents"
info "Switch to Major via /agents → 'major', or set as default in opencode.json"

# Portable roles. Existing OpenCode roles remain authoritative; these
# roles are loaded into OpenCode only — Claude integration removed
# (Claude retired 2026-10).
log "=== Portable role integration ==="
mkdirp "${AGENTS_DIR}/agents"
for role in laptop-admin software-maintainer; do
  src="${AGENTS_DIR}/agents/${role}.md"
  [[ -f "$src" ]] || { warn "missing portable role: ${src} — skipping"; continue; }
  link "$src" "${OPENCODE_DIR}/subagent/${role}.md"
done

# VS Code Copilot discovery layer: each role file in opencode/subagent/
# or agents/ becomes a symlink at ~/.copilot/agents/<name>.agent.md
# so VS Code Copilot's chat dropdown shows the agent. The role file
# already has dual-consumer YAML frontmatter (OpenCode + Copilot).
log "=== Copilot agent discovery layer ==="
mkdirp "${HOME}/.copilot/agents"
for src in "${AGENTS_DIR}"/opencode/subagent/*.md "${AGENTS_DIR}"/agents/*.md; do
  [[ -f "$src" ]] || continue
  name="$(basename "${src%.md}")"
  link "$src" "${HOME}/.copilot/agents/${name}.agent.md"
done
# major.agent.md is a real file (Major is Copilot-only); only create
# it if the user hasn't placed one already.
if [[ ! -e "${HOME}/.copilot/agents/major.agent.md" ]]; then
  warn "no ~/.copilot/agents/major.agent.md — pick a chat agent from the dropdown until you create one"
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
info "Major agent system installed:"
echo "  ~/.agents/                          ← source of truth"
echo "  ~/.config/opencode/agent/major.md   ← OpenCode (native multi-agent)"
echo "  ~/.config/opencode/subagent/*.md    ← OpenCode subagents (incl. portable roles)"
echo "  ~/.copilot/agents/*.agent.md         ← VS Code Copilot agents (symlinks to L1 + major.agent.md)"
echo "  ~/AGENTS.md                         ← pi / Codex / Gemini / Copilot (auto-discovered)"
echo "  ~/.agents/mcp/*.md                  ← Shared tool-specific instructions (e.g. codebase-memory)"
echo
info "Edit routing rules: ~/.agents/route.yaml"
info "Edit agent behavior: ~/.agents/opencode/agent/major.md"
info "Full docs: ~/.agents/README.md"
info "Verify integrations: ~/.agents/bin/verify-global-agents"
echo
log "Done. Re-run this script any time you edit files in ~/.agents/"

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
