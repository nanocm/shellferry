#!/bin/sh
set -eu
mkdir -p "$OFFLINE_PREFIX/bin"
printf '%s\n' "$OFFLINE_PREFIX/bin" | sh "$OFFLINE_ROOT/upstream/install.sh" --version 2.6.1
