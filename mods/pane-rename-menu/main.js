import { View, div } from "gpui-kit";
import { h_flex, v_flex } from "gpui-base";
import { panes, terminals, props, closeOverlay, run, shared, keys } from "herdr";
import { paneName, renamePane } from "./api.js";
import { look, panel } from "./look.js";

export default class PaneMenu extends View {
  init(_props, cx) { this.at = 0; this.handle = cx.focus_handle(); this.handle.focus(); }
  items() {
    const target = props()?.target ?? {}, p = panes().find(p => p.pane === target.pane);
    const terminal = terminals().find(t => t.address === target.terminal);
    const rows = [];
    if (p) {
      const shortcut = keys().find(k => k.section === "global" && k.action === "mod.open:pane-rename")?.keys ?? "";
      rows.push(["Rename pane…", () => renamePane(p.pane), shortcut]);
      rows.push(["Split right", () => run("pane.split", { pane: p.pane, direction: "right" })]);
      rows.push(["Split down", () => run("pane.split", { pane: p.pane, direction: "down" })]);
      rows.push([p.zoomed ? "Restore pane" : "Zoom pane", () => run("pane.zoom", { pane: p.pane })]);
    }
    if (terminal) {
      const program = terminal.labels?.["herdr.right-click"] === "program";
      rows.push([program ? "Use Herdr right-click menu" : "Send right-clicks to pane", () => run("terminal.right_click", { terminal: terminal.address, to: program ? "menu" : "program" })]);
      const parent = terminals().find(t => t.address === terminal.parent);
      if (parent) rows.push([`Send back to ${parent.name || parent.address}`, () => run("terminal.park", { terminal: terminal.address })]);
    }
    if (p) rows.push(["Close pane", () => shared("layout") === "herdr-t3"
      ? run(`t3-tabs.close-pane:${p.pane}`) : run("pane.close", { pane: p.pane })]);
    return { rows, p };
  }
  choose(i) {
    const row = this.items().rows[i];
    if (!row) return;
    closeOverlay(props()?.overlay);
    row[1]();
  }
  render() {
    const s = look(), { rows, p } = this.items();
    const highlightedText = ["xp", "win98", "lcars", "fallout", "starcraft"].includes(s.kind) ? s.onAccent : s.fg;
    const content = v_flex().p(5).gap(2)
      .child(div().px(8).py(5).truncate().text_size(11).text_color(s.dim).child(paneName(p) || p?.title || "Pane"))
      .when(!rows.length, e => e.child(div().p(8).child("This pane is no longer available.")))
      .children(rows.map((row, i) => h_flex().id(`rename-menu-${i}`).h(s.row).px(9).gap(8).items_center()
        .rounded(s.kind === "lcars" ? 17 : Math.min(s.radius, 6))
        .text_color(i === this.at ? highlightedText : s.fg)
        .when(i === this.at, e => e.bg(s.selected)).hover(e => e.bg(s.hover).text_color(highlightedText))
        .cursor_pointer().on_hover((on, cx) => { if (on) { this.at = i; cx.notify(); } })
        .on_click(() => this.choose(i))
        .child(div().flex_1().child(s.kind === "lcars" ? row[0].toUpperCase() : row[0]))
        .child(div().text_size(11).child(row[2] ?? ""))));
    return div().id("rename-menu").track_focus(this.handle).w_full()
      .on_key_down((e, cx) => {
        if (e.key === "escape") closeOverlay(props()?.overlay);
        else if (e.key === "enter") this.choose(this.at);
        else if (rows.length && e.key === "down") this.at = (this.at + 1) % rows.length;
        else if (rows.length && e.key === "up") this.at = (this.at + rows.length - 1) % rows.length;
        else return;
        cx.stop_propagation(); cx.notify();
      }).child(panel(s, content));
  }
}
