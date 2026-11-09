#!/bin/sh
set -eu
d=$(mktemp -d)
trap 'rm -rf "$d"' EXIT
tar -xzf "$OFFLINE_ROOT/resources/bats-source.tar.gz" --strip-components=1 -C "$d"
cp "$OFFLINE_ROOT/upstream/install.sh" "$d/install.sh"
bash "$d/install.sh" "$OFFLINE_PREFIX"
