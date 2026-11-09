#!/bin/bash
set -euo pipefail
original_args=("$@")
while [ "$#" -gt 0 ]; do
  case "$1" in
    --version)
      [ "$#" -ge 2 ] && [ "$2" = 3.274.1 ] || { echo 'This offline bundle fixes Pulumi at 3.274.1; prepare a new bundle for another version.' >&2; exit 64; }
      shift 2
      ;;
    --install-root)
      [ "$#" -ge 2 ] && [ "$2" = "$OFFLINE_PREFIX" ] || { echo 'Set the installation directory using outer --prefix; conflicting --install-root is not supported.' >&2; exit 64; }
      shift 2
      ;;
    --silent|--no-edit-path) shift ;;
    *) echo "Unsupported installer argument: $1" >&2; exit 64 ;;
  esac
done
mkdir -p "$OFFLINE_PREFIX/bin"
bash "$OFFLINE_ROOT/upstream/install.sh" "${original_args[@]}"
export PATH="$OFFLINE_PREFIX/bin:$PATH"
"$OFFLINE_PREFIX/bin/pulumi" plugin install resource random 4.21.6 --exact --reinstall --file "$OFFLINE_ROOT/resources/pulumi-resource-random-v4.21.6-linux-amd64.tar.gz" --checksum d23098a615cd8590e026ec3d36c95f00617d93b0af14164162b81cf1af808174 --non-interactive
"$OFFLINE_PREFIX/bin/pulumi" gen-completion bash > "$OFFLINE_PREFIX/completion.bash"
{
  printf 'export PULUMI_HOME=%q
' "$OFFLINE_PREFIX"
  printf 'export PATH=%q:"$PATH"
' "$OFFLINE_PREFIX/bin"
  printf 'export PULUMI_SKIP_UPDATE_CHECK=true
'
  printf 'export PULUMI_DISABLE_AUTOMATIC_PLUGIN_ACQUISITION=true
'
  printf '. %q
' "$OFFLINE_PREFIX/completion.bash"
} > "$OFFLINE_PREFIX/env.sh"
