#!/bin/bash
set -e
if [ "${1:-}" = --verify-existing ]; then test "$(cat "$BASHER_ROOT/.shellferry-source")" = "7c3d238ce263856edbb99fee000613c01ba5712d"; exit 0; fi
touch "$HOME/.bashrc"
bash "$OFFLINE_ROOT/upstream/install.sh"
printf '%s\n' "7c3d238ce263856edbb99fee000613c01ba5712d" > "$BASHER_ROOT/.shellferry-source"
