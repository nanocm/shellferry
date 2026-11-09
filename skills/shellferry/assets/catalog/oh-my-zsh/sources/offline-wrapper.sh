#!/bin/sh
set -eu
if [ "${1:-}" = --verify-existing ]; then
  test "$(cat "$ZSH/.shellferry-source")" = "cca3bdfbef8c52ef8939ce7911ff68852b949daa"
  test -f "$ZSH/oh-my-zsh.sh"
  exit 0
fi
sh "$OFFLINE_ROOT/upstream/install.sh" --unattended
printf '%s\n' "cca3bdfbef8c52ef8939ce7911ff68852b949daa" > "$ZSH/.shellferry-source"
