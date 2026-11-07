import { View, div, svg } from "gpui-kit";
import { h_flex } from "gpui-base";
import { panes, props, run, theme, home } from "herdr";
import { paneName, paneMenu } from "./api.js";
import { look } from "./look.js";

export default class PaneHeader extends View {
  render() {
    const p = panes().find(p => p.pane === props()?.pane);
    if (!p) return div();
    const s = look(), t = theme();
    const title = paneName(p) || ((p.program?.agent || p.program?.shell) && p.program.name) || p.title || p.mod || "Terminal";
    const folder = p.cwd?.startsWith(home() + "/") ? "~" + p.cwd.slice(home().length) : p.cwd ?? "";
    const action = (id, label, hint, callback) => div().id(id).px(6).h(24).rounded(4).cursor_pointer()
      .flex().items_center().text_color(s.kind === "lcars" ? s.onAccent : s.dim)
      .hover(e => e.bg(t.hover)).tooltip(hint).child(label)
      .on_mouse_down("left", (_e, cx) => cx.stop_propagation())
      .on_click((_e, cx) => { cx.stop_propagation(); callback(); });
    return h_flex().id(`rename-header-${p.pane}`).size_full().px(9).gap(7).items_center()
      .font_family(s.font).text_size(s.kind === "lcars" ? 15 : 12)
      .bg(s.kind === "lcars" ? (p.focused ? s.accent : "#9999ff") : t.chrome)
      .text_color(s.kind === "lcars" ? s.onAccent : p.focused ? t.foreground : t.muted)
      .on_click(() => run("pane.focus", { pane: p.pane }))
      .on_mouse_down("right", (_e, cx) => { cx.stop_propagation(); paneMenu(p); })
      .when(Boolean(p.program?.icon), e => e.child(svg(p.program.icon).size(14).flex_none()))
      .child(div().max_w(320).truncate().font_semibold().child(title))
      .child(div().flex_1().min_w(0).truncate().child([folder, p.branch].filter(Boolean).join(" · ")))
      .when(Boolean(p.status), e => e.child(div().size(6).rounded_full().bg(t[p.status] ?? t.dim)))
      .child(action("rename-more", "···", "Pane actions", () => paneMenu(p)))
      .child(action("rename-right", "⊞", "Split right", () => run("pane.split", { pane: p.pane, direction: "right" })))
      .child(action("rename-down", "⊟", "Split down", () => run("pane.split", { pane: p.pane, direction: "down" })))
      .child(action("rename-zoom", p.zoomed ? "↙" : "↗", "Zoom / restore", () => run("pane.zoom", { pane: p.pane })))
      .child(action("rename-close", "×", "Close pane", () => run("pane.close", { pane: p.pane })));
  }
}
