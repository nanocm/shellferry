#!/usr/bin/env python3
"""Build self-contained Unix installers without executing online install scripts."""

from __future__ import annotations

import argparse
import hashlib
from http.client import HTTPException
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import sys
import tarfile
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, unquote
from urllib.request import Request, urlopen
import zipfile


TARGETS = (
    "linux-x86_64", "linux-aarch64", "linux-x86_64-musl",
    "linux-aarch64-musl", "darwin-x86_64", "darwin-aarch64",
)
USER_AGENT = "offpack/0.1 (+offline installer builder)"
MAX_MEMBER = 512 * 1024 * 1024
MAX_PAYLOAD = 1024 * 1024 * 1024


class PackError(Exception):
    pass


def log(message):
    print(message, file=sys.stderr, flush=True)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_url(url):
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise PackError("下载地址必须是无内嵌账号密码的 HTTPS URL。")
    if any(char in url for char in "\r\n\x00"):
        raise PackError("下载地址包含非法字符。")
    return url


def safe_version(value):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+\-]{0,95}", value):
        raise PackError(f"不支持的版本号：{value!r}")
    if value in {".", ".."}:
        raise PackError("版本号不能是相对路径。")
    return value


def safe_name(value):
    if not re.fullmatch(r"[a-z0-9][a-z0-9._\-]{0,63}", value):
        raise PackError("软件名称只能包含小写字母、数字、点、下划线和连字符。")
    return value


