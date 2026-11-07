import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from adapters import adapt, adapt_layout


class Adapters(unittest.TestCase):
    def test_preserves_root_and_switcher(self):
        source = {"id": "root", "theme": {"light": "paper", "dark": "ink"}, "titlebar": "none",
                  "children": [{"content": {"mod": "layout-switcher"}},
                               {"content": {"tab": "active", "pane": {"gap": 9, "header": {"height": 38, "content": {"mod": "terminals-pane"}}}}}]}
        before = copy.deepcopy(source)
        result = adapt_layout(source, "my-terminals")
        self.assertEqual(source, before)
        self.assertEqual(result["theme"], source["theme"])
        self.assertEqual(result["children"][0], source["children"][0])
        pane = result["children"][1]["content"]["pane"]
        self.assertEqual(pane["gap"], 9)
        self.assertEqual(pane["header"]["height"], 38)
        self.assertEqual(pane["header"]["content"]["mod"], "pane-rename-terminals")
        self.assertEqual(adapt_layout(result, "my-terminals"), result)

    def test_t3_keeps_its_menu(self):
        self.assertEqual(adapt_layout({}, "herdr-t3")["terminal_menu"], "t3-menu")

    def test_missing_header_gets_native_header(self):
        result = adapt_layout({"content": {"tab": "active"}}, "lcars")
        self.assertEqual(result["content"]["pane"]["header"]["content"]["mod"], "pane-rename-header")

    def test_unexpected_source_fails_closed(self):
        with self.assertRaises(ValueError):
            adapt("board/main.js", "// new incompatible board")

    def test_name_adapter_is_idempotent_and_preserves_other_code(self):
        source = 'const untouched = 1;\n    const name = p.title || "shell";\n.on_click(() => run("pane.focus", { pane }))\n'
        result = adapt("pane/main.js", source)
        self.assertIn('const untouched = 1;', result)
        self.assertIn('renamedPane(p) || (p.title || "shell")', result)
        self.assertIn('openRenameMenu(p)', result)
        self.assertEqual(adapt("pane/main.js", result), result)


if __name__ == "__main__": unittest.main()
