#!/bin/bash
set -e
offline_bpkg_checkout() { mkdir -p "$1"; tar -xzf "$OFFLINE_ROOT/resources/bpkg-source.tar.gz" --strip-components=1 -C "$1"; }
export -f offline_bpkg_checkout
exec bash "$OFFLINE_ROOT/upstream/install.sh"
