#!/usr/bin/env python3
"""Run a converted installer in a disposable, networkless Podman/Docker container."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid

from offpack import sha256, safe_path


HARNESS = r'''#!/bin/sh
set -eu
export HOME=/tmp/offline-home
mkdir -p "$HOME" /tmp/guards
cp -R /bundle /tmp/package
chmod -R u+w /tmp/package
cd /tmp/package
prefix="$HOME/prefix with spaces"
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
[ ! -e /tmp/network-attempts ] || { cat /tmp/network-attempts >&2; exit 97; }
# Re-run installation to verify the actual upstream update/idempotence behavior.
sh repeat.sh "$prefix"
sh smoke.sh "$prefix"
[ ! -e /tmp/network-attempts ] || { cat /tmp/network-attempts >&2; exit 97; }
printf '\nOFFLINE_INSTALL_TEST_PASS\n'
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="Bundle directory or tar.gz archive (archive is extracted before testing)")
    parser.add_argument("--engine", choices=["podman", "docker"], default="podman")
    parser.add_argument("--image", required=True, help="Prepared matching image; no automatic image pulls")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--user", default="1000:1000")
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    archive_hash = None
    extracted = None
    if bundle.is_file():
        archive_hash = sha256(bundle)
        extracted = tempfile.TemporaryDirectory(prefix="offline-roundtrip-")
        extraction = Path(extracted.name)
        with tarfile.open(bundle, "r:*") as archive:
            seen = set()
            total_size = 0
            for member in archive:
                name = member.name.rstrip("/")
                safe_path(name)
                if name in seen or not (member.isfile() or member.isdir()):
                    raise ValueError("Archive contains duplicate entries or non-regular files")
                seen.add(name)
                total_size += member.size
                if total_size > 8 * 1024**3:
                    raise ValueError("Archive exceeds 8 GiB extraction limit")
                output = extraction / name
                if member.isdir():
                    output.mkdir(parents=True, exist_ok=True)
                else:
                    output.parent.mkdir(parents=True, exist_ok=True)
                    with archive.extractfile(member) as stream, output.open("wb") as target:
                        import shutil
                        shutil.copyfileobj(stream, target)
                    output.chmod(0o755 if name.endswith(".sh") else 0o644)
        roots = list(extraction.iterdir())
        if len(roots) != 1 or not roots[0].is_dir():
            raise ValueError("Archive must contain exactly one top-level bundle directory")
        bundle = roots[0]
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image_info = subprocess.run([args.engine, "image", "inspect", args.image], capture_output=True, text=True, check=True)
    image = json.loads(image_info.stdout)[0]
    environment_command = [args.engine, "run", "--rm", "--pull=never", "--network=none", "--cap-drop=all",
                           "--entrypoint", "sh", args.image, "-c",
                           'cat /etc/os-release; (ldd --version 2>&1 || true) | head -n 2; '
                           'for command in sh bash tar gzip unzip xz openssl file git dpkg-deb; do command -v "$command" || true; done']
    environment = subprocess.run(environment_command, capture_output=True, text=True, timeout=60)
    container = "offline-verify-" + uuid.uuid4().hex[:12]
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="offline-harness-") as temporary:
        harness = Path(temporary) / "verify.sh"
        harness.write_text(HARNESS, encoding="utf-8", newline="\n")
        harness.chmod(0o755)
        command = [args.engine, "run", "--rm", "--name", container, "--pull=never", "--network=none",
                   "--cap-drop=all", "--security-opt=no-new-privileges", "--user", args.user,
                   "--env", "HOME=/tmp/offline-home", "--env", "http_proxy=", "--env", "https_proxy=",
                   "--env", "HTTP_PROXY=", "--env", "HTTPS_PROXY=", "--env", "ALL_PROXY=", "--env", "all_proxy=",
                   "--volume", f"{bundle}:/bundle:ro", "--volume", f"{harness}:/verify.sh:ro",
                   "--entrypoint", "sh", args.image, "/verify.sh"]
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=args.timeout)
            output, code = result.stdout, result.returncode
        except subprocess.TimeoutExpired as exc:
            output = exc.stdout or b""
            if isinstance(output, bytes):
                output = output.decode("utf-8", errors="replace")
            output += "\nVerification timed out."
            code = 124
        finally:
            subprocess.run([args.engine, "rm", "-f", container], capture_output=True)
    passed = code == 0 and "OFFLINE_INSTALL_TEST_PASS" in output
    report = {"name": manifest["name"], "version": manifest["version"], "target": manifest["target"],
              "status": "passed" if passed else "failed", "engine": args.engine, "image": args.image,
              "image_id": image.get("Id"), "image_digests": image.get("RepoDigests", []),
              "environment": environment.stdout, "archive_sha256": archive_hash,
              "archive_roundtrip": archive_hash is not None,
              "network": "none", "user": args.user, "manifest_sha256": sha256(bundle / "manifest.json"),
              "checksum_list_sha256": sha256(bundle / "SHA256SUMS"), "elapsed_seconds": round(time.monotonic() - started, 2),
              "exit_code": code, "checks": ["checksum verification", "prerequisite preflight", "path with spaces",
              "install from clean home", "smoke command", "repeat installation", "blocked download command detection"],
              "verified_at": datetime.now(timezone.utc).isoformat(), "recipe_sha256": manifest["recipe_sha256"],
              "builder": manifest.get("builder"),
              "verifier": {name: sha256(Path(__file__).with_name(name)) for name in ("verify.py", "offpack.py")},
              "scope": "Container userspace on host kernel; download command guards cover curl/wget/fetch/aria2c only. Network=none proves operation without external network, not absence of every attempted network syscall. No claim about untested OS versions, architectures, services, or kernel features."}
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output.with_suffix(".log").write_text(output, encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not passed:
        print(output[-12000:], file=sys.stderr)
    if extracted is not None:
        extracted.cleanup()
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
