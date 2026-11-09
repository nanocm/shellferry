#!/bin/bash
set -euo pipefail
export HOME=/tmp/clean-home
mkdir -p "$HOME" /tmp/guards
cat > /tmp/guards/block <<'GUARD'
#!/bin/sh
printf '%s\n' "$0 $*" >> /tmp/network-attempts
exit 97
GUARD
chmod +x /tmp/guards/block
for cmd in curl wget fetch aria2c; do ln -s block "/tmp/guards/$cmd"; done
export PATH="/tmp/guards:$PATH"
prefix="$HOME/"'literal $HOME  twice `printf INJECTED` $(printf INJECTED)' 
sh /bundle/install.sh --prefix "$prefix" > /tmp/install.log 2>&1
# A new shell receives none of the recipe-only environment settings.
unset OFFLINE_ROOT OFFLINE_PREFIX OFFLINE_AUDIT CLOUDSDK_COMPONENT_MANAGER_SNAPSHOT_URL CLOUDSDK_COMPONENT_MANAGER_DISABLE_UPDATE_CHECK CLOUDSDK_CORE_DISABLE_USAGE_REPORTING CLOUDSDK_CORE_DISABLE_PROMPTS || true
. "$HOME/.bashrc"
test "$(command -v gcloud)" = "$prefix/google-cloud-sdk/bin/gcloud"
complete -p gcloud > /tmp/completion
before=$(sha256sum "$prefix/google-cloud-sdk/bin/gcloud")
set +e
sh /bundle/install.sh --prefix "$prefix" > /tmp/overwrite.log 2>&1
status=$?
set -e
[ "$status" -ne 0 ]
grep -q 'already exists' /tmp/overwrite.log
test "$before" = "$(sha256sum "$prefix/google-cloud-sdk/bin/gcloud")"
gcloud version
gcloud components list --only-local-state --format='value(id)' > /tmp/local-components
grep -Fx core /tmp/local-components
gcloud config list --format=json > /tmp/config.json
# Run the installed original directly, without bundle environment or resources.
CLOUDSDK_COMPONENT_MANAGER_SNAPSHOT_URL="file://$prefix/google-cloud-sdk/offline/components-v592.0.0.json" \
  "$prefix/google-cloud-sdk/install.sh" --quiet --usage-reporting=false --command-completion=true --path-update=true --rc-path="$HOME/.bashrc" > /tmp/reinitialize.log 2>&1
[ "$(sha256sum "$prefix/google-cloud-sdk/install.sh" | awk '{print $1}')" = "db69ff9ac4c55c8b18c1041b717ba1370e4d921ace4d67c05088d4411d75282a" ]
[ -d "$prefix/google-cloud-sdk" ]
[ ! -e "$HOME/INJECTED" ]
"$prefix/google-cloud-sdk/platform/bundledpythonunix/bin/python3" -c 'import json; json.load(open("/tmp/config.json"))'
[ ! -e /tmp/network-attempts ]
printf 'POST_INSTALL_NO_RECIPE_ENV_PASS\nDEFAULT_OVERWRITE_REJECTED_PASS\nINSTALLED_ORIGINAL_REINITIALIZE_PASS\nLITERAL_PREFIX_PASS\n'
