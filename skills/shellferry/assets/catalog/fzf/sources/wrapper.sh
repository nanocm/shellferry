#!/bin/sh
set -eu
mkdir -p "$OFFLINE_PREFIX"
tar -xzf "$OFFLINE_ROOT/resources/fzf-source.tar.gz" --strip-components=1 -C "$OFFLINE_PREFIX"
cp "$OFFLINE_ROOT/upstream/install.sh" "$OFFLINE_PREFIX/install"
bash "$OFFLINE_PREFIX/install" --all --no-update-rc --no-zsh --no-fish --no-nushell
