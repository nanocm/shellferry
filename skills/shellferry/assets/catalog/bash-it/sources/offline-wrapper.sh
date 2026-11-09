#!/bin/bash
set -e
mkdir -p "$OFFLINE_PREFIX"
tar -xzf "$OFFLINE_ROOT/resources/bash-it-source.tar.gz" --strip-components=1 -C "$OFFLINE_PREFIX"
cp "$OFFLINE_ROOT/upstream/install.sh" "$OFFLINE_PREFIX/install.sh"
bash "$OFFLINE_PREFIX/install.sh" --silent --no-modify-config
