"""Evidence reuse must become ineligible when relevant inputs change."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from convert import build
from evidence import check, record
from offpack import PackError, sha256
from test_convert import fixture


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "original.sh").write_text('#!/bin/sh\nmkdir -p "$OFFLINE_PREFIX"\n')
        recipe = fixture()
        recipe["scripts"][0]["sha256"] = sha256(self.root / "original.sh")
        self.recipe = self.root / "recipe.json"
        self.recipe.write_text(json.dumps(recipe))
        self.bundle = self.root / "bundle"
        with contextlib.redirect_stdout(io.StringIO()):
            build(self.recipe, self.bundle, self.root / "cache")
        manifest = json.loads((self.bundle / "manifest.json").read_text())
        scripts = Path(__file__).resolve().parents[1]
        self.report = {"name": "fixture", "version": "1", "target": "linux-x86_64", "status": "passed",
                       "network": "none", "archive_roundtrip": True, "archive_sha256": "f" * 64,
                       "manifest_sha256": sha256(self.bundle / "manifest.json"),
                       "checksum_list_sha256": sha256(self.bundle / "SHA256SUMS"),
                       "environment": 'ID=ubuntu\nVERSION_ID="22.04"\n',
                       "builder": manifest["builder"], "verified_at": "2026-11-09T00:00:00+00:00",
                       "verifier": {name: sha256(scripts / name) for name in ("verify.py", "offpack.py")}}
        self.report_file = self.root / "report.json"
        self.store = self.root / "evidence"

    def publish(self):
        self.report_file.write_text(json.dumps(self.report))
        return record(self.bundle, self.report_file, self.store)

    def query(self, version="22.04"):
        return check(self.recipe, "ubuntu", version, self.store)

    def test_matching_prior_evidence_is_explicitly_not_new_test(self):
        self.publish()
        result = self.query()
        self.assertTrue(result["has_matching_prior_evidence"])
        self.assertEqual(result["status"], "prior-evidence-only")

    def test_changed_distribution_or_recipe_or_source_is_ineligible(self):
        self.publish()
        self.assertFalse(self.query("24.04")["has_matching_prior_evidence"])
        original = self.recipe.read_text()
        self.recipe.write_text(original + "\n")
        self.assertFalse(self.query()["has_matching_prior_evidence"])
        self.recipe.write_text(original)
        (self.root / "original.sh").write_text("changed")
        self.assertFalse(self.query()["has_matching_prior_evidence"])

    def test_old_report_without_code_hash_is_historical_only(self):
        self.report.pop("verifier")
        entry = self.publish()
        self.assertEqual(entry["provenance_level"], "historical-unbound-code")
        self.assertFalse(self.query()["has_matching_prior_evidence"])

    def test_changed_evidence_is_ineligible(self):
        entry = self.publish()
        (self.store / entry["report"]).write_text("{}")
        self.assertFalse(self.query()["has_matching_prior_evidence"])

    def test_failed_report_cannot_be_published(self):
        self.report["status"] = "failed"
        with self.assertRaises(PackError):
            self.publish()

    def test_changed_bundle_cannot_be_published(self):
        (self.bundle / "upstream/install.sh").write_text("changed")
        with self.assertRaises(PackError):
            self.publish()
