#!/usr/bin/env python3
"""Install, update, inspect, or remove a local Shellferry skill. No network calls."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import uuid

NAME = "shellferry"
RECEIPT = ".shellferry-install.json"
ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "skills" / NAME
IGNORED = {"__pycache__", ".git", ".cache"}


class InstallError(Exception):
    pass


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(directory):
    files = {}
    for path in sorted(directory.rglob("*")):
        relative = path.relative_to(directory)
        if any(part in IGNORED for part in relative.parts) or path.suffix == ".pyc" or path.name == RECEIPT:
            continue
        if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
            raise InstallError(f"Symlink/junction in skill payload: {relative}")
        if path.is_file():
            files[relative.as_posix()] = digest(path)
    return files


def destination(args):
    if args.dest:
        parent = args.dest.expanduser().absolute()
    elif args.scope == "project":
        if args.host == "codex-legacy":
            raise InstallError("Project scope uses --host codex (.agents/skills), not codex-legacy.")
        project = args.project_dir.expanduser().resolve()
        if not project.is_dir():
            raise InstallError(f"Project directory does not exist: {project}")
        parent = project / (".claude" if args.host == "claude" else ".agents") / "skills"
    elif args.host == "codex-legacy":
        parent = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "skills"
    else:
        parent = Path.home() / (".claude" if args.host == "claude" else ".agents") / "skills"
    parent = parent.resolve()
    target = parent / NAME
    if target.is_symlink() or getattr(target, "is_junction", lambda: False)():
        raise InstallError(f"Refusing to replace a symlink/junction: {target}")
    if target.resolve().parent != parent:
        raise InstallError("Resolved skill directory escaped the intended destination.")
    if target == SOURCE or target in SOURCE.parents or SOURCE in target.parents:
        raise InstallError("Install destination must not overlap the source checkout.")
    return target


def read_receipt(target):
    path = target / RECEIPT
    if not path.is_file():
        raise InstallError(f"Existing directory is not managed by this installer: {target}. Use a different destination or move it yourself.")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("name") != NAME or data.get("schema") != 1:
        raise InstallError("Unrecognized installation receipt.")
    return data


def backup(target):
    # One checked directory rename on the same filesystem; never recursive deletion.
    resolved = target.resolve()
    if resolved.parent != target.parent.resolve() or target.name != NAME:
        raise InstallError("Backup source failed its workspace boundary check.")
    base = target.parent.parent / ".shellferry-backups"
    base.mkdir(parents=True, exist_ok=True)
    base = base.resolve()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    saved = base / f"{NAME}-{stamp}-{uuid.uuid4().hex[:8]}"
    if saved.resolve().parent != base or saved.exists():
        raise InstallError("Invalid backup destination.")
    target.rename(saved)
    return saved


def perform(args):
    target = destination(args)
    if args.action == "status":
        if not target.exists():
            return {"status": "not-installed", "path": str(target)}
        receipt = read_receipt(target)
        changed = inventory(target) != receipt["files"]
        return {"status": "modified" if changed else "installed", "path": str(target), "version": receipt["version"]}
    existing = None
    if target.exists():
        existing = read_receipt(target)
        changed = inventory(target) != existing["files"]
        if changed and not args.force:
            raise InstallError("Installed files have local changes. Use --force to preserve them in a backup and continue.")
    if args.action == "uninstall":
        if existing is None:
            return {"status": "not-installed", "path": str(target)}
        if args.dry_run:
            return {"status": "would-uninstall", "path": str(target)}
        saved = backup(target)
        return {"status": "uninstalled", "path": str(target), "backup": str(saved)}

    if not (SOURCE / "SKILL.md").is_file():
        raise InstallError("Missing skills/shellferry/SKILL.md; run from a complete source or release package.")
    source_files = inventory(SOURCE)
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if existing and existing["version"] == version and existing["files"] == source_files and inventory(target) == source_files:
        return {"status": "already-current", "path": str(target), "version": version}
    if existing and args.action != "update":
        raise InstallError("A different managed version is installed. Run: python install.py update")
    if args.dry_run:
        return {"status": "would-install" if not existing else "would-update", "path": str(target), "version": version, "file_count": len(source_files)}

    target.parent.mkdir(parents=True, exist_ok=True)
    saved = None
    with tempfile.TemporaryDirectory(prefix=".shellferry-stage-", dir=target.parent) as temporary:
        stage = Path(temporary) / NAME
        stage.mkdir()
        for name in source_files:
            output = stage / name
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE / name, output)
        if inventory(stage) != source_files:
            raise InstallError("Copied files did not match the source.")
        record = {"schema": 1, "name": NAME, "version": version, "files": source_files}
        (stage / RECEIPT).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
        if existing:
            saved = backup(target)
        try:
            stage.rename(target)
        except OSError:
            if saved is not None and not target.exists():
                saved.rename(target)
            raise
    return {"status": "updated" if existing else "installed", "path": str(target), "version": version,
            **({"backup": str(saved)} if saved else {})}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", choices=["install", "update", "status", "uninstall"], default="install")
    parser.add_argument("--host", choices=["codex", "codex-legacy", "claude"], default="codex")
    parser.add_argument("--scope", choices=["user", "project"], default="user")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    parser.add_argument("--dest", type=Path, help="Explicit parent skills directory; installs a shellferry child")
    parser.add_argument("--force", action="store_true", help="Allow locally modified managed installs; back them up first")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        result = perform(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if result["status"] in {"installed", "updated", "already-current"}:
            invocation = "/shellferry in Claude Code" if args.host == "claude" else "$shellferry in Codex"
            print(f"Invoke {invocation}. If it does not appear on your next turn, restart your host.")
        return 0
    except (InstallError, OSError, ValueError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if os.name == "nt":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
