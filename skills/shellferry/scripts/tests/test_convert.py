"""Regression tests for failures discovered during installer conversion."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from convert import apply_patches, build, validate_recipe
from offpack import PackError


def fixture():
    return {"schema": 1, "name": "fixture", "version": "1", "target": "linux-x86_64",
            "shell": "sh", "entrypoint": "upstream/install.sh", "scripts": [{"path": "upstream/install.sh", "source": "original.sh"}],
            "resources": [], "smoke": [["sh", "-ec", 'test -d "$OFFLINE_PREFIX"']]}


class RecipeTests(unittest.TestCase):
    def test_changed_upstream_rejects_patch(self):
        with self.assertRaises(PackError):
            apply_patches("a\na\n", [{"old": "a", "new": "b", "count": 1}])

    def test_empty_anchor_rejected(self):
        with self.assertRaises(PackError):
            apply_patches("a", [{"old": "", "new": "b"}])

    def test_parameter_strings_are_not_arrays(self):
        for key in ("args", "repeat_args", "requires", "notes"):
            recipe = fixture()
            recipe[key] = "--force"
            with self.subTest(key=key), self.assertRaises(PackError):
                validate_recipe(recipe)

    def test_shell_code_rejects_path_interpolation(self):
        for executable, option in (("sh", "-c"), ("bash", "-euc"), ("sh", "-ec")):
            recipe = fixture()
            recipe["smoke"] = [[executable, option, '"{prefix}/tool"']]
            with self.subTest(option=option), self.assertRaises(PackError):
                validate_recipe(recipe)

    def test_shell_code_accepts_quoted_environment(self):
        validate_recipe(fixture())

    def test_audit_environment_cannot_be_overridden(self):
        recipe = fixture()
        recipe["env"] = {"OFFLINE_AUDIT": "/dev/null"}
        with self.assertRaises(PackError):
            validate_recipe(recipe)

    def test_invalid_libc_rejected(self):
        recipe = fixture()
        recipe["runtime"] = {"libc": "not-a-libc"}
        with self.assertRaises(PackError):
            validate_recipe(recipe)

    def test_invalid_default_prefix_rejected(self):
        recipe = fixture()
        recipe["default_prefix"] = "relative/path"
        with self.assertRaises(PackError):
            validate_recipe(recipe)


@unittest.skipUnless(sys.platform.startswith("linux"), "Shell regressions require Linux")
class ShellTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="offline-regression-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def bundle(self, script):
        (self.root / "original.sh").write_text(script)
        recipe = self.root / "recipe.json"
        recipe.write_text(json.dumps(fixture()))
        with contextlib.redirect_stdout(io.StringIO()):
            build(recipe, self.root / "bundle", self.root / "cache")
        return self.root / "bundle"

    def test_swallowed_unknown_url_still_fails(self):
        bundle = self.bundle('#!/bin/sh\noffline_fetch https://example.invalid/missing || true\nexit 0\n')
        result = subprocess.run(["sh", str(bundle / "install.sh")], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Offline resource lookup failed", result.stderr)

    def test_special_prefix_stays_literal_in_smoke(self):
        bundle = self.bundle('#!/bin/sh\nmkdir -p "$OFFLINE_PREFIX"\n')
        prefix = self.root / 'prefix " $(touch injected-marker)'
        first = subprocess.run(["sh", str(bundle / "install.sh"), "--prefix", str(prefix)], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        smoke = subprocess.run(["sh", str(bundle / "smoke.sh"), str(prefix)], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(smoke.returncode, 0, smoke.stderr)
        self.assertFalse((self.root / "injected-marker").exists())

    def test_corruption_rejected_before_installation(self):
        bundle = self.bundle('#!/bin/sh\nmkdir -p "$OFFLINE_PREFIX"\n')
        with (bundle / "upstream/install.sh").open("a") as stream:
            stream.write("# changed\n")
        prefix = self.root / "not-created"
        result = subprocess.run(["sh", str(bundle / "install.sh"), "--prefix", str(prefix)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(prefix.exists())


if __name__ == "__main__":
    unittest.main()
