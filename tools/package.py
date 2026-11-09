#!/usr/bin/env python3
"""Build a portable source/skill distribution without caches or local Git state."""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ("README.md", "README.zh-CN.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "CONTRIBUTING.md", "VERSION", "plugin.json", "install.py", ".gitattributes", ".gitignore", ".github", ".claude-plugin", "skills", "docs", "tools", "tests")
EXCLUDE = {"__pycache__", ".git", ".cache", "dist", "work", ".venv"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    subprocess.run([sys.executable, str(ROOT / "tools/check_repo.py")], check=True)
    subprocess.run([sys.executable, str(ROOT / "tools/coverage.py"), "--check", "--minimum", "105"], check=True)
    version = (ROOT / "VERSION").read_text().strip()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    archive = args.output_dir / f"shellferry-{version}.zip"
    files = []
    for name in INCLUDE:
        path = ROOT / name
        files.extend([path] if path.is_file() else [file for file in path.rglob("*") if file.is_file()])
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for path in sorted(files):
            relative = path.relative_to(ROOT)
            if any(part in EXCLUDE for part in relative.parts) or path.suffix == ".pyc":
                continue
            if path.is_symlink():
                raise ValueError(f"Unexpected symlink: {relative}")
            info = zipfile.ZipInfo(f"shellferry-{version}/" + relative.as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100755 if path.suffix == ".sh" else 0o100644) << 16
            package.writestr(info, path.read_bytes())
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_name(archive.name + ".sha256").write_text(f"{checksum}  {archive.name}\n", encoding="utf-8")
    with zipfile.ZipFile(archive) as package:
        if package.testzip() is not None:
            raise ValueError("Corrupt release archive")
    print(f"{archive}\nSHA-256: {checksum}")


if __name__ == "__main__":
    main()
