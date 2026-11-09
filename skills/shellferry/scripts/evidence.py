#!/usr/bin/env python3
"""Publishable validation records and conservative matching of prior results.

Records are provenance claims by the repository publisher, not signatures or
proof that a newly built archive has already run. Local caches are not required.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

from offpack import PackError, safe_path, sha256

DIRECTORY = Path(__file__).resolve().parent.parent / "references/evidence"


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def load_relative(directory, path, expected_hash):
    safe_path(path)
    file = (directory / path).resolve()
    if not file.is_relative_to(directory.resolve()) or sha256(file) != expected_hash:
        raise PackError(f"Evidence file changed or escaped its directory: {path}")
    return json.loads(file.read_text(encoding="utf-8"))


def environment_identity(report):
    environment = report.get("environment", "")
    identity = {}
    for field, key in (("ID", "os_id"), ("VERSION_ID", "os_version")):
        match = re.search(r"^" + field + r"=([^\n]+)$", environment, re.MULTILINE)
        if match:
            identity[key] = match[1].strip().strip('"')
    return identity


def record(bundle, report_file, directory=DIRECTORY):
    manifest_file = bundle / "manifest.json"
    sums_file = bundle / "SHA256SUMS"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    report = json.loads(report_file.read_text(encoding="utf-8"))
    if report.get("status") != "passed" or report.get("network") != "none" or not report.get("archive_roundtrip"):
        raise PackError("Only passed archive roundtrip tests with network=none can be recorded.")
    if report["manifest_sha256"] != sha256(manifest_file) or report["checksum_list_sha256"] != sha256(sums_file):
        raise PackError("Report does not describe this bundle.")
    for field in ("name", "version", "target"):
        if report.get(field) != manifest.get(field):
            raise PackError(f"Report identity mismatch: {field}")
    # Check the actual files, rather than accepting an old manifest next to changed contents.
    for line in sums_file.read_text(encoding="utf-8").splitlines():
        digest, path = line.split("  ", 1)
        safe_path(path)
        item = (bundle / path).resolve()
        if not item.is_relative_to(bundle.resolve()) or sha256(item) != digest:
            raise PackError(f"Bundle file changed: {path}")
    if report.get("builder") and report["builder"] != manifest.get("builder"):
        raise PackError("Builder identity differs between manifest and report.")
    # Retain historical records honestly: no code hashes or dates are invented.
    bound = bool(manifest.get("builder") and report.get("verifier") and report.get("verified_at"))
    identifier = sha256(report_file)[:24]
    relative_report = f"records/{identifier}/report.json"
    relative_manifest = f"records/{identifier}/manifest.json"
    (directory / relative_report).parent.mkdir(parents=True, exist_ok=True)
    # Preserve original bytes: JSON reserialization or CRLF conversion breaks
    # the archive/report hash binding, especially across Windows and Linux.
    (directory / relative_report).write_bytes(report_file.read_bytes())
    (directory / relative_manifest).write_bytes(manifest_file.read_bytes())
    entry = {"id": identifier, "name": manifest["name"], "version": manifest["version"],
             "target": manifest["target"], "environment": environment_identity(report),
             "provenance_level": "code-bound" if bound else "historical-unbound-code",
             "report": relative_report, "report_sha256": sha256(directory / relative_report),
             "manifest": relative_manifest, "manifest_sha256": sha256(directory / relative_manifest)}
    index_path = directory / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {"schema": 1, "records": []}
    index["records"] = [item for item in index["records"] if item["id"] != identifier] + [entry]
    index["records"].sort(key=lambda item: (item["name"], item["environment"].get("os_version", ""), item["id"]))
    write_json(index_path, index)
    return entry


def check(recipe_file, os_id, os_version, directory=DIRECTORY):
    recipe = json.loads(recipe_file.read_text(encoding="utf-8"))
    recipe_digest = sha256(recipe_file)
    scripts = Path(__file__).resolve().parent
    builder = {name: sha256(scripts / name) for name in ("convert.py", "offpack.py")}
    verifier = {name: sha256(scripts / name) for name in ("verify.py", "offpack.py")}
    input_issues = []
    for item in recipe.get("scripts", []):
        if not item.get("sha256"):
            input_issues.append("script digest missing")
        elif item.get("source") and sha256((recipe_file.parent / item["source"]).resolve()) != item["sha256"]:
            input_issues.append("local source differs from pinned script")
    for item in recipe.get("resources", []):
        if not item.get("sha256"):
            input_issues.append("resource digest missing")
        elif item.get("source") and sha256((recipe_file.parent / item["source"]).resolve()) != item["sha256"]:
            input_issues.append("local resource differs from pinned resource")
    index_path = directory / "index.json"
    entries = json.loads(index_path.read_text(encoding="utf-8"))["records"] if index_path.exists() else []
    results = []
    for entry in entries:
        if entry["name"] != recipe["name"]:
            continue
        reasons = list(input_issues)
        try:
            report = load_relative(directory, entry["report"], entry["report_sha256"])
            manifest = load_relative(directory, entry["manifest"], entry["manifest_sha256"])
        except (PackError, OSError, ValueError) as exc:
            results.append({"id": entry["id"], "match": False, "reasons": [str(exc)]})
            continue
        if any(manifest.get(field) != recipe.get(field) for field in ("name", "version", "target")):
            reasons.append("software version or target differs")
        if environment_identity(report) != {"os_id": os_id, "os_version": os_version}:
            reasons.append("distribution or version differs")
        if manifest.get("recipe_sha256") != recipe_digest:
            reasons.append("recipe changed")
        if manifest.get("builder") != builder:
            reasons.append("builder identity missing or changed")
        if report.get("verifier") != verifier:
            reasons.append("verifier identity missing or changed")
        if not report.get("verified_at"):
            reasons.append("verification timestamp not recorded")
        if report.get("manifest_sha256") != entry["manifest_sha256"]:
            reasons.append("report does not bind the stored manifest")
        if report.get("builder") != manifest.get("builder"):
            reasons.append("report and manifest builder identities differ")
        if report.get("status") != "passed" or report.get("network") != "none" or not report.get("archive_roundtrip"):
            reasons.append("validation scope insufficient")
        results.append({"id": entry["id"], "match": not reasons, "reasons": reasons,
                        "verified_at": report.get("verified_at"), "image": report.get("image"),
                        "image_id": report.get("image_id"), "image_digests": report.get("image_digests"),
                        "prerequisites": manifest.get("requires", []), "runtime": manifest.get("runtime", {}),
                        "notes": manifest.get("notes", []), "archive_sha256": report.get("archive_sha256"),
                        "report": entry["report"]})
    return {"name": recipe["name"], "version": recipe["version"], "target": recipe["target"],
            "requested_environment": {"os_id": os_id, "os_version": os_version},
            "has_matching_prior_evidence": any(item["match"] for item in results),
            "status": "prior-evidence-only", "records": results,
            "meaning": "Reuse the recorded conversion decisions within the listed prerequisites. This does not validate a new archive or replace an explicitly requested fresh test. No local download cache is needed."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    add = sub.add_parser("record")
    add.add_argument("--bundle", type=Path, required=True)
    add.add_argument("--report", type=Path, required=True)
    add.add_argument("--directory", type=Path, default=DIRECTORY)
    query = sub.add_parser("check")
    query.add_argument("--recipe", type=Path, required=True)
    query.add_argument("--os-id", required=True)
    query.add_argument("--os-version", required=True)
    query.add_argument("--directory", type=Path, default=DIRECTORY)
    args = parser.parse_args()
    try:
        result = record(args.bundle, args.report, args.directory) if args.action == "record" else check(args.recipe, args.os_id, args.os_version, args.directory)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (PackError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
