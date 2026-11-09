#!/bin/bash
set -euo pipefail
if [ "${1:-}" = --reinitialize ]; then
  [ "$#" -eq 1 ] || { echo '--reinitialize accepts no other arguments' >&2; exit 64; }
  "$OFFLINE_PREFIX/google-cloud-sdk/bin/gcloud" version | grep -Fx 'Google Cloud SDK 592.0.0'
  "$OFFLINE_PREFIX/google-cloud-sdk/install.sh" --quiet --usage-reporting=false --command-completion=true --path-update=true --rc-path="$HOME/.bashrc"
else
  bash "$OFFLINE_ROOT/upstream/bootstrap.sh" --disable-prompts --install-dir "$OFFLINE_PREFIX" "$@"
fi
mkdir -p "$OFFLINE_PREFIX/bin"
for tool in gcloud bq gsutil; do
  ln -sf "$OFFLINE_PREFIX/google-cloud-sdk/bin/$tool" "$OFFLINE_PREFIX/bin/$tool"
done
