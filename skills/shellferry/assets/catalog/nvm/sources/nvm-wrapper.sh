#!/bin/bash
set -e
mkdir -p "$NVM_DIR" "$OFFLINE_PREFIX/bin"
bash "$OFFLINE_ROOT/upstream/install.sh"
node_home="$NVM_DIR/versions/node/v26.13.0"
mkdir -p "$node_home"
tar -xzf "$OFFLINE_ROOT/resources/node-v26.13.0-linux-x64.tar.gz" --strip-components=1 -C "$node_home"
runtime_tmp=$(mktemp -d)
dpkg-deb -x "$OFFLINE_ROOT/resources/libatomic1_16-20260322-1ubuntu1_amd64.deb" "$runtime_tmp"
mkdir -p "$node_home/lib/offline-runtime"
cp -P "$runtime_tmp"/usr/lib/x86_64-linux-gnu/libatomic.so.1* "$node_home/lib/offline-runtime/"
rm -rf "$runtime_tmp"
mv -f "$node_home/bin/node" "$node_home/bin/node.real"
cat > "$node_home/bin/node" <<'NODE_WRAPPER'
#!/bin/sh
node_directory=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
export LD_LIBRARY_PATH="$node_directory/../lib/offline-runtime${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec "$node_directory/node.real" "$@"
NODE_WRAPPER
chmod +x "$node_home/bin/node"
. "$NVM_DIR/nvm.sh"
nvm alias default v26.13.0
nvm use v26.13.0
"$node_home/bin/node" -e 'console.log("offline node works")'
