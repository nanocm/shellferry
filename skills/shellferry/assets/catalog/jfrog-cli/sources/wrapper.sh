#!/bin/sh
set -eu
mkdir -p "$OFFLINE_PREFIX/bin"
export PATH="$OFFLINE_PREFIX/bin:$PATH"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cd "$work"
sh "$OFFLINE_ROOT/upstream/install.sh" "$@"

