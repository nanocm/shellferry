#!/bin/sh
set -eu
if [ "${1:-}" = --verify-existing ]; then test "$(cat "$PYENV_ROOT/.shellferry-source")" = "9e40c078c0f86eae0d96e114269e934681745625"; "$PYENV_ROOT/bin/pyenv" --version; exit 0; fi
bash "$OFFLINE_ROOT/upstream/install.sh"
printf '%s\n' "9e40c078c0f86eae0d96e114269e934681745625" > "$PYENV_ROOT/.shellferry-source"