def safe_path(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_./@+\-]+", value):
        raise PackError(f"文件路径含不支持的字符：{value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value != str(path) or value == ".":
        raise PackError(f"文件路径必须是规范的相对路径：{value!r}")
    return value


def install_path(value):
    safe_path(value)
    if not value.startswith(("bin/", "share/")):
        raise PackError("安装文件必须位于 bin/ 或 share/ 下。")
    return value


def request_url(url, method="GET", headers=None):
    validate_url(url)
    request_headers = {"User-Agent": USER_AGENT, "Accept-Encoding": "identity"}
    request_headers.update(headers or {})
    response = urlopen(Request(url, headers=request_headers, method=method), timeout=45)
    validate_url(response.geturl())
    return response


def read_url(url, limit=2 * 1024 * 1024):
    last_error = None
    for attempt in range(3):
        try:
            with request_url(url) as response:
                body = response.read(limit + 1)
                if len(body) > limit:
                    raise PackError("入口脚本超过大小限制。")
                return body
        except (OSError, URLError, HTTPException) as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(attempt + 1)
    raise PackError(f"无法下载 {url}：{last_error}")


def latest_tag(repository):
    url = f"https://github.com/{repository}/releases/latest"
    for attempt in range(3):
        try:
            with request_url(url, method="HEAD") as response:
                final_path = unquote(urlparse(response.geturl()).path)
            expected_prefix = f"/{repository}/releases/tag/"
            if not final_path.startswith(expected_prefix):
                raise PackError("GitHub 没有返回确定的发布版本，请用 --version 指定版本。")
            return safe_version(final_path[len(expected_prefix):])
        except HTTPError as exc:
            # A few proxies block HEAD but allow a regular request.
            if exc.code == 405:
                with request_url(url) as response:
                    final_path = unquote(urlparse(response.geturl()).path)
                prefix = f"/{repository}/releases/tag/"
                if final_path.startswith(prefix):
                    return safe_version(final_path[len(prefix):])
                raise PackError("无法解析最新版本，请用 --version 指定版本。") from exc
            if attempt == 2:
                raise
        except (OSError, URLError, HTTPException):
            if attempt == 2:
                raise
        time.sleep(attempt + 1)
    raise PackError("无法解析最新版本。")


def download(url, cache, expected_sha=None, retries=4):
    validate_url(url)
    if expected_sha is not None and not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha):
        raise PackError("SHA-256 必须是 64 位十六进制字符串。")
    cache.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()
    completed = cache / key
    receipt = cache / (key + ".json")
    partial = cache / (key + ".part")
    if completed.is_file() and receipt.is_file():
        try:
            previous = json.loads(receipt.read_text(encoding="utf-8"))
            actual_sha = sha256(completed)
            if previous["sha256"] == actual_sha and (
                expected_sha is None or actual_sha.lower() == expected_sha.lower()
            ):
                log(f"使用缓存：{Path(urlparse(url).path).name}")
                return completed, actual_sha
        except (ValueError, KeyError, OSError):
            pass
        completed.unlink(missing_ok=True)
        receipt.unlink(missing_ok=True)

    log(f"下载：{url}")
    last_error = None
    for attempt in range(retries):
        position = partial.stat().st_size if partial.is_file() else 0
        headers = {"Range": f"bytes={position}-"} if position else {}
        try:
            with request_url(url, headers=headers) as response:
                status = response.status
                if status == 206:
                    match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", response.headers.get("Content-Range", ""))
                    if not match or int(match[1]) != position:
                        partial.unlink(missing_ok=True)
                        raise OSError("下载服务器返回了不匹配的断点范围")
                    total = int(match[3])
                    mode = "ab"
                elif status == 200:
                    position = 0
                    total = int(response.headers["Content-Length"]) if response.headers.get("Content-Length") else None
                    mode = "wb"
                else:
                    raise OSError(f"下载服务器返回 HTTP {status}")
                with partial.open(mode) as output:
                    for chunk in iter(lambda: response.read(1024 * 1024), b""):
                        output.write(chunk)
                if total is not None and partial.stat().st_size != total:
                    raise OSError("连接中断，文件下载不完整")
            if not partial.stat().st_size:
                raise OSError("下载内容为空")
            actual_sha = sha256(partial)
            if expected_sha and actual_sha.lower() != expected_sha.lower():
                partial.unlink(missing_ok=True)
                raise PackError(f"上游文件 SHA-256 不匹配：{url}")
            os.replace(partial, completed)
            receipt.write_text(json.dumps({"url": url, "sha256": actual_sha}, indent=2), encoding="utf-8")
            return completed, actual_sha
        except HTTPError as exc:
            last_error = exc
            if exc.code == 416:
                partial.unlink(missing_ok=True)
            elif exc.code in {400, 401, 403, 404}:
                raise PackError(f"下载失败（HTTP {exc.code}）：{url}") from exc
        except (OSError, URLError, HTTPException) as exc:
            last_error = exc
        if attempt + 1 < retries:
            log(f"下载中断，正在重试（{attempt + 2}/{retries}）……")
            time.sleep(min(attempt + 1, 3))
    raise PackError(f"下载失败，断点已保留，可重新运行：{last_error}")


