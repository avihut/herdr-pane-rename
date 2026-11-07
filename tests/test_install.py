from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from install import plan, uninstall, digest, encoded


class Installation(unittest.TestCase):
    def test_shortcut_collision_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / "layouts").mkdir()
            (home / "keys.json").write_text('{"global":{"cmd-f2":"something-else","ctrl-shift-f2":"something-else"}}')
            before = (home / "keys.json").read_bytes()
            with self.assertRaisesRegex(ValueError, "Shortcut conflict"):
                plan(home)
            self.assertEqual((home / "keys.json").read_bytes(), before)
            self.assertFalse((home / "mods").exists())

    def test_uninstall_preserves_concurrent_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            backup = home / ".pane-rename-backup"
            backup.mkdir()
            (home / "keys.json").write_bytes(b"later edit")
            (backup / "keys.json").write_bytes(b"original")
            (backup / "manifest.json").write_bytes(encoded({"keys.json": {"installed": digest(b"installed"), "existed": True}}))
            with self.assertRaisesRegex(ValueError, "changed since installation"):
                uninstall(home)
            self.assertEqual((home / "keys.json").read_bytes(), b"later edit")

    def test_partial_install_can_restore_applied_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            backup = home / ".pane-rename-backup"
            backup.mkdir()
            (home / "keys.json").write_bytes(b"installed")
            (backup / "keys.json").write_bytes(b"original")
            (backup / "manifest.json").write_bytes(encoded({
                "keys.json": {"installed": digest(b"installed"), "existed": True, "applied": True},
                "never-written.js": {"installed": digest(b"planned"), "existed": False, "applied": False}}))
            uninstall(home)
            self.assertEqual((home / "keys.json").read_bytes(), b"original")
            self.assertFalse(backup.exists())


if __name__ == "__main__": unittest.main()
