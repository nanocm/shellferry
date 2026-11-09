#!/bin/sh
set -eu
mkdir -p "$OFFLINE_PREFIX/bin"
export PATH="$OFFLINE_PREFIX/bin:$PATH"

if [ -f "$OFFLINE_PREFIX/bin/kustomize" ]; then
  "$OFFLINE_PREFIX/bin/kustomize" version | grep -q v5.8.3 || exit 1
  exit 0
fi
bash "$OFFLINE_ROOT/upstream/install.sh" "$@"

