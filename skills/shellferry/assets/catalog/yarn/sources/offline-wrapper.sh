#!/bin/bash
set -e
offline_yarn_tarballs() {
  [ "$1" = -o ] || return 64
  local dest="${2%\#1}"
  local url="${3%\{,.asc\}}"
  offline_fetch "$url" "$dest" && offline_fetch "$url.asc" "$dest.asc"
}
export -f offline_yarn_tarballs
mkdir -p "$OFFLINE_PREFIX/runtime"
tar -xJf "$OFFLINE_ROOT/resources/node-v22.15.0-linux-x64.tar.xz" --strip-components=1 -C "$OFFLINE_PREFIX/runtime"
export PATH="$OFFLINE_PREFIX/runtime/bin:$OFFLINE_PREFIX/yarn/bin:$PATH"
exec bash "$OFFLINE_ROOT/upstream/install.sh" --version 1.22.22
