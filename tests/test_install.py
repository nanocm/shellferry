"""Exercise fresh install, managed updates, preservation, and path boundaries."""
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("shellferry_installer", ROOT / "install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="shellferry-install-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.checkout = self.root / "checkout"
        source = self.checkout / "skills/shellferry"
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text("---\nname: shellferry\ndescription: test\n---\n")
        (self.checkout / "VERSION").write_text("0.1.0")
        self.source = source
        p1 = patch.object(installer, "ROOT", self.checkout)
        p2 = patch.object(installer, "SOURCE", source)
        p1.start()
        p2.start()
        self.addCleanup(p1.stop)
        self.addCleanup(p2.stop)
        self.args = SimpleNamespace(action="install", dest=self.root / "skills", scope="user", host="codex", project_dir=self.root, force=False, dry_run=False)
        self.target = self.args.dest / "shellferry"

    def test_fresh_install_idempotent_and_uninstall_preserves_backup(self):
        self.assertEqual(installer.perform(self.args)["status"], "installed")
        self.assertEqual(installer.perform(self.args)["status"], "already-current")
        self.args.action = "status"
        self.assertEqual(installer.perform(self.args)["status"], "installed")
        self.args.action = "uninstall"
        result = installer.perform(self.args)
        self.assertFalse(self.target.exists())
        self.assertTrue((Path(result["backup"]) / "SKILL.md").is_file())

    def test_dry_run_does_not_create_destination(self):
        self.args.dry_run = True
        self.assertEqual(installer.perform(self.args)["status"], "would-install")
        self.assertFalse(self.args.dest.exists())

    def test_version_only_update_refreshes_receipt(self):
        installer.perform(self.args)
        (self.checkout / "VERSION").write_text("0.1.1")
        self.args.action = "update"
        result = installer.perform(self.args)
        self.assertEqual(result["status"], "updated")
        self.args.action = "status"
        self.assertEqual(installer.perform(self.args)["version"], "0.1.1")

    def test_unmanaged_directory_refused(self):
        self.target.mkdir(parents=True)
        (self.target / "mine.txt").write_text("do not change")
        self.args.force = True
        with self.assertRaises(installer.InstallError):
            installer.perform(self.args)
        self.assertEqual((self.target / "mine.txt").read_text(), "do not change")

    def test_modified_update_needs_force_and_preserves_edits(self):
        installer.perform(self.args)
        (self.target / "SKILL.md").write_text("my changes")
        (self.source / "new.txt").write_text("new version")
        self.args.action = "update"
        with self.assertRaises(installer.InstallError):
            installer.perform(self.args)
        self.args.force = True
        result = installer.perform(self.args)
        self.assertEqual((Path(result["backup"]) / "SKILL.md").read_text(), "my changes")
        self.assertEqual((self.target / "new.txt").read_text(), "new version")

    def test_project_location_is_inside_requested_project(self):
        self.args.dest = None
        self.args.scope = "project"
        result = installer.perform(self.args)
        self.assertEqual(Path(result["path"]), self.root / ".agents/skills/shellferry")

    def test_symlink_destination_is_not_replaced(self):
        self.args.dest.mkdir()
        outside = self.root / "outside"
        outside.mkdir()
        try:
            self.target.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("Symlink creation unavailable")
        with self.assertRaises(installer.InstallError):
            installer.perform(self.args)
        self.assertTrue(self.target.is_symlink())
