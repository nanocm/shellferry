#!/bin/sh
set -eu
export HOME=/tmp/edge-home
mkdir -p "$HOME" /tmp/guards
cp -R /bundle /tmp/edge-package
chmod -R u+w /tmp/edge-package
cat > /tmp/guards/network-block <<'GUARD'
#!/bin/sh
printf '%s\n' "$0 $*" >> /tmp/network-attempts
exit 97
GUARD
chmod +x /tmp/guards/network-block
for cmd in curl wget fetch aria2c; do ln -s network-block "/tmp/guards/$cmd"; done
export PATH="/tmp/guards:$PATH"
prefix="$HOME/prefix with spaces"
sh /tmp/edge-package/install.sh --prefix "$prefix" -- --dry-run
test ! -e "$prefix"
test ! -e "$HOME/.cache"
mkdir -p "$HOME/.cache/code-server"
printf 'not the pinned release\n' > "$HOME/.cache/code-server/code-server-4.145.2-linux-amd64.tar.gz"
sh /tmp/edge-package/install.sh --prefix "$prefix"
cmp "$HOME/.cache/code-server/code-server-4.145.2-linux-amd64.tar.gz" /tmp/edge-package/resources/code-server-4.145.2-linux-amd64.tar.gz
"$prefix/bin/code-server" --version | grep '^4.145.2 '
test ! -e /tmp/network-attempts
printf 'DRY_RUN_AND_CACHE_REPLACEMENT_PASS\n'
