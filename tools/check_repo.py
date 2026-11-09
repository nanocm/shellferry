#!/usr/bin/env python3
"""Validate the portable repository and internal file/hash bindings. No network."""
from __future__ import annotations
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/shellferry"
sys.path.insert(0, str(SKILL / "scripts"))
from convert import validate_recipe
from offpack import sha256


def check():
    errors = []
    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    if manifest.get("name") != "shellferry" or manifest.get("version") != (ROOT / "VERSION").read_text().strip():
        errors.append("Plugin identity/version mismatch")
    claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    if any(claude.get(key) != manifest.get(key) for key in ("name", "version")):
        errors.append("Claude plugin identity/version mismatch")
    if claude.get("skills") != "./skills/":
        errors.append("Claude plugin must load the shared skills directory")
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    plugins = marketplace.get("plugins", [])
    if marketplace.get("name") != "shellferry" or len(plugins) != 1 or plugins[0].get("name") != "shellferry" or plugins[0].get("source") != "./":
        errors.append("Claude marketplace must resolve shellferry to the package root")
    frontmatter = (SKILL / "SKILL.md").read_text(encoding="utf-8").split("---", 2)
    if len(frontmatter) != 3 or not re.search(r"^name: shellferry$", frontmatter[1], re.MULTILINE):
        errors.append("Invalid skill name/frontmatter")
    for path in (ROOT / "LICENSE", ROOT / "README.md", ROOT / "README.zh-CN.md", ROOT / "THIRD_PARTY_NOTICES.md"):
        if not path.is_file():
            errors.append(f"Missing {path.name}")
    recipes = list((SKILL / "assets/catalog").glob("*/recipe.json"))
    names = set()
    for path in recipes:
        try:
            recipe = json.loads(path.read_text(encoding="utf-8"))
            validate_recipe(recipe)
            names.add(recipe["name"])
            for category in ("scripts", "resources"):
                for item in recipe.get(category, []):
                    if not re.fullmatch(r"[a-f0-9]{64}", item.get("sha256", "")):
                        errors.append(f"{path.parent.name}: unpinned {category} entry")
                    if item.get("source"):
                        source = (path.parent / item["source"]).resolve()
                        if Path(item["source"]).is_absolute() or not source.is_relative_to(SKILL.resolve()):
                            errors.append(f"{path.parent.name}: nonportable source")
                        elif sha256(source) != item["sha256"]:
                            errors.append(f"{path.parent.name}: source digest mismatch")
                    if category == "resources" and item.get("source"):
                        errors.append(f"{path.parent.name}: downloaded resource tied to a local source")
        except (ValueError, KeyError, OSError) as exc:
            errors.append(f"{path}: {exc}")
    evidence = SKILL / "references/evidence"
    index = json.loads((evidence / "index.json").read_text(encoding="utf-8"))
    for entry in index["records"]:
        for kind in ("report", "manifest"):
            path = (evidence / entry[kind]).resolve()
            if not path.is_relative_to(evidence.resolve()) or sha256(path) != entry[kind + "_sha256"]:
                errors.append(f"Evidence changed: {entry['id']} {kind}")
    inventory = json.loads((SKILL / "third-party.json").read_text(encoding="utf-8"))
    license_files = []
    components = {item["component"] for item in inventory["components"]}
    for component in inventory["components"]:
        for item in component["files"]:
            path = (SKILL / item["path"]).resolve()
            license_files.append(path)
            if not path.is_relative_to((SKILL / "LICENSES").resolve()) or not path.is_file():
                errors.append(f"Invalid license path: {item['path']}")
            elif sha256(path) != item["sha256"] or path.stat().st_size != item["size"]:
                errors.append(f"License text changed: {item['path']}")
    covered_sources = set()
    for item in inventory["catalog_sources"]:
        if item.get("distribution") in {"vendored-source", "authored-source"}:
            path = (SKILL / item["path"]).resolve()
            covered_sources.add(path)
            if not path.is_relative_to((SKILL / "assets/catalog").resolve()) or not path.is_file():
                errors.append(f"Invalid inventoried source: {item['path']}")
            elif sha256(path) != item["sha256"]:
                errors.append(f"Source provenance digest changed: {item['path']}")
        for name in item.get("license_components", []):
            if name not in components:
                errors.append(f"Unknown license component: {name}")
    for path in (SKILL / "assets/catalog").glob("*/sources/*"):
        if path.is_file() and path.resolve() not in covered_sources:
            errors.append(f"Source missing from license inventory: {path.relative_to(SKILL)}")
    # Verify Git's effective attributes, including nested attribute files.
    # Normalizing a snapshot changes the bytes referenced by published evidence.
    git_probe = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=ROOT, capture_output=True, text=True) if shutil.which("git") else None
    if git_probe is not None and git_probe.returncode == 0 and Path(git_probe.stdout.strip()).resolve() == ROOT.resolve():
        pinned = [p.relative_to(ROOT).as_posix() for p in recipes]
        pinned += [p.relative_to(ROOT).as_posix() for p in (SKILL / "assets/catalog").glob("*/sources/*") if p.is_file()]
        pinned += [(evidence / entry["report"]).relative_to(ROOT).as_posix() for entry in index["records"]]
        pinned += [(evidence / entry["manifest"]).relative_to(ROOT).as_posix() for entry in index["records"]]
        pinned += [path.relative_to(ROOT.resolve()).as_posix() for path in license_files]
        attrs = subprocess.run(["git", "check-attr", "text", "--stdin"], input=("\n".join(pinned) + "\n").encode("utf-8"), cwd=ROOT, capture_output=True, check=True)
        for line in attrs.stdout.decode("utf-8").splitlines():
            if not line.endswith(": text: unset"):
                errors.append(f"Hash-bound file can be normalized by Git: {line}")
    # Check real local documentation links, omitting examples inside code fences.
    for path in list(ROOT.glob("*.md")) + list((ROOT / "docs").rglob("*.md")) + list(SKILL.glob("*.md")) + list((SKILL / "references").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        outside = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        for match in re.finditer(r"\]\(([^)]+)\)", outside):
            target = match[1].strip("<>").split("#", 1)[0]
            if not target or urlparse(target).scheme or target.startswith("/"):
                continue
            if not (path.parent / unquote(target)).exists():
                errors.append(f"Broken link in {path.relative_to(ROOT)}: {target}")
    # Do not scan upstream shell content for generic names; only machine-path patterns.
    for base in (ROOT / "docs", SKILL):
        for path in base.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix not in {".md", ".json", ".yaml", ".py"}:
                continue
            text = path.read_text(encoding="utf-8")
            if re.search(r"C:[/\\]+Users[/\\]+cms|D:[/\\]+A_gpt|/mnt/[cd]/(?:A_gpt|Users/cms)", text):
                errors.append(f"Personal machine path in {path.relative_to(ROOT)}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(json.dumps({"status": "passed", "recipes": len(recipes), "software": len(names), "evidence_records": len(index["records"])}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(check())
