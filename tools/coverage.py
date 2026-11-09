#!/usr/bin/env python3
"""Check and render catalog coverage from matching, hash-bound test evidence."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/shellferry"
REFERENCES = SKILL / "references"
sys.path.insert(0, str(SKILL / "scripts"))
from evidence import check
from offpack import sha256


def collect():
    catalog = SKILL / "assets/catalog"
    index = json.loads((REFERENCES / "evidence/index.json").read_text(encoding="utf-8"))
    descriptions = json.loads((REFERENCES / "coverage-descriptions.json").read_text(encoding="utf-8"))
    records = []
    missing = []
    for path in sorted(catalog.glob("*/recipe.json")):
        recipe = json.loads(path.read_text(encoding="utf-8"))
        environments = sorted({(e["environment"]["os_id"], e["environment"]["os_version"])
                               for e in index["records"] if e["name"] == recipe["name"]})
        matches = []
        for os_id, version in environments:
            result = check(path, os_id, version)
            for entry in result["records"]:
                if entry["match"]:
                    matches.append({"os_id": os_id, "os_version": version,
                                    **{key: entry[key] for key in ("id", "report", "image", "image_id", "archive_sha256", "verified_at")}})
        if not matches:
            missing.append(path.parent.name)
        detail = descriptions.get(path.parent.name, {})
        if not detail.get("functional_summary"):
            raise ValueError(f"Missing functional summary: {path.parent.name}")
        records.append({"recipe": path.parent.name, "name": recipe["name"], "version": recipe["version"],
                        "target": recipe["target"], "recipe_sha256": sha256(path),
                        "kind": detail.get("kind", "shell-installer"),
                        "functional_summary": detail["functional_summary"],
                        "requires": recipe.get("requires", []), "runtime": recipe.get("runtime", {}),
                        "notes": recipe.get("notes", []), "matching_evidence": matches})
    software = {r["name"] for r in records if r["matching_evidence"]}
    return {"schema": 1, "status": "passed" if not missing else "incomplete",
            "software_count": len(software), "recipe_count": len(records),
            "kind_counts": dict(sorted(Counter(r["kind"] for r in records).items())),
            "evidence_record_count": len(index["records"]), "missing_evidence": missing,
            "meaning": "Each listed match binds the current recipe, inputs, builder and verifier to a previous passed archive test. It does not execute newly built bundles.",
            "records": records}


def render(data):
    lines = ["# Validation matrix", "",
             f"**{data['software_count']} distinct software packages, {data['recipe_count']} recipes.** "
             "Each recipe has matching evidence for its current inputs and builder/verifier code. "
             "Results describe the exact pinned version, prerequisites, and functional scope below.", "",
             "Tests run through Podman in WSL2 with `--network none`, user `1000:1000`, a clean HOME, "
             "a prefix containing spaces, read-only bundle mounts, and dropped capabilities. "
             "The verifier extracts each final archive into a fresh directory, checks integrity, installs, "
             "runs functional assertions, and repeats installation. Passing establishes completion without "
             "external connectivity. Detecting all attempted native network calls requires separate tracing.", "",
             "Most new cases use Ubuntu 22.04. Some baseline cases use Ubuntu 26.04. "
             "Prepared images include the tools listed in their Containerfiles; target machines must meet "
             "each recipe's prerequisites. Python, Rust, or C build tools are present only where declared. "
             "Managers, cloud clients, and cluster tools are tested within the local scope stated below.", "",
             "Installation testing is optional when building a user bundle. These published catalog entries "
             "require passing evidence; a new build retains its own status. See "
             "[verification modes](verification.md) and [evidence reuse](shared-evidence.md).", "",
             "| Recipe | Version | Path | Environment | Functional check | Evidence |",
             "| --- | --- | --- | --- | --- | --- |"]
    for record in data["records"]:
        latest = sorted(record["matching_evidence"], key=lambda e: e["verified_at"] or "", reverse=True)
        environments = ", ".join(sorted({e['os_id'] + ' ' + e['os_version'] for e in latest}))
        report = latest[0]["report"] if latest else None
        evidence = f"[passed](evidence/{report})" if report else "Missing"
        description = record["functional_summary"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| [{record['recipe']}](../assets/catalog/{record['recipe']}/recipe.json) | "
                     f"{record['version']} | {record['kind']} | {environments} | {description} | {evidence} |")
    lines += ["", "## Evidence and reproduction", "",
              "[coverage.json](coverage.json) records every matching report, image identity, prerequisite, "
              "and scope note. [Scope and prerequisites](known-limitations.md) describes functional coverage, "
              "installer adaptations, and failed candidates. The index retains historical records; "
              "current matches require the recorded code and recipe hashes.", "",
              "Check the catalog, or reproduce a recorded installation test with a prepared matching image:", "",
              "```sh", "python3 tools/coverage.py --check --minimum 105", "",
              "python3 skills/shellferry/scripts/catalog.py build zoxide --output work/zoxide",
              "python3 skills/shellferry/scripts/convert.py archive work/zoxide --output dist/zoxide.tar.gz",
              "python3 skills/shellferry/scripts/verify.py dist/zoxide.tar.gz \\",
              "  --engine podman --image docker.io/library/ubuntu:22.04 --output dist/zoxide.validation.json", "```", "",
              "The catalog includes converted online shell installers, source installers with their companion "
              "trees, and Python installer adaptations. These paths are labeled separately. Version and "
              "environment changes require new evidence before entering the verified catalog. Unprepared project dependencies, remote services, "
              "other CPU architectures, macOS, Alpine, full systemd behavior, and kernel features are outside "
              "the recorded scope unless a row explicitly includes them.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check current evidence and the generated inventory without rewriting it")
    parser.add_argument("--minimum", type=int, default=105)
    args = parser.parse_args()
    data = collect()
    if data["missing_evidence"] or data["software_count"] < args.minimum:
        raise SystemExit(json.dumps({k: v for k, v in data.items() if k != "records"}, indent=2))
    output = REFERENCES / "coverage.json"
    if args.check:
        if not output.is_file() or json.loads(output.read_text(encoding="utf-8")) != data:
            raise SystemExit("Coverage inventory is stale; run python tools/coverage.py")
        matrix = REFERENCES / "validation-matrix.md"
        if not matrix.is_file() or matrix.read_text(encoding="utf-8") != render(data):
            raise SystemExit("Validation matrix is stale; run python tools/coverage.py")
    else:
        output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        (REFERENCES / "validation-matrix.md").write_text(render(data), encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in data.items() if k != "records"}, indent=2))


if __name__ == "__main__":
    main()
