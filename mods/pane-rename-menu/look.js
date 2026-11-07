import { div, Background, PathBuilder } from "gpui-kit";
import { h_flex, v_flex } from "gpui-base";
import { theme, settings, shared } from "herdr";

export function look() {
  const t = theme(), dark = Boolean(settings()?.dark), layout = shared("layout");
  const s = { kind: "herdr", font: "Geist", radius: 9, size: 12.8, row: 31,
    bg: t.popover, fg: t.foreground, dim: t.muted, field: t.background,
    edge: t.border, accent: t.accent, onAccent: t.accent_foreground,
    button: t.raised, selected: t.selected, hover: t.hover };
  // Layout geometry and typography are deliberate; colors track appearance.
  if (layout === "winxp") Object.assign(s, { kind: "xp", font: "Tahoma", radius: 5, size: 12, row: 25,
    bg: dark ? "#30333b" : "#ece9d8", fg: dark ? "#e9eaf0" : "#000000",
    dim: dark ? "#b9bdc9" : "#55534b", field: dark ? "#1e2026" : "#ffffff",
    edge: dark ? "#6c7488" : "#7f9db9", button: dark ? "#454954" : "#f5f3eb",
    accent: "#316ac5", onAccent: "#ffffff", selected: "#316ac5", hover: "#316ac5" });
  else if (["win98", "win98-dark"].includes(layout)) Object.assign(s, { kind: "win98", font: "Pixelated MS Sans Serif", radius: 0, size: 12, row: 23,
    bg: t.surface, field: dark ? "#181818" : "#ffffff", button: t.surface,
    accent: t.accent, selected: t.accent, hover: t.accent, onAccent: t.accent_foreground });
  else if (layout === "lcars") Object.assign(s, { kind: "lcars", font: "Antonio", radius: 18, size: 16, row: 34,
    bg: "#000000", fg: "#ffcc99", dim: "#cc9966", field: "#0a0a12", edge: "#9999ff",
    accent: "#ff9900", onAccent: "#000000", button: "#cc99cc", buttonFg: "#000000", selected: "#ff9900", hover: "#ffcc66" });
  else if (layout === "pasture") Object.assign(s, { kind: "pasture", radius: 4, size: 14,
    bg: dark ? "#6b4a2c" : "#d2a673", fg: dark ? "#efe4cc" : "#573c27",
    dim: dark ? "#e0c8a4" : "#65482d", edge: dark ? "#3a2716" : "#9b6b40",
    field: dark ? "#382718" : "#f3dfbf", button: dark ? "#7d5a37" : "#e0bb8c",
    accent: dark ? "#efe4cc" : "#573c27", onAccent: dark ? "#382718" : "#fff5df",
    selected: dark ? "#7d5a37" : "#e0bb8c", hover: dark ? "#7d5a37" : "#e0bb8c" });
  else if (layout === "fallout") {
    const amber = shared("fallout.amber") === true;
    const ink = amber ? (dark ? "#ffcd70" : "#71420b") : (dark ? "#a6f58d" : "#24552a");
    Object.assign(s, { kind: "fallout", font: "Geist Mono", radius: 2, size: 12,
      bg: dark ? "#30382c" : "#cbd0b7", fg: ink, dim: dark ? "#c9c9a6" : "#343e26",
      field: dark ? "#111a10" : "#e8ecd9", edge: dark ? "#657050" : "#7c8767",
      accent: ink, onAccent: dark ? "#111a10" : "#e8ecd9", button: dark ? "#111a10" : "#e8ecd9",
      selected: ink, hover: ink });
  } else if (layout === "board") Object.assign(s, { kind: "board", radius: 7, size: 13 });
  else if (layout === "evangelion") Object.assign(s, { kind: "evangelion", font: "Geist Mono", radius: 0, size: 12, row: 28 });
  else if (["terminals", "my-terminals"].includes(layout)) Object.assign(s, { kind: "terminals", radius: 16, size: 13 });
  else if (layout === "herdr-t3") Object.assign(s, { size: 14, radius: 6 });
  s.dark = dark;
  return s;
}

function bevel(content, dark, inset = false) {
  const light = dark ? "#6a6a6a" : "#ffffff", shade = dark ? "#141414" : "#808080";
  return div().w_full().bg(inset ? shade : light).pt(2).pl(2)
    .child(div().w_full().bg(inset ? light : shade).pr(2).pb(2).child(content));
}

export function button(s, id, label, action, primary = false) {
  const bg = primary ? s.accent : s.button;
  let el = h_flex().id(id).h(30).px(13).items_center().justify_center()
    .rounded(s.kind === "lcars" ? 15 : s.radius).border(1).border_color(primary ? s.accent : s.edge)
    .bg(bg).text_color(primary ? s.onAccent : (s.buttonFg ?? s.fg)).text_size(s.size).cursor_pointer()
    .hover(e => e.opacity(0.85)).on_mouse_down("left", (_e, cx) => cx.stop_propagation())
    .on_click(action).child(s.kind === "lcars" || s.kind === "fallout" ? label.toUpperCase() : label);
  if (s.kind === "win98") el = div().w(92).child(bevel(el, s.dark));
  return el;
}

export function panel(s, content, title, dismiss) {
  let root = v_flex().w_full().min_h(0).font_family(s.font).text_size(s.size).text_color(s.fg).bg(s.bg);
  if (title) {
    let bar = h_flex().h(s.kind === "xp" ? 30 : 34).px(12).items_center().gap(10);
    if (s.kind === "xp") {
      const rect = PathBuilder.fill().move_to("0%", "0%").line_to("100%", "0%")
        .line_to("100%", "100%").line_to("0%", "100%").close().build();
      bar = bar.relative().bg("#0054e3").text_color("#ffffff")
        .child(window.paint_path(rect, Background.linear_gradient(180, "#0997ff", "#003dd7"))
          .absolute().top(0).left(0).size_full());
    }
    else if (s.kind === "win98") bar = bar.h(22).px(4).bg(s.accent).text_color(s.onAccent);
    else if (s.kind === "lcars") bar = bar.bg(s.accent).text_color(s.onAccent).rounded_tl(24).rounded_tr(24);
    else if (s.kind === "evangelion") bar = bar.font_family("Antonio").text_size(20).text_color(s.accent).border_b(1).border_color(s.accent);
    else bar = bar.border_b(1).border_color(s.edge);
    root = root.child(bar.child(div().relative().flex_1().font_semibold().child(["lcars", "fallout", "evangelion"].includes(s.kind) ? title.toUpperCase() : title))
      .child(div().relative().id("rename-dismiss").px(5).cursor_pointer().child("×").on_click(dismiss)));
  }
  root = root.child(content);
  if (s.kind === "win98") return bevel(root, s.dark);
  return root.border(s.kind === "xp" || s.kind === "pasture" ? 3 : 1).border_color(s.kind === "xp" ? "#0831d9" : s.edge).rounded(s.radius).overflow_hidden();
}