def parse_source(source):
    if source in {"bun", "zoxide"}:
        return {"name": source, "url": None, "version": None, "original": source}
    if source.startswith("https://") and not any(char.isspace() for char in source):
        url = source
        script_args = []
    else:
        if any(char in source for char in "\r\n`$"):
            raise PackError("请传入一条不含变量展开或命令替换的 curl/wget 管道命令。")
        lexer = shlex.shlex(source, posix=True, punctuation_chars="|;&<>()")
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
        if tokens.count("|") != 1 or any(token in {";", "&&", "||", "&", "(", ")", "<", ">", ">>"} for token in tokens):
            raise PackError("仅支持单条 curl/wget URL | bash/sh 命令；多条命令请分别打包。")
        divider = tokens.index("|")
        fetch, shell = tokens[:divider], tokens[divider + 1:]
        if not fetch or fetch[0] not in {"curl", "wget"} or not shell or shell[0] not in {"sh", "bash"}:
            raise PackError("命令格式应为 curl/wget URL | bash/sh。")
        urls = [token for token in fetch[1:] if token.startswith("https://")]
        if len(urls) != 1:
            raise PackError("下载命令必须包含且仅包含一个 HTTPS URL。")
        url = urls[0]
        flags = [token for token in fetch[1:] if token != url]
        allowed_curl = {"--fail", "--silent", "--show-error", "--location", "--progress-bar"}
        if fetch[0] == "curl":
            if any(flag not in allowed_curl and not re.fullmatch(r"-[fsSL]+", flag) for flag in flags):
                raise PackError("此版本支持 curl 的 -f/-s/-S/-L 下载参数；其他参数请改用脚本 URL。")
        else:
            if flags not in (["-qO-"], ["-O-"], ["-q", "-O-"], ["-qO", "-"], ["-q", "-O", "-"], ["-O", "-"]):
                raise PackError("wget 请使用 -qO- URL 或 -q -O - URL。")
        script_args = shell[1:]
        if script_args and script_args[0] == "-s":
            script_args = script_args[1:]
        if script_args and script_args[0] == "--":
            script_args = script_args[1:]
        elif script_args:
            raise PackError("脚本参数请写在 bash/sh -s -- 之后。")
    validate_url(url)
    parsed = urlparse(url)
    if parsed.netloc == "bun.sh" and parsed.path.rstrip("/") == "/install" and not parsed.query:
        name = "bun"
    elif parsed.netloc == "raw.githubusercontent.com" and re.fullmatch(r"/ajeetdsouza/zoxide/[^/]+/install\.sh", parsed.path) and not parsed.query:
        name = "zoxide"
    else:
        name = None
    version = None
    if name == "bun" and script_args:
        if len(script_args) != 1 or script_args[0].startswith("-"):
            raise PackError("Bun 支持传入一个版本参数；其他选项请在离线安装时设置。")
        version = safe_version(script_args[0])
    elif name == "zoxide" and script_args:
        raise PackError("zoxide 安装参数请在离线端设置；平台使用 --target，目录使用 install.sh --prefix。")
    return {"name": name, "url": url, "version": version, "original": source}


def builtin_recipe(source, target, requested_version, variant):
    name = source["name"]
    repository = {"bun": "oven-sh/bun", "zoxide": "ajeetdsouza/zoxide"}[name]
    requested = requested_version or source["version"] or "latest"
    if requested_version and source["version"]:
        left = requested_version.removeprefix("bun-").removeprefix("v")
        right = source["version"].removeprefix("bun-").removeprefix("v")
        if left != right:
            raise PackError("--version 与原命令中的版本不同，请只保留一个版本。")
    tag = latest_tag(repository) if requested == "latest" else safe_version(requested)
    system, arch = target.split("-")[:2]
    if name == "bun":
        tag = tag if tag.startswith("bun-") else "bun-" + (tag if tag.startswith("v") else "v" + tag)
        build = f"{system}-{'x64' if arch == 'x86_64' else 'aarch64'}"
        if target.endswith("-musl"):
            build += "-musl"
        if arch == "x86_64" and variant == "baseline":
            build += "-baseline"
        asset_name = f"bun-{build}.zip"
        files = {f"bun-{build}/bun": "bin/bun"}
        links = {"bin/bunx": "bun"}
        archive_format = "zip"
        version = tag.removeprefix("bun-v")
    else:
        tag = tag if tag.startswith("v") else "v" + tag
        version = tag.removeprefix("v")
        triple = f"{arch}-unknown-linux-musl" if system == "linux" else f"{arch}-apple-darwin"
        asset_name = f"zoxide-{version}-{triple}.tar.gz"
        files = {"zoxide": "bin/zoxide", "man/man1/*.1": "share/man/man1/"}
        links = {}
        archive_format = "tar.gz"
    return {
        "name": name, "version": version, "target": target,
        "release_url": f"https://github.com/{repository}/releases/tag/{tag}",
        "installer_url": source["url"] or (
            "https://bun.sh/install" if name == "bun" else
            "https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh"
        ),
        "source_command": source["original"], "links": links,
        "assets": [{"url": f"https://github.com/{repository}/releases/download/{tag}/{asset_name}",
                    "format": archive_format, "files": files}],
    }


