#!/bin/sh
set -e
mkdir -p "$OFFLINE_PREFIX/bin"
export PATH="$OFFLINE_PREFIX/bin:$PATH"
bash "$OFFLINE_ROOT/upstream/install.sh" "$@" || {
  status=$?
  if [ "$status" -eq 3 ] && [ "$("$OFFLINE_PREFIX/bin/rclone" version | head -n 1)" = "rclone v1.76.0" ]; then
    exit 0
  fi
  exit "$status"
}
