#!/bin/sh
set -e
mkdir -p "$OFFLINE_PREFIX/bin"
export PATH="$OFFLINE_PREFIX/bin:$PATH"
sh "$OFFLINE_ROOT/upstream/install.sh" "$@"
