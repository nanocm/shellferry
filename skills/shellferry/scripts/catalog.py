#!/usr/bin/env python3
"""List, inspect and build portable, pinned conversion recipes."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
from convert import build
from offpack import PackError, safe_name

CATALOG = Path(__file__).resolve().parent.parent / "assets/catalog"


def recipe_path(name):
    safe_name(name)
    path = CATALOG / name / "recipe.json"
    if not path.is_file():
        raise PackError(f"No pinned recipe for {name}; analyze the installer and create an adaptation.")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("list")
    show = sub.add_parser("show")
    show.add_argument("name")
    evidence = sub.add_parser("evidence", help="Match shared prior evidence; no downloads or containers")
    evidence.add_argument("name")
    evidence.add_argument("--os-id", required=True)
    evidence.add_argument("--os-version", required=True)
    make = sub.add_parser("build")
    make.add_argument("name")
    make.add_argument("--output", type=Path, required=True)
    make.add_argument("--cache-dir", type=Path, default=Path.home() / ".cache/offline-install")
    args = parser.parse_args()
    try:
        if args.action == "list":
            for path in sorted(CATALOG.glob("*/recipe.json")):
                recipe = json.loads(path.read_text(encoding="utf-8"))
                print(f"{path.parent.name:16} {recipe['version']:24} {recipe['target']}")
            print("Pinned examples; inspect notes and validation scope before reusing.")
        elif args.action == "show":
            recipe = json.loads(recipe_path(args.name).read_text(encoding="utf-8"))
            print(json.dumps({key: recipe.get(key) for key in ["name", "version", "target", "requires", "env", "args", "repeat_args", "smoke", "notes"]}, ensure_ascii=False, indent=2))
        elif args.action == "evidence":
            from evidence import check
            print(json.dumps(check(recipe_path(args.name), args.os_id, args.os_version), ensure_ascii=False, indent=2))
        else:
            build(recipe_path(args.name), args.output.resolve(), args.cache_dir.expanduser())
        return 0
    except (PackError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if os.name == "nt":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
