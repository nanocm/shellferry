#!/bin/sh
set -eu
mkdir -p "$OFFLINE_PREFIX/bin"
export PATH="$OFFLINE_PREFIX/bin:$PATH"

bash "$OFFLINE_ROOT/upstream/install.sh" "$@"

