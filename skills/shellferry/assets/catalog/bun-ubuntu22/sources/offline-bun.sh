#!/bin/sh
set -eu

# Bootstrap unzip privately from the bundled, verified Ubuntu packages.
# No package is installed into the system and no elevation is requested.
tools=$(mktemp -d "${TMPDIR:-/tmp}/bun-offline-tools.XXXXXXXX")
trap 'rm -rf -- "$tools"' 0
trap 'exit 130' 1 2 15
dpkg-deb -x "$OFFLINE_ROOT/resources/unzip_6.0-26ubuntu3.2_amd64.deb" "$tools/root"
dpkg-deb -x "$OFFLINE_ROOT/resources/libbz2-1.0_1.0.8-5ubuntu0.1_amd64.deb" "$tools/root"
mkdir -p "$tools/bin"
cat > "$tools/bin/unzip" <<'UNZIP'
#!/bin/sh
set -eu
# The private library search path affects only the temporary unzip process.
LD_LIBRARY_PATH="$BUN_OFFLINE_TOOLS/root/lib/x86_64-linux-gnu:$BUN_OFFLINE_TOOLS/root/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
  exec "$BUN_OFFLINE_TOOLS/root/usr/bin/unzip" "$@"
UNZIP
chmod 755 "$tools/bin/unzip"
export BUN_OFFLINE_TOOLS="$tools"
export PATH="$tools/bin:$PATH"
export SHELL=${SHELL:-/bin/bash}

bash "$OFFLINE_ROOT/upstream/install.sh" "$@"
