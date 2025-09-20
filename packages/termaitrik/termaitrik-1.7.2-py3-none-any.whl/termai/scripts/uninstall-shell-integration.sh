#!/usr/bin/env bash
set -euo pipefail

BLOCK_START="# >>> termai integration >>>"
BLOCK_END="# <<< termai integration <<<"

remove_block() {
  local rc="$1"
  if [ -f "$rc" ]; then
    local removed=0
    if grep -q "$BLOCK_START" "$rc"; then
      # Remove the standard marked block
      sed -i.bak "/$BLOCK_START/,/$BLOCK_END/d" "$rc" && removed=1
    fi
    # Also remove any legacy blocks that contain literal '$BLOCK_START'/'$BLOCK_END'
    if grep -q '^\$BLOCK_START$' "$rc"; then
      sed -i.bak '/^\$BLOCK_START$/,/^\$BLOCK_END$/d' "$rc" && removed=1
    fi
    if [ $removed -eq 1 ]; then
      echo "Removed TermAI integration from $rc."
    else
      echo "No TermAI integration block found in $rc."
    fi
  fi
}

remove_block "$HOME/.bashrc"
remove_block "$HOME/.zshrc"
remove_block "$HOME/.config/fish/config.fish"

# Remove any fish autoloaded function definition file
FISH_FUNC_DIR="$HOME/.config/fish/functions"
if [ -d "$FISH_FUNC_DIR" ] && [ -f "$FISH_FUNC_DIR/ai.fish" ]; then
  rm -f "$FISH_FUNC_DIR/ai.fish"
  echo "Removed fish autoload function: $FISH_FUNC_DIR/ai.fish"
fi

echo "Done. Reopen your shell to apply changes."
