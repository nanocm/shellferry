#!/usr/bin/env bash
set -e
# Preserve bootstrap checks, extraction, native components and shell initialization.
bash "$OFFLINE_ROOT/upstream/install.sh"
test "$(cat "$SDKMAN_DIR/var/version")" = '5.24.0'
test "$(cat "$SDKMAN_DIR/var/version_native")" = '0.8.0'
# Supported settings: no live health/self-update checks on the air-gapped target.
sed -i 's/^sdkman_auto_answer=.*/sdkman_auto_answer=true/; s/^sdkman_healthcheck_enable=.*/sdkman_healthcheck_enable=false/; s/^sdkman_selfupdate_feature=.*/sdkman_selfupdate_feature=false/; s/^sdkman_colour_enable=.*/sdkman_colour_enable=false/' "$SDKMAN_DIR/etc/config"
source "$SDKMAN_DIR/bin/sdkman-init.sh"
source "$OFFLINE_ROOT/upstream/offline-transport.sh"
sdk install java '21.0.13.0+9-tem'
sdk default java '21.0.13.0+9-tem'
sdk use java '21.0.13.0+9-tem'
test -x "$SDKMAN_DIR/candidates/java/21.0.13.0+9-tem/bin/javac"