def load_recipe(path, target, version):
    try:
        recipe = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PackError(f"无法读取配置文件：{exc}") from exc
    if not isinstance(recipe, dict):
        raise PackError("配置文件的顶层必须是对象。")
    recipe["name"] = safe_name(recipe.get("name", ""))
    recipe["version"] = safe_version(version or recipe.get("version", ""))
    declared_target = recipe.get("target")
    if target and declared_target and target != declared_target:
        raise PackError("--target 与配置文件的平台不同。请先调整配置文件中的下载资源，避免打包错误架构的程序。")
    recipe["target"] = target or declared_target
    if recipe["target"] not in TARGETS:
        raise PackError("配置文件需包含有效 target，或使用 --target 指定目标平台。")
    if not isinstance(recipe.get("assets"), list) or not recipe["assets"]:
        raise PackError("配置文件必须包含非空 assets 列表。")
    variables = {"name": recipe["name"], "version": recipe["version"], "target": recipe["target"]}
    try:
        for asset in recipe["assets"]:
            asset["url"] = validate_url(asset["url"].format_map(variables))
            asset["files"] = {key.format_map(variables): value.format_map(variables) for key, value in asset["files"].items()}
    except (KeyError, ValueError, TypeError, AttributeError) as exc:
        raise PackError(f"配置文件字段不正确：{exc}") from exc
    recipe.setdefault("links", {})
    return recipe


def archive_members(path, archive_format):
    """Only expose regular files; never use extractall on untrusted archives."""
    if archive_format == "raw":
        return None, {"@file": (path.stat().st_size, lambda: path.open("rb"))}
    if archive_format == "zip":
        archive = zipfile.ZipFile(path)
        members = {}
        for info in archive.infolist():
            name = info.filename.removeprefix("./")
            unix_mode = info.external_attr >> 16
            if info.is_dir() or unix_mode & 0o170000 == 0o120000:
                continue
            if name in members:
                archive.close()
                raise PackError(f"压缩包包含重复文件：{name}")
            members[name] = (info.file_size, lambda entry=info: archive.open(entry))
        return archive, members
    if archive_format in {"tar.gz", "tar.xz", "tar.bz2", "tar"}:
        archive = tarfile.open(path, "r:*")
        members = {}
        for info in archive.getmembers():
            if not info.isfile():
                continue
            name = info.name.removeprefix("./")
            if name in members:
                archive.close()
                raise PackError(f"压缩包包含重复文件：{name}")
            members[name] = (info.size, lambda entry=info: archive.extractfile(entry))
        return archive, members
    raise PackError(f"不支持的压缩格式：{archive_format}")


def collect_files(asset_path, asset, payload, occupied, total):
    archive, members = archive_members(asset_path, asset.get("format", "tar.gz"))
    try:
        files = asset.get("files")
        if not isinstance(files, dict) or not files:
            raise PackError("每个下载资源必须包含非空 files 映射。")
        for source, destination in files.items():
            if source.endswith("/*.1"):
                prefix = source[:-3]
                matches = [name for name in members if name.startswith(prefix) and name.endswith(".1") and "/" not in name[len(prefix):]]
                if not destination.endswith("/"):
                    raise PackError("通配符文件的安装目录必须以 / 结尾。")
                destinations = {name: destination + PurePosixPath(name).name for name in matches}
            else:
                destinations = {source: destination} if source in members else {}
            if not destinations:
                raise PackError(f"压缩包中找不到文件：{source}")
            for member, relative in destinations.items():
                if member != "@file":
                    safe_path(member)
                install_path(relative)
                if relative in occupied:
                    raise PackError(f"多个资源试图安装同一个文件：{relative}")
                size, opener = members[member]
                if size > MAX_MEMBER or total + size > MAX_PAYLOAD:
                    raise PackError("解压文件超过大小限制。")
                destination_path = payload / relative
                destination_path.parent.mkdir(parents=True, exist_ok=True)
                with opener() as input_stream, destination_path.open("wb") as output_stream:
                    remaining = size
                    while remaining:
                        chunk = input_stream.read(min(1024 * 1024, remaining))
                        if not chunk:
                            raise PackError(f"压缩包文件不完整：{member}")
                        output_stream.write(chunk)
                        remaining -= len(chunk)
                total += size
                occupied.add(relative)
        return total
    finally:
        if archive is not None:
            archive.close()


