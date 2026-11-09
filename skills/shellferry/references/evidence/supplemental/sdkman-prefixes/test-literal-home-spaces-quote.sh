#!/bin/sh
set -eu
export HOME=/tmp/offline-home
mkdir -p "$HOME" /tmp/guards
cp -R /bundle /tmp/package
chmod -R u+w /tmp/package
cd /tmp/package
prefix='/tmp/offline-home/literal $HOME  user'"'"'s sdk'
# Expose accidental downloads even when the upstream installer ignores their failure.
cat > /tmp/guards/network-block <<'GUARD'
#!/bin/sh
printf '%s\n' "$0 $*" >> /tmp/network-attempts
echo 'An unconverted network command was called' >&2
exit 97
GUARD
chmod +x /tmp/guards/network-block
for cmd in curl wget fetch aria2c; do ln -s network-block "/tmp/guards/$cmd"; done
export PATH="/tmp/guards:$PATH"
sh install.sh --prefix "$prefix" --check
[ ! -e "$prefix" ]
sh install.sh --prefix "$prefix"
sh smoke.sh "$prefix"
cat "$HOME/.bashrc"
[ ! -e /tmp/network-attempts ] || { cat /tmp/network-attempts >&2; exit 97; }
# Re-run installation to verify the actual upstream update/idempotence behavior.
sh repeat.sh "$prefix"
sh smoke.sh "$prefix"
cat "$HOME/.bashrc"
[ ! -e /tmp/network-attempts ] || { cat /tmp/network-attempts >&2; exit 97; }
printf '\nOFFLINE_INSTALL_TEST_PASS\n'
