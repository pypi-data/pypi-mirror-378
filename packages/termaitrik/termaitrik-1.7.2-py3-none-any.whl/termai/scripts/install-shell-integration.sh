#!/usr/bin/env bash
set -euo pipefail

# Determine repository root candidate (one level up from this script's directory)
# NOTE: When this script is run from an installed package (site-packages/termai/scripts),
# ".." will resolve to site-packages/termai which is NOT a project root. We'll validate below.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Resolve a usable repo path (one that contains pyproject.toml or setup.py). Traverse up to 3 levels.
resolve_repo() {
    local cand="$1"
    local i
    for i in 1 2 3; do
        if [ -f "$cand/pyproject.toml" ] || [ -f "$cand/setup.py" ]; then
            echo "$cand"; return 0
        fi
        # Stop at filesystem root
        if [ "$cand" = "/" ]; then break; fi
        cand="$(cd "$cand/.." && pwd)"
    done
    echo ""
}

DEFAULT_REPO="$(resolve_repo "$REPO_DIR")"

# Optional explicit shell override via --shell <name> or TERMAI_SHELL env
SHELL_OVERRIDE="${TERMAI_SHELL:-}"
if [ "${1:-}" = "--shell" ] && [ -n "${2:-}" ]; then
    SHELL_OVERRIDE="$2"; shift 2
fi

detect_shell() {
    if [ -n "$SHELL_OVERRIDE" ]; then
        echo "$SHELL_OVERRIDE"; return 0
    fi
    # Prefer $SHELL env if it exists (e.g. /usr/local/bin/fish)
    local base="${SHELL##*/}"
    case "$base" in
        fish) echo fish; return 0 ;;
        zsh) echo zsh; return 0 ;;
        bash) echo bash; return 0 ;;
    esac
    # Fall back to version variables (script might be run under a different interpreter)
    if [ -n "${ZSH_VERSION-}" ]; then echo zsh; return 0; fi
    # If BASH_VERSION is set but $SHELL points to fish, treat as fish
    if [ -n "${BASH_VERSION-}" ]; then
        if command -v fish >/dev/null 2>&1 && ps -p "${PPID}" -o comm= 2>/dev/null | grep -qi fish; then
            echo fish; return 0
        fi
        echo bash; return 0
    fi
    if command -v fish >/dev/null 2>&1; then echo fish; return 0; fi
    echo bash
}

SHELL_TYPE="$(detect_shell)"

case "$SHELL_TYPE" in
    fish) RC_FILE="$HOME/.config/fish/config.fish" ;;
    zsh) RC_FILE="$HOME/.zshrc" ;;
    bash) RC_FILE="$HOME/.bashrc" ;;
    *) echo "Shell non supportata ($SHELL_TYPE). Configura manualmente l'alias 'ai'." >&2; exit 1 ;;
esac

echo "Detected shell: $SHELL_TYPE. Installing into: $RC_FILE (repo: ${DEFAULT_REPO:-none})"

mkdir -p "$(dirname "$RC_FILE")"
touch "$RC_FILE"

BLOCK_START="# >>> termai integration >>>"
BLOCK_END="# <<< termai integration <<<"

# Remove previous block
if grep -q "$BLOCK_START" "$RC_FILE"; then
    sed -i.bak "/$BLOCK_START/,/$BLOCK_END/d" "$RC_FILE"
fi

# Also remove any legacy blocks that contain literal '$BLOCK_START'/'$BLOCK_END'
if grep -q '^\$BLOCK_START$' "$RC_FILE"; then
    sed -i.bak '/^\$BLOCK_START$/,/^\$BLOCK_END$/d' "$RC_FILE"
fi

if [ "$SHELL_TYPE" = "fish" ]; then
    # Fish function: ONLY run via uvx from PyPI (auto-update, no local/package conflicts)
    # Write start marker, then function body via single-quoted heredoc (no expansion), then end marker.
    echo "$BLOCK_START" >> "$RC_FILE"
    cat >> "$RC_FILE" <<'EOF'
function ai
    # Run the published package via uvx, forcing latest and refreshing cache
    # Use python -m termai.cli within the uvx environment to avoid any global 'termai' collisions
    uvx --isolated --refresh --from termaitrik@latest python -m termai.cli $argv; and return $status

    # If uvx is not installed, print a helpful message and return failure
    echo "[TermAI] 'uvx' non trovato. Installa uv da https://docs.astral.sh/uv/getting-started/ e riprova." >&2
    return 127
end
EOF
    echo "$BLOCK_END" >> "$RC_FILE"
else
    # For bash/zsh block, also prevent premature expansion of $@ during installation time
    echo "$BLOCK_START" >> "$RC_FILE"
    cat >> "$RC_FILE" <<'EOF'
ai() {
    # Run the published package via uvx (force latest and refresh cache); never from local repo
    uvx --isolated --refresh --from termaitrik@latest python -m termai.cli "$@" && return $?

    # If uvx is not installed, print a helpful message and return failure
    echo "[TermAI] 'uvx' non trovato. Installa uv da https://docs.astral.sh/uv/getting-started/ e riprova." >&2
    return 127
}
EOF
    echo "$BLOCK_END" >> "$RC_FILE"
fi

echo "Installed alias 'ai' -> uvx termaitrik@latest (python -m termai.cli), no local fallbacks. Reopen the shell or run: source '$RC_FILE'"
