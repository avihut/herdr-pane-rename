"""Small, guarded edits to existing native headers; never replace their controls."""
import json

HELPERS = '''
// Pane Rename integration: the same per-pane identity as pane-rename/model.js.
function renamedPane(p) {
  if (!p?.pane) return null;
  const value = renameShared(`pane-rename.v1:${JSON.stringify([p.pane, p.terminal ?? null, p.mod ?? null])}`);
  return typeof value === "string" && value ? value : null;
}
function openPaneRename(pane) {
  if (typeof pane !== "string" || !pane) return;
  return renameOverlay({mod:"pane-rename",kind:"dialog",frame:"none",width:460,props:{pane}});
}
function openRenameMenu(p) {
  if (!p?.pane) return;
  return renameOverlay({mod:"pane-rename-menu",kind:"popup",frame:"none",width:290,
    props:{tab:"pane",target:{pane:p.pane,terminal:p.terminal}}});
}
'''
IMPORT = 'import { shared as renameShared, openOverlay as renameOverlay } from "herdr";\n'


def replace_once(text, before, after):
    count = text.count(before)
    if count != 1:
        raise ValueError(f"Adapter expected one match, found {count}: {before[:100]}")
    return text.replace(before, after, 1)


def adapt(path, text):
    if "// Pane Rename integration:" in text:
        return text
    original = text
    if path in ("pane/main.js", "cockpit/pane.js", "t3-pane/main.js"):
        start = text.index("    const name = ")
        end = text.index(";", start)
        expression = text[start + len("    const name = "):end]
        text = text[:start] + "    const name = renamedPane(p) || (" + expression + ")" + text[end:]
        text = replace_once(text, '.on_click(() => run("pane.focus", { pane }))',
            '.on_click(() => run("pane.focus", { pane }))\n      .on_mouse_down("right", (_e, cx) => { cx.stop_propagation(); openRenameMenu(p); })')
    elif path == "terminals-pane/main.js":
        text = replace_once(text, 'const title = p.title || "shell";', 'const title = renamedPane(p) || p.title || "shell";')
        text = replace_once(text, '.on_click(() => run("pane.focus", { pane }))',
            '.on_click(() => run("pane.focus", { pane }))\n      .on_mouse_down("right", (_e, cx) => { cx.stop_propagation(); openRenameMenu(p); })')
    elif path == "board/main.js":
        text = replace_once(text, '.child(p?.program?.name ?? "Terminal")', '.child(renamedPane(p) || p?.program?.name || "Terminal")')
        text = replace_once(text, 'return h_flex().size_full().px(13)',
            'return h_flex().id("rename-board-pane").on_mouse_down("right", (_e, cx) => { cx.stop_propagation(); openRenameMenu(p); }).size_full().px(13)')
    elif path == "pasture/main.js":
        text = replace_once(text, '.child(pane?.program.name ?? "Terminal")', '.child(renamedPane(pane) || pane?.program?.name || "Terminal")')
        marker = '    if (p.role === "pane") {'
        start = text.index(marker)
        pos = text.index('return h_flex()', start)
        text = text[:pos] + text[pos:].replace('return h_flex()', 'return h_flex().id("rename-pasture-pane").on_mouse_down("right", (_e, cx) => { cx.stop_propagation(); openRenameMenu(pane); })', 1)
    elif path == "fallout/main.js":
        text = replace_once(text, 'txt(p?.title??"TERMINAL",11,c.paper)', 'txt(renamedPane(p)||p?.title||"TERMINAL",11,c.paper)')
        text = replace_once(text, 'if(p.kind==="pane"){if(t.pane){',
            'if(p.kind==="pane"){if(t.pane){action("Rename pane…",()=>openPaneRename(t.pane));')
    elif path == "lcars/main.js":
        text = replace_once(text, 'const menu = (tab, target) => openOverlay(',
            'const menu = (tab, target) => tab === "pane" ? openRenameMenu({pane:target.pane,terminal:target.terminal}) : openOverlay(')
    elif path == "t3-menu/main.js":
        text = replace_once(text, '["Split right", "pane.split",', '["Rename pane…", "pane-rename.open", { pane: tg.pane }],\n        ["Split right", "pane.split",')
        text = replace_once(text, 'if (it[1] === "worktree")', 'if (it[1] === "pane-rename.open") openPaneRename(it[2].pane);\n    else if (it[1] === "worktree")')
        text = replace_once(text, 'function shortcut(name, args) {',
            'function shortcut(name, args) {\n  if (name === "pane-rename.open") return keys().find(b => b.section === "global" && b.action === "mod.open:pane-rename")?.keys ?? "";')
    elif path in ("win98-dark/window.js", "winxp/kit.js"):
        text = replace_once(text, 'export function paneTitle(p) {', 'export function paneTitle(p) {\n  const custom = renamedPane(p);\n  if (custom) return custom;')
        if path.startswith("win98"):
            text = replace_once(text, 'openMenu([', 'openMenu([\n        { label: "&Rename Pane…", shortcut: "Cmd+F2", act: { renamePane: id } },')
    elif path == "win98-dark/kit.js":
        text = replace_once(text, 'export function perform(act) {', 'export function perform(act) {\n  if (act?.renamePane) { openPaneRename(act.renamePane); return; }')
    elif path == "winxp/window.js":
        text = replace_once(text, '{ label: "Restore",', '{ label: "Rename Pane…", shortcut: "Cmd+F2", act: { renamePane: id } },\n        { label: "Restore",')
    elif path == "evangelion/main.js":
        text = replace_once(text, '.child(pane.title||pane.program?.name||"Terminal")', '.child(renamedPane(pane)||pane.title||pane.program?.name||"Terminal")')
    elif path == "evangelion/kit.js":
        text = replace_once(text, 'export const context = (tab,target) => openOverlay(',
            'export const context = (tab,target) => tab === "pane" ? openRenameMenu({pane:target.pane,terminal:target.terminal}) : openOverlay(')
    else:
        raise ValueError(f"No adapter for {path}")
    if path == "winxp/kit.js":
        text = replace_once(text, 'export function perform(act) {', 'export function perform(act) {\n  if (act?.renamePane) { openPaneRename(act.renamePane); return; }')
    assert text != original
    return IMPORT + text + HELPERS


def adapt_layout(doc, name):
    doc = json.loads(json.dumps(doc))
    # Keep every root look field, native switcher, tab and panel in place.
    doc["terminal_menu"] = "t3-menu" if name == "herdr-t3" else "pane-rename-menu"
    def walk(node):
        if isinstance(node, list):
            for child in node:
                walk(child)
        elif isinstance(node, dict):
            content = node.get("content", {})
            if content.get("tab"):
                pane = content.setdefault("pane", {})
                header = pane.get("header")
                if not header:
                    pane["header"] = {"content": {"mod": "pane-rename-header"}, "height": 30, "position": "top", "reveal": "always"}
                else:
                    mod = header.get("content", {}).get("mod")
                    clones = {"pane": "pane-rename-herdr", "terminals-pane": "pane-rename-terminals"}
                    if mod in clones:
                        header["content"]["mod"] = clones[mod]
                pane["lone"] = True
            for child in node.values():
                walk(child)
    walk(doc)
    return doc
