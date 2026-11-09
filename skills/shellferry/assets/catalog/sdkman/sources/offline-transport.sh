#!/usr/bin/env bash
# Shellferry's local transport for the reviewed SDKMAN + Temurin install path.
# It is sourced only during installation; installed SDKMAN files keep their normal semantics.
__sdkman_secure_curl() {
    case "$1" in
        # Reviewed local allowlist: this bundle contains only this Java release.
        https://api.sdkman.io/2/candidates/validate/java/21.0.13.0+9-tem/linuxx64) printf '%s' 'valid' ;;
        https://api.sdkman.io/2/hooks/post/java/21.0.13.0+9-tem/linuxx64) cat "$OFFLINE_ROOT/upstream/java-post.sh" ;;
        *) offline_fetch "$1" ;;
    esac
}
__sdkman_secure_curl_with_timeouts() { __sdkman_secure_curl "$@"; }
__sdkman_secure_curl_download() {
    local url="$1" output='' headers=''
    shift
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --output) output="$2"; shift 2 ;;
            --dump-header) headers="$2"; shift 2 ;;
            *) printf 'Unsupported offline download argument: %s\n' "$1" >&2; return 64 ;;
        esac
    done
    [ "$url" = 'https://broker.sdkman.io/download/java/21.0.13.0+9-tem/linuxx64' ] && [ -n "$output" ] && [ -n "$headers" ] || return 69
    offline_fetch 'https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.13%2B9/OpenJDK21U-jdk_x64_linux_hotspot_21.0.13_9.tar.gz' "$output" || return
    # The broker provides archive type, not a checksum for its transformed zip.
    # Verify the original archive using Temurin's publisher checksum before the upstream hook.
    local expected actual
    read -r expected _ < "$OFFLINE_ROOT/resources/temurin-jdk.sha256.txt"
    [ "$expected" = 'd7f5d5cf865a2902b70ff549b97586a7d3f234e016f041ab447ea740c7d66d1c' ] || return 65
    actual=$(sha256sum "$output"); actual="${actual%% *}"
    [ "$actual" = "$expected" ] || { echo 'Temurin publisher checksum mismatch' >&2; return 65; }
    printf 'X-Sdkman-ArchiveType: tar.gz\r\n' > "$headers"
}