def make_installer(recipe, files):
    template = Path(__file__).with_name("installer.sh.in").read_text(encoding="utf-8")
    target_system, target_arch = recipe["target"].split("-")[:2]
    replacements = {
        "@APP@": shlex.quote(recipe["name"]),
        "@VERSION@": shlex.quote(recipe["version"]),
        "@SYSTEM@": shlex.quote(target_system),
        "@ARCH@": shlex.quote(target_arch),
        "@LIBC@": shlex.quote("musl" if recipe["target"].endswith("-musl") else "default"),
        "@FILES@": "\n".join(sorted(files)),
        "@LINKS@": "\n".join(f"{path} {target}" for path, target in sorted(recipe["links"].items())),
    }
    for marker, value in replacements.items():
        template = template.replace(marker, value)
    return template


def check_binary_platform(path, target):
    """Catch mislabeled native binaries without executing cross-platform code."""
    with path.open("rb") as stream:
        header = stream.read(64)
    system, arch = target.split("-")[:2]
    if header.startswith(b"\x7fELF") and len(header) >= 20:
        if system != "linux":
            raise PackError(f"目标是 {system}，但 {path.name} 是 Linux ELF 程序。")
        byte_order = {1: "little", 2: "big"}.get(header[5])
        if byte_order is None:
            raise PackError(f"ELF 字节序无效：{path.name}")
        machine = int.from_bytes(header[18:20], byte_order)
        expected = {"x86_64": 62, "aarch64": 183}[arch]
        if machine != expected:
            raise PackError(f"{path.name} 的 ELF 架构与 {target} 不匹配。")
    elif header[:4] in {b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf"} and len(header) >= 8:
        byte_order = "little" if header[0] == 0xcf else "big"
        machine = int.from_bytes(header[4:8], byte_order)
        if system != "darwin" or machine != {"x86_64": 0x1000007, "aarch64": 0x100000c}[arch]:
            raise PackError(f"{path.name} 的 macOS 程序架构与 {target} 不匹配。")
    elif header.startswith(b"MZ"):
        raise PackError(f"{path.name} 是 Windows 程序，不能装入 Unix 安装包。")


def build_bundle(recipe, output, cache, expected_sha=None):
    safe_name(recipe["name"])
    safe_version(recipe["version"])
    files = set()
    total = 0
    assets = []
    bundle_name = f"{recipe['name']}-{recipe['version']}-{recipe['target']}"
    if output is None:
        output = Path("dist") / (bundle_name + ".tar.gz")
    output = output.expanduser().resolve()
    if output.exists():
        raise PackError(f"输出文件已存在，请选择其他 --output 路径：{output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="offpack-") as temporary:
        bundle = Path(temporary) / bundle_name
        payload = bundle / "payload"
        payload.mkdir(parents=True)
        for index, asset in enumerate(recipe["assets"]):
            checksum = expected_sha if index == 0 and expected_sha else asset.get("sha256")
            asset_path, digest = download(asset["url"], cache, checksum)
            total = collect_files(asset_path, asset, payload, files, total)
            assets.append({"url": asset["url"], "sha256": digest, "size": asset_path.stat().st_size,
                           "upstream_checksum_verified": bool(checksum)})
        for link, target in recipe["links"].items():
            install_path(link)
            if link in files or "/" in target or not re.fullmatch(r"[A-Za-z0-9_.+\-]+", target) or target in {".", ".."}:
                raise PackError(f"无效的快捷链接：{link}")
            resolved = str(PurePosixPath(link).parent / target)
            if resolved not in files:
                raise PackError(f"快捷链接没有对应文件：{link} -> {target}")
        if not any(path.startswith("bin/") for path in files):
            raise PackError("安装包至少需要包含一个 bin/ 下的可执行文件。")
        for path in files:
            if path.startswith("bin/"):
                check_binary_platform(payload / path, recipe["target"])
        manifest = {
            "schema": 1, "name": recipe["name"], "version": recipe["version"],
            "target": recipe["target"], "source_command": recipe.get("source_command"),
            "installer_url": recipe.get("installer_url"), "release_url": recipe.get("release_url"),
            "assets": assets, "links": recipe["links"],
            "files": [{"path": path, "sha256": sha256(payload / path)} for path in sorted(files)],
        }
        (bundle / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        (bundle / "install.sh").write_text(make_installer(recipe, files), encoding="utf-8", newline="\n")
        (bundle / "README.txt").write_text(
            f"{recipe['name']} {recipe['version']} / {recipe['target']}\n\n"
            "Offline install: sh install.sh\n"
            'Custom prefix: sh install.sh --prefix "$HOME/.local"\n'
            "Verify without installing: sh install.sh --check\n"
            "Replace an existing installation: sh install.sh --force\n\n"
            "No network, Python, curl, wget, sudo or package manager is used by install.sh.\n"
            "Required: POSIX sh, standard Unix file utilities, sha256sum or shasum.\n"
            "Extract the outer archive using tar before running install.sh.\n"
            "Bun defaults to BUN_INSTALL or ~/.bun; other packages default to ~/.local.\n"
            "Add the displayed bin directory to PATH. zoxide also needs shell integration.\n"
            'Bash: eval "$(zoxide init bash)"\n'
            'Zsh: eval "$(zoxide init zsh)"\n'
            "Fish: zoxide init fish | source\n\n"
            "See manifest.json for the exact version, sources and SHA-256 digests.\n"
            "Bundle checksums detect corruption. Upstream authenticity is checked only\n"
            "when an expected SHA-256 was supplied while building.\n",
            encoding="utf-8", newline="\n",
        )
        checksum_files = sorted(path for path in bundle.rglob("*") if path.is_file())
        (bundle / "SHA256SUMS").write_text("".join(
            f"{sha256(path)}  {path.relative_to(bundle).as_posix()}\n" for path in checksum_files
        ), encoding="utf-8", newline="\n")
        temporary_output = output.with_name(output.name + ".part")
        try:
            with tarfile.open(temporary_output, "w:gz", compresslevel=6) as archive:
                for path in [bundle] + sorted(bundle.rglob("*")):
                    relative = path.relative_to(bundle.parent).as_posix()
                    info = archive.gettarinfo(str(path), arcname=relative)
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mtime = 0
                    info.mode = 0o755 if path.is_dir() or path.name == "install.sh" or path.relative_to(bundle).as_posix().startswith("payload/bin/") else 0o644
                    if path.is_file():
                        with path.open("rb") as stream:
                            archive.addfile(info, stream)
                    else:
                        archive.addfile(info)
            os.replace(temporary_output, output)
        finally:
            temporary_output.unlink(missing_ok=True)
    print(f"已生成：{output}")
    print(f"版本：{recipe['name']} {recipe['version']}；平台：{recipe['target']}")
    print(f"文件：{output.stat().st_size / 1024 / 1024:.2f} MiB；SHA-256：{sha256(output)}")
    print("将压缩包传到目标机器，然后运行：")
    print(f"  tar -xzf {shlex.quote(output.name)}")
    print(f"  sh {shlex.quote(bundle_name + '/install.sh')} --check")
    print(f"  sh {shlex.quote(bundle_name + '/install.sh')}")
    return output


def inspect_source(source):
    info = parse_source(source)
    if info["url"] is None:
        info["url"] = "https://bun.sh/install" if info["name"] == "bun" else "https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh"
    print(f"脚本：{info['url']}")
    print(f"内置离线适配：{info['name'] or '无；需要配置文件或专门适配'}")
    body = read_url(info["url"]).decode("utf-8", errors="replace")
    pattern = re.compile(r"curl|wget|https?://|\b(?:apt(?:-get)?|dnf|yum|pip3?|npm|cargo|git clone)\b")
    print("下载与依赖相关行（静态查看，不执行脚本）：")
    for number, line in enumerate(body.splitlines(), 1):
        if pattern.search(line):
            print(f"  {number}: {line[:500]}")
    print("这些行仅供分析，不能证明已经收集了所有运行时依赖。")


def main(argv=None):
    parser = argparse.ArgumentParser(description="把在线安装命令打包为无需联网的 Linux/macOS 安装包。")
    parser.add_argument("--version", action="version", version="offpack 0.1.0")
    subparsers = parser.add_subparsers(dest="action", required=True)
    pack = subparsers.add_parser("pack", help="构建离线安装包")
    pack.add_argument("source", nargs="?", help="curl/wget 命令、入口脚本 URL、bun 或 zoxide")
    pack.add_argument("--recipe", type=Path, help="其他软件的 JSON 打包配置")
    pack.add_argument("--target", choices=TARGETS, help="远程目标平台；不根据打包机推断")
    pack.add_argument("--version", dest="package_version", help="固定软件版本；默认为打包时的最新发布版本")
    pack.add_argument("--variant", choices=("baseline", "standard"), default="baseline", help="Bun x86_64 构建，默认兼容较旧 CPU 的 baseline")
    pack.add_argument("--sha256", help="可选的上游资源 SHA-256；只用于单个下载资源")
    pack.add_argument("--output", "-o", type=Path, help="输出 .tar.gz 路径；默认 dist/软件-版本-平台.tar.gz")
    pack.add_argument("--cache-dir", type=Path, default=Path(__file__).parent / ".cache", help="下载缓存与断点目录")
    inspect = subparsers.add_parser("inspect", help="查看任意入口脚本中的下载与依赖，不执行脚本")
    inspect.add_argument("source")
    subparsers.add_parser("probe", help="显示用于查询目标机器平台的离线命令")
    args = parser.parse_args(argv)
    try:
        if args.action == "inspect":
            inspect_source(args.source)
        elif args.action == "probe":
            print("在目标 Linux/macOS 机器执行以下命令，然后选择对应 --target：")
            print("uname -s; uname -m; (ldd --version 2>&1 || true) | head -n 2")
            print("Linux + x86_64 -> linux-x86_64；Linux + aarch64 -> linux-aarch64")
            print("Alpine/musl 系统追加 -musl；Darwin 对应 darwin-x86_64 / darwin-aarch64。")
        else:
            if args.recipe:
                if args.source:
                    raise PackError("source 和 --recipe 请只使用一个。")
                recipe = load_recipe(args.recipe, args.target, args.package_version)
            else:
                if not args.source or not args.target:
                    raise PackError("请提供安装命令和 --target，例如：pack bun --target linux-x86_64")
                source = parse_source(args.source)
                if not source["name"]:
                    raise PackError("此入口尚无内置适配。请先用 inspect 查看脚本，再用 --recipe 配置下载资源与文件映射。")
                recipe = builtin_recipe(source, args.target, args.package_version, args.variant)
            if args.sha256 and len(recipe["assets"]) != 1:
                raise PackError("多个下载资源请分别在配置文件中填写 sha256。")
            build_bundle(recipe, args.output, args.cache_dir.expanduser().resolve(), args.sha256)
    except (PackError, OSError, URLError, HTTPException, ValueError, KeyError, TypeError, tarfile.TarError, zipfile.BadZipFile) as exc:
        log(f"错误：{exc}")
        return 1
    except KeyboardInterrupt:
        log("已取消；下载断点保留在缓存目录。")
        return 130
    return 0


if __name__ == "__main__":
    if os.name == "nt":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
