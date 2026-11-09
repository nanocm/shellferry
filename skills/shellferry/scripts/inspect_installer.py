#!/usr/bin/env python3
"""Save an installer snapshot and static analysis hints without executing shell."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlparse
from offpack import PackError, read_url, validate_url


PATTERNS = {
    "network": r"\b(?:curl|wget|fetch|aria2c|git\s+clone)\b|https?://",
    "next_stage": r"\beval\b|\bsource\b|\b(?:bash|sh)\s|\bexec\b|rustup-init|install-ping|shell-setup",
    "dependency": r"\b(?:apt(?:-get)?|dnf|yum|apk|pip3?|npm|pnpm|cargo|make|cmake|unzip|openssl|xz)\b",
    "target": r"uname|ldd|os-release|alpine-release|avx|aarch64|x86_64|musl|glibc",
    "side_effect": r"sudo|systemctl|\.bashrc|\.zshrc|telemetry|analytics|completions|chmod|chown",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Local script, HTTPS URL, or command text (never executed)")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise PackError("Output directory exists; choose a new snapshot directory.")
        source = args.source
        is_local = False
        try:
            is_local = Path(source).is_file()
        except OSError:
            pass
        source_url = None
        if is_local:
            body = Path(source).read_bytes()
        else:
            candidates = re.findall(r"https://[^\s\"'<>|)]+", source)
            if len(candidates) != 1:
                raise PackError("Provide a single entry script URL or local script; manually analyze multi-URL commands.")
            source_url = validate_url(candidates[0])
            body = read_url(source_url)
        text = body.decode("utf-8-sig").replace("\r\n", "\n")
        hints = []
        for number, line in enumerate(text.splitlines(), 1):
            matches = [name for name, pattern in PATTERNS.items() if re.search(pattern, line)]
            if matches:
                hints.append({"line": number, "categories": matches, "text": line})
        urls = sorted(set(re.findall(r"https?://[^\s\"'<>`]+", text)))
        report = {"source": source, "entry_url": source_url, "sha256": hashlib.sha256(body).hexdigest(),
                  "bytes": len(body), "hints": hints, "candidate_urls": urls,
                  "status": "static-hints-only", "limitations": "Dynamic URLs, later scripts, native bootstrap downloads and dependency closure require analysis and offline execution."}
        args.output.mkdir(parents=True)
        (args.output / "original.sh").write_bytes(body)
        (args.output / "analysis.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"output": str(args.output.resolve()), "sha256": report["sha256"], "hint_lines": len(hints), "status": report["status"]}, ensure_ascii=False, indent=2))
        return 0
    except (PackError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if os.name == "nt":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
