#!/usr/bin/env python3
"""Apply reviewed, fail-closed shell patches and build a portable offline bundle."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import sys
import tarfile
import tempfile

from offpack import PackError, TARGETS, download, read_url, safe_name, safe_path, sha256, validate_url


def write(path, text, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    path.chmod(mode)


def render(value):
    """Shell quote text while allowing only three explicitly documented variables."""
    chunks = re.split(r"(\{(?:bundle|prefix|home)\})", value)
    names = {"{bundle}": '"$OFFLINE_ROOT"', "{prefix}": '"$prefix"', "{home}": '"$HOME"'}
    return "".join(names.get(chunk, shlex.quote(chunk)) for chunk in chunks if chunk) or "''"


def shell_code_index(command):
    if command and Path(command[0]).name in {"sh", "bash", "dash", "zsh"}:
        for index, argument in enumerate(command[1:], 1):
            if re.fullmatch(r"-[a-zA-Z]*c[a-zA-Z]*", argument) and index + 1 < len(command):
                return index + 1
    return None


def resource_path(value):
    safe_path(value)
    if not value.startswith("resources/"):
        raise PackError("资源路径必须以 resources/ 开头。")
    return value


def script_path(value):
    safe_path(value)
    if not value.startswith("upstream/"):
        raise PackError("脚本路径必须以 upstream/ 开头。")
    return value


def apply_patches(text, patches):
    for index, patch in enumerate(patches):
        old, new = patch["old"], patch["new"]
        count = patch.get("count", 1)
        if not isinstance(old, str) or not old or not isinstance(new, str) or not isinstance(count, int) or count < 1:
            raise PackError(f"无效替换规则 #{index + 1}")
        actual = text.count(old)
        if actual != count:
            raise PackError(f"替换规则 #{index + 1} 匹配 {actual} 次，预期 {count} 次；上游脚本可能已变化，需重新分析。")
        text = text.replace(old, new, count)
    return text


def validate_recipe(recipe):
    if recipe.get("schema") != 1:
        raise PackError("recipe schema 必须是 1。")
    safe_name(recipe["name"])
    if not isinstance(recipe.get("version"), str) or not recipe["version"]:
        raise PackError("需明确固定 version。")
    if recipe.get("target") not in TARGETS:
        raise PackError("需明确 target。")
    if recipe.get("shell", "sh") not in {"sh", "bash"}:
        raise PackError("shell 必须是 sh 或 bash。")
    default_prefix = recipe.get("default_prefix", "{home}/.local")
    if not isinstance(default_prefix, str) or not default_prefix.startswith(("/", "{home}/")) or any(c in default_prefix for c in "\n\r\x00"):
        raise PackError("default_prefix 必须是绝对路径或 {home}/ 下的路径。")
    prefix_env = recipe.get("default_prefix_env")
    if prefix_env is not None and (not isinstance(prefix_env, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", prefix_env)):
        raise PackError("default_prefix_env 必须是环境变量名。")
    script_path(recipe["entrypoint"])
    if not recipe.get("scripts") or not recipe.get("smoke"):
        raise PackError("需提供 scripts 和至少一个 smoke 验证命令。")
    for key, value in recipe.get("env", {}).items():
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key) or not isinstance(value, str):
            raise PackError(f"无效环境变量：{key}")
        if key in {"OFFLINE_ROOT", "OFFLINE_AUDIT", "HOME", "BASH_ENV", "ENV", "LD_PRELOAD"}:
            raise PackError(f"环境变量 {key} 由包装器管理。")
    for command in recipe["smoke"]:
        if not isinstance(command, list) or not command or not all(isinstance(v, str) for v in command):
            raise PackError("smoke 必须是非空字符串参数数组的列表。")
        code_index = shell_code_index(command)
        if code_index is not None and re.search(r"\{(?:prefix|bundle|home)\}", command[code_index]):
            raise PackError("shell -c 代码不能插入路径占位符，请在代码中引用 \"$OFFLINE_PREFIX\"、\"$OFFLINE_ROOT\"、\"$HOME\"。")
    for field in ("args", "repeat_args", "requires", "notes"):
        values = recipe.get(field, [])
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            raise PackError(f"{field} 必须是字符串数组。")
    runtime = recipe.get("runtime", {})
    if not isinstance(runtime, dict) or set(runtime) - {"libc", "os_id", "os_version"}:
        raise PackError("runtime 只接受 libc、os_id、os_version。")
    for field, value in runtime.items():
        if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.+\-]+", value):
            raise PackError(f"runtime.{field} 格式无效。")
    if runtime.get("libc") not in {None, "glibc", "musl"}:
        raise PackError("runtime.libc 必须是 glibc 或 musl。")
    for command in recipe.get("requires", []):
        if not re.fullmatch(r"[A-Za-z0-9_.+\-]+", command):
            raise PackError(f"无效前置命令：{command}")


def make_library(resources):
    lines = ['# Local resource lookup. Unknown URLs fail; there is no online fallback.',
             'offline_fetch() {', '  [ "$#" -ge 1 ] && [ "$#" -le 2 ] || { echo "offline_fetch URL [DEST]" >&2; return 64; }',
             '  case "$1" in']
    for item in resources:
        patterns = "|".join(shlex.quote(url) for url in [item["url"]] + item.get("aliases", []))
        lines.append(f'    {patterns}) _offline_file="$OFFLINE_ROOT"/{shlex.quote(item["path"])} ;;')
    lines.extend(['    *) printf "Uncollected URL: %s\\n" "$1" | tee -a "${OFFLINE_AUDIT:?offline wrapper audit required}" >&2; return 69 ;;', '  esac',
                  '  [ -f "$_offline_file" ] || { echo "Offline resource is missing" | tee -a "${OFFLINE_AUDIT:?offline wrapper audit required}" >&2; return 66; }',
                  '  _offline_status=0',
                  '  if [ "$#" -eq 2 ] && [ "$2" != - ]; then cp -- "$_offline_file" "$2" || _offline_status=$?; else cat -- "$_offline_file" || _offline_status=$?; fi',
                  '  if [ "$_offline_status" -ne 0 ]; then printf "Local resource read failed: %s\\n" "$1" | tee -a "${OFFLINE_AUDIT:?offline wrapper audit required}" >&2; return "$_offline_status"; fi', '}'])
    return "\n".join(lines) + "\n"


def make_wrapper(recipe):
    target_os, target_arch = recipe["target"].split("-")[:2]
    requires = list(dict.fromkeys([recipe.get("shell", "sh")] + recipe.get("requires", [])))
    env_lines = "\n".join(f"export {name}={render(value)}" for name, value in recipe.get("env", {}).items())
    check_lines = "\n".join(f"command -v {shlex.quote(name)} >/dev/null 2>&1 || die {shlex.quote('Missing prerequisite: ' + name)}" for name in requires)
    invocation = shlex.quote(recipe.get("shell", "sh")) + ' "$OFFLINE_ROOT"/' + shlex.quote(recipe["entrypoint"])
    invocation += "".join(" " + render(arg) for arg in recipe.get("args", [])) + ' "$@"'
    default_prefix = render(recipe.get("default_prefix", "{home}/.local"))
    prefix_selection = 'prefix=${OFFLINE_PREFIX:-$default_prefix}'
    if recipe.get("default_prefix_env"):
        prefix_selection = 'prefix=${OFFLINE_PREFIX:-${' + recipe["default_prefix_env"] + ':-$default_prefix}}'
    runtime = dict(recipe.get("runtime", {}))
    if recipe["target"].endswith("-musl"):
        runtime.setdefault("libc", "musl")
    compatibility = []
    if runtime.get("libc"):
        compatibility.extend(['runtime_libc=unknown',
                              'if (ldd --version 2>&1 || true) | grep -qi musl; then runtime_libc=musl;',
                              'elif (getconf GNU_LIBC_VERSION 2>/dev/null || true) | grep -qi glibc; then runtime_libc=glibc; fi',
                              f'[ "$runtime_libc" = {shlex.quote(runtime["libc"])} ] || die "libc mismatch or not detected: $runtime_libc"'])
    if runtime.get("os_id") or runtime.get("os_version"):
        compatibility.append('[ -r /etc/os-release ] || die "Cannot verify distribution without /etc/os-release"')
        compatibility.append('runtime_id=$(sed -n \'s/^ID=//p\' /etc/os-release | tr -d \'"\')')
        compatibility.append('runtime_version=$(sed -n \'s/^VERSION_ID=//p\' /etc/os-release | tr -d \'"\')')
        if runtime.get("os_id"):
            compatibility.append(f'[ "$runtime_id" = {shlex.quote(runtime["os_id"])} ] || die "Distribution mismatch: $runtime_id"')
        if runtime.get("os_version"):
            compatibility.append(f'[ "$runtime_version" = {shlex.quote(runtime["os_version"])} ] || die "Distribution version mismatch: $runtime_version"')
    text = r'''#!/bin/sh
set -eu
die() { printf 'Error: %s\n' "$*" >&2; exit 1; }
OFFLINE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
export OFFLINE_ROOT
default_prefix=@DEFAULT_PREFIX@
@PREFIX_SELECTION@
check_only=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --prefix) [ "$#" -ge 2 ] || die '--prefix needs a directory'; prefix=$2; shift 2 ;;
    --prefix=*) prefix=${1#*=}; shift ;;
    --check) check_only=1; shift ;;
    --help) printf '%s\n' 'Usage: sh install.sh [--prefix DIR] [--check] [-- ORIGINAL_ARGUMENTS]'; exit 0 ;;
    --) shift; break ;;
    *) die 'Installer arguments must follow --' ;;
  esac
done
case "$prefix" in /*) ;; *) die '--prefix must be absolute' ;; esac
[ "$prefix" != / ] || die 'Choose a prefix other than /'
system=$(uname -s)
case "$system" in Linux) system=linux ;; Darwin) system=darwin ;; esac
arch=$(uname -m)
case "$arch" in arm64) arch=aarch64 ;; amd64) arch=x86_64 ;; esac
[ "$system" = @OS@ ] && [ "$arch" = @ARCH@ ] || die 'Target OS or CPU does not match this bundle'
@COMPATIBILITY@
if command -v sha256sum >/dev/null 2>&1; then
  (cd "$OFFLINE_ROOT" && sha256sum -c SHA256SUMS) || die 'Bundle verification failed'
elif command -v shasum >/dev/null 2>&1; then
  (cd "$OFFLINE_ROOT" && shasum -a 256 -c SHA256SUMS) || die 'Bundle verification failed'
else die 'sha256sum or shasum is required'; fi
@REQUIRES@
[ "$check_only" -eq 0 ] || { echo 'Verification passed; nothing installed.'; exit 0; }
OFFLINE_PREFIX=$prefix
export OFFLINE_PREFIX
OFFLINE_AUDIT=$(mktemp "${TMPDIR:-/tmp}/offline-audit.XXXXXXXX")
export OFFLINE_AUDIT
trap 'rm -f -- "$OFFLINE_AUDIT"' 0
trap 'exit 130' 1 2 15
@ENV@
if [ "${OFFLINE_TRACE:-0}" = 1 ]; then PS4='+ offline: '; export PS4; fi
install_status=0
@INVOKE@ || install_status=$?
if [ -s "$OFFLINE_AUDIT" ]; then cat "$OFFLINE_AUDIT" >&2; die 'Offline resource lookup failed, even if the upstream script ignored the error'; fi
exit "$install_status"
'''
    return text.replace("@OS@", shlex.quote(target_os)).replace("@ARCH@", shlex.quote(target_arch)).replace("@DEFAULT_PREFIX@", default_prefix).replace("@PREFIX_SELECTION@", prefix_selection).replace("@COMPATIBILITY@", "\n".join(compatibility)).replace("@REQUIRES@", check_lines).replace("@ENV@", env_lines).replace("@INVOKE@", invocation)


def build(recipe_file, destination, cache):
    recipe_file = recipe_file.resolve()
    recipe = json.loads(recipe_file.read_text(encoding="utf-8-sig"))
    validate_recipe(recipe)
    if destination.exists():
        raise PackError(f"输出已存在，请选择新目录：{destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    entries = []
    url_map = {}
    with tempfile.TemporaryDirectory(prefix="offline-build-", dir=destination.parent) as temporary:
        root = Path(temporary) / "bundle"
        root.mkdir()
        resource_names = set()
        for item in recipe.get("resources", []):
            path = resource_path(item["path"])
            if path in resource_names:
                raise PackError(f"资源路径重复：{path}")
            resource_names.add(path)
            validate_url(item["url"])
            for url in [item["url"]] + item.get("aliases", []):
                if url in url_map:
                    raise PackError(f"URL 映射重复：{url}")
                url_map[url] = path
            if item.get("source"):
                source = (recipe_file.parent / item["source"]).resolve()
                digest = sha256(source)
                if item.get("sha256") and digest.lower() != item["sha256"].lower():
                    raise PackError(f"资源摘要不匹配：{path}")
            else:
                source, digest = download(item["url"], cache, item.get("sha256"))
            output = root / path
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, output)
            entries.append({"kind": "resource", "path": path, "url": item["url"], "sha256": digest,
                            "expected_checksum_matched": bool(item.get("sha256")),
                            "checksum_source": item.get("checksum_source", "recipe" if item.get("sha256") else "local-computation")})
        script_names = set()
        for item in recipe["scripts"]:
            path = script_path(item["path"])
            if path in script_names:
                raise PackError(f"脚本路径重复：{path}")
            script_names.add(path)
            if item.get("source"):
                original = (recipe_file.parent / item["source"]).read_bytes()
            elif item.get("url"):
                original = read_url(item["url"])
            else:
                raise PackError(f"脚本没有来源：{path}")
            original_digest = hashlib.sha256(original).hexdigest()
            if item.get("sha256") and original_digest.lower() != item["sha256"].lower():
                raise PackError(f"原脚本摘要变化：{path}")
            text = original.decode("utf-8-sig").replace("\r\n", "\n")
            patched = apply_patches(text, item.get("patches", []))
            # Keep the shebang first for subprocesses that invoke an embedded script directly.
            first, separator, rest = patched.partition("\n")
            prelude = '. "$OFFLINE_ROOT/offline-lib.sh"\n'
            patched = first + "\n" + prelude + rest if first.startswith("#!") else prelude + patched
            write(root / path, patched, 0o755)
            evidence = root / "provenance" / path
            evidence.parent.mkdir(parents=True, exist_ok=True)
            evidence.write_bytes(original)
            diff = "".join(difflib.unified_diff(text.splitlines(True), patched.splitlines(True), fromfile="original/" + path, tofile=path))
            write(root / "provenance" / (path + ".diff"), diff)
            entries.append({"kind": "script", "path": path, "url": item.get("url"), "sha256_original": original_digest,
                            "sha256_patched": sha256(root / path), "patch_count": len(item.get("patches", []))})
        if recipe["entrypoint"] not in script_names:
            raise PackError("entrypoint 不在 scripts 中。")
        write(root / "offline-lib.sh", make_library(recipe.get("resources", [])))
        write(root / "install.sh", make_wrapper(recipe), 0o755)
        smoke = '#!/bin/sh\nset -eu\nprefix=${1:?prefix required}\nOFFLINE_PREFIX=$prefix\nOFFLINE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)\nexport OFFLINE_ROOT OFFLINE_PREFIX\n'
        smoke += "\n".join(f"export {name}={render(value)}" for name, value in recipe.get("env", {}).items()) + "\n"
        smoke += "\n".join(" ".join(shlex.quote(arg) if index == shell_code_index(command) else render(arg) for index, arg in enumerate(command)) for command in recipe["smoke"]) + "\n"
        write(root / "smoke.sh", smoke, 0o755)
        repeat = '#!/bin/sh\nset -eu\nprefix=${1:?prefix required}\nOFFLINE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)\nexport OFFLINE_ROOT\n'
        repeat += 'sh "$OFFLINE_ROOT/install.sh" --prefix "$prefix" --'
        repeat += ''.join(' ' + render(arg) for arg in recipe.get("repeat_args", [])) + '\n'
        write(root / "repeat.sh", repeat, 0o755)
        manifest = {"schema": 1, "mode": "converted-script", "name": recipe["name"], "version": recipe["version"],
                    "target": recipe["target"], "entrypoint": recipe["entrypoint"], "resources": entries,
                    "requires": recipe.get("requires", []), "runtime": recipe.get("runtime", {}), "notes": recipe.get("notes", []),
                    "default_prefix": recipe.get("default_prefix", "{home}/.local"), "default_prefix_env": recipe.get("default_prefix_env"),
                    "validation_status": "not-run", "recipe_sha256": sha256(recipe_file),
                    "builder": {name: sha256(Path(__file__).with_name(name)) for name in ("convert.py", "offpack.py")}}
        write(root / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        # Remove machine-local paths from the portable, auditable recipe.
        portable = json.loads(json.dumps(recipe))
        for item in portable.get("scripts", []):
            item["source"] = "provenance/" + item["path"]
        for item in portable.get("resources", []):
            item["source"] = item["path"]
        write(root / "recipe.json", json.dumps(portable, ensure_ascii=False, indent=2) + "\n")
        write(root / "INSTALL.txt", f"{recipe['name']} {recipe['version']} / {recipe['target']}\n"
              "Verify: sh install.sh --check\nInstall: sh install.sh\n"
              "Default prefix: " + recipe.get("default_prefix", "{home}/.local") + "\n"
              "Custom prefix: sh install.sh --prefix \"$HOME/.local\"\n"
              "Extra upstream arguments: sh install.sh -- UPSTREAM_ARGS\n"
              "Check the installed program: sh smoke.sh \"$HOME/.local\"\n"
              "Prerequisites: " + ", ".join(recipe.get("requires", [])) + "\n"
              "Behavior changes: " + "; ".join(recipe.get("notes", [])) + "\n"
              "Original scripts and diffs are in provenance/. Read validation.json alongside the archive for actual tested scope.\n")
        write(root / "SHA256SUMS", "".join(f"{sha256(path)}  {path.relative_to(root).as_posix()}\n" for path in sorted(root.rglob("*")) if path.is_file()))
        shutil.move(str(root), str(destination))
    print(str(destination))


def archive_bundle(bundle, output):
    if output.exists():
        raise PackError(f"输出已存在：{output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output, "w:gz") as archive:
        for path in [bundle] + sorted(bundle.rglob("*")):
            info = archive.gettarinfo(str(path), arcname=str(Path(bundle.name) / path.relative_to(bundle)).replace("\\", "/"))
            if not (info.isfile() or info.isdir()):
                raise PackError("包目录只能包含普通文件和目录。")
            info.uid = info.gid = info.mtime = 0
            info.uname = info.gname = ""
            info.mode = 0o755 if info.isdir() or path.suffix == ".sh" else 0o644
            if info.isfile():
                with path.open("rb") as stream:
                    archive.addfile(info, stream)
            else:
                archive.addfile(info)
    write(output.with_name(output.name + ".sha256"), f"{sha256(output)}  {output.name}\n")
    print(str(output))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    builder = commands.add_parser("build")
    builder.add_argument("recipe", type=Path)
    builder.add_argument("--output", type=Path, required=True)
    builder.add_argument("--cache-dir", type=Path, default=Path.home() / ".cache/offline-install")
    archiver = commands.add_parser("archive")
    archiver.add_argument("bundle", type=Path)
    archiver.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            build(args.recipe, args.output.resolve(), args.cache_dir)
        else:
            archive_bundle(args.bundle.resolve(), args.output.resolve())
        return 0
    except (PackError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if os.name == "nt":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
