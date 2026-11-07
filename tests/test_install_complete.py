from pathlib import Path
from unittest.mock import patch
import contextlib
import io
import json
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import install

class CompleteInstallation(unittest.TestCase):
    def test_staged_mods_install_completely_and_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home/'layouts').mkdir()
            original = b'{"global":{"f2":"tab.rename"}}\n'
            (home/'keys.json').write_bytes(original)
            with patch.object(sys, 'argv', ['install.py', '--home', str(home)]), patch.object(install.subprocess, 'run'), contextlib.redirect_stdout(io.StringIO()):
                install.main()
            for source in (install.ROOT/'mods').glob('pane-rename*'):
                installed = home/'mods'/source.name
                self.assertEqual(json.loads((installed/'mod.json').read_text())['place'], 'none')
                for file in source.glob('*.js'):
                    self.assertEqual(file.read_bytes(), (installed/file.name).read_bytes())
            self.assertEqual(json.loads((home/'keys.json').read_text())['global']['f2'], 'tab.rename')
            install.uninstall(home)
            self.assertEqual((home/'keys.json').read_bytes(), original)
            self.assertFalse((home/'mods/pane-rename').exists())
