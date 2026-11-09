#!/usr/bin/env python3
"""Test real Skills CLI and Claude plugin installation in isolated directories."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILLS_VERSION = "1.7.6"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(folder):
    return {
        path.relative_to(folder).as_posix(): digest(path)
        for path in folder.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }


def isolated_environment(base):
    home = base / "home"
    project = base / "project"
    home.mkdir(parents=True)
    project.mkdir()
    env = dict(os.environ)
    env.update({
        "HOME": str(home), "USERPROFILE": str(home),
        "CLAUDE_CONFIG_DIR": str(home / ".claude"),
        "CODEX_HOME": str(home / ".codex"),
        "XDG_CONFIG_HOME": str(home / ".config"),
        "DISABLE_TELEMETRY": "1", "DO_NOT_TRACK": "1", "NO_COLOR": "1",
    })
    return home, project, env


def run(command, project, env):
    result = subprocess.run(command, cwd=project, env=env, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=120)
    if result.returncode:
        raise RuntimeError(f"{Path(command[0]).name} failed ({result.returncode}): "
                           + (result.stdout + result.stderr)[-5000:])
    return result.stdout


def check_payload(path, expected):
    actual = inventory(path)
    if actual != expected:
        missing = sorted(expected.keys() - actual.keys())
        extra = sorted(actual.keys() - expected.keys())
        changed = sorted(name for name in expected.keys() & actual.keys()
                         if expected[name] != actual[name])
        raise ValueError(f"Installed payload differs: missing={missing}, extra={extra}, changed={changed}")
    result = subprocess.run(
        [sys.executable, str(path / "scripts/catalog.py"), "evidence", "zoxide",
         "--os-id", "ubuntu", "--os-version", "22.04"],
        capture_output=True, text=True, encoding="utf-8", timeout=30, check=True)
    if not json.loads(result.stdout)["has_matching_prior_evidence"]:
        raise ValueError("Relocated evidence no longer matches")
    return {"status": "passed", "files": len(expected), "relocated_evidence": "passed"}


def extract(archive, destination):
    destination.mkdir()
    root = destination.resolve()
    with zipfile.ZipFile(archive) as package:
        for info in package.infolist():
            target = (destination / info.filename).resolve()
            if not target.is_relative_to(root) or (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("Unsafe archive member")
        package.extractall(destination)
    folders = [p for p in destination.iterdir() if p.is_dir()]
    if len(folders) != 1 or not (folders[0] / "skills/shellferry/SKILL.md").is_file():
        raise ValueError("Expected a complete Shellferry release archive")
    return folders[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    parser.add_argument("--archive", type=Path, default=ROOT / "dist" / f"shellferry-{version}.zip")
    parser.add_argument("--output", type=Path, default=ROOT / "dist/installation-checks.json")
    parser.add_argument("--require-claude", action="store_true")
    args = parser.parse_args()
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "status": "failed",
              "scope": "Local archive installation; no remote GitHub fetch or agent conversation", "checks": {}}
    qa = (ROOT / "work" / f"installation-check-{uuid.uuid4().hex[:10]}").resolve()
    qa.mkdir(parents=True)
    try:
        report["archive_sha256"] = digest(args.archive)
        source = extract(args.archive.resolve(), qa / "extracted")
        expected = inventory(source / "skills/shellferry")
        npx = shutil.which("npx")
        if not npx:
            raise RuntimeError("Node.js 22.20+ and npx are required")
        report["skills_cli_version"] = SKILLS_VERSION
        for scope in ("project", "global"):
            home, project, env = isolated_environment(qa / f"npx-{scope}")
            options = ["--copy"] if scope == "project" else ["--global"]
            output = run([npx, "--yes", f"skills@{SKILLS_VERSION}", "add", str(source),
                          "--skill", "shellferry", "--agent", "codex", "claude-code",
                          *options, "--yes", "--json"], project, env)
            installs = json.loads(output)
            if len(installs) != 1 or installs[0]["status"] != "installed":
                raise ValueError("Skills CLI did not install exactly one skill")
            base = project if scope == "project" else home
            for host, directory in (("codex", ".agents"), ("claude", ".claude")):
                report["checks"][f"npx_{scope}_{host}"] = check_payload(
                    base / directory / "skills/shellferry", expected)
            report["checks"][f"npx_{scope}_mode"] = installs[0]["mode"]

        claude = shutil.which("claude")
        if claude:
            home, project, env = isolated_environment(qa / "claude-plugin")
            report["claude_version"] = run([claude, "--version"], project, env).strip()
            for filename in ("plugin.json", "marketplace.json"):
                result = json.loads(run([claude, "plugin", "validate",
                    str(source / ".claude-plugin" / filename), "--strict", "--json"], project, env))
                if not result["success"]:
                    raise ValueError(f"Claude rejected {filename}")
            run([claude, "plugin", "marketplace", "add", str(source), "--json"], project, env)
            run([claude, "plugin", "install", "shellferry@shellferry", "--json"], project, env)
            installed = json.loads((home / ".claude/plugins/installed_plugins.json").read_text(encoding="utf-8"))
            path = Path(installed["plugins"]["shellferry@shellferry"][0]["installPath"]).resolve()
            if not path.is_relative_to(home.resolve()):
                raise ValueError("Claude installed outside the isolated home")
            report["checks"]["claude_plugin"] = check_payload(path / "skills/shellferry", expected)
            report["checks"]["claude_manifests"] = "passed"
        elif args.require_claude:
            raise RuntimeError("Claude Code CLI is required but unavailable")
        else:
            report["checks"]["claude_plugin"] = {"status": "skipped", "reason": "Claude CLI unavailable"}
        report["status"] = "passed"
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
        report["error"] = str(exc).replace(str(qa), "<isolated-test>").replace(str(ROOT), "<repository>")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
