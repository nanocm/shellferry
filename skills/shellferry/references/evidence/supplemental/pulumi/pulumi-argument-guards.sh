#!/bin/bash
set -euo pipefail
export HOME=/tmp/clean-home
mkdir -p "$HOME" /tmp/guards
cat > /tmp/guards/pulumi <<'OLD'
#!/bin/sh
echo old-pulumi-ran > /tmp/old-pulumi-ran
exit 98
OLD
cat > /tmp/guards/block <<'GUARD'
#!/bin/sh
echo network-attempt >> /tmp/network-attempts
exit 97
GUARD
chmod +x /tmp/guards/pulumi /tmp/guards/block
for cmd in curl wget fetch aria2c; do ln -s block "/tmp/guards/$cmd"; done
export PATH="/tmp/guards:$PATH"
prefix="$HOME/intended prefix"
reject() {
  set +e
  sh /bundle/install.sh --prefix "$prefix" -- "$@" > /tmp/rejection.log 2>&1
  status=$?
  set -e
  [ "$status" = 64 ]
  [ ! -e "$prefix" ]
  [ ! -e /tmp/unintended ]
  [ ! -e /tmp/old-pulumi-ran ]
  [ ! -e /tmp/network-attempts ]
}
reject --install-root /tmp/unintended
reject --install-root=/tmp/unintended
reject --version 0.0.1
reject --version=0.0.1
reject --install-root
reject --version
printf 'PULUMI_ARGUMENT_OVERRIDE_REJECTED_BEFORE_WRITES_PASS\nOLD_PATH_CLI_NOT_EXECUTED_PASS\n'
