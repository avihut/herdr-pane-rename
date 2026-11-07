import { View, div } from "gpui-kit";
import { Input, InputState, h_flex, v_flex } from "gpui-base";
import { props, focused, panes, shared, setShared, closeOverlay } from "herdr";
import { identity, stateKey, resolvePane, validateName } from "./model.js";
import { look, panel, button } from "./look.js";

export default class RenamePane extends View {
  init(_props, cx) {
    this.target = resolvePane(panes(), props(), focused());
    this.error = "";
    const value = this.target ? shared(stateKey(this.target)) ?? "" : "";
    this.input = InputState.new({ value, placeholder: "Automatic name" });
    if (value) this.input.set_selected_range({ start: 0, end: value.length });
    this.input.on("change", (_e, cx) => { this.error = ""; cx.notify(); });
    this.input.on("submit", (_e, cx) => { this.save(); cx.notify(); });
    this.handle = cx.focus_handle();
    this.input.focus();
    cx.timer.after(60, () => this.input.focus());
  }
  dismiss() { closeOverlay(props()?.overlay); }
  live() { return this.target && panes().find(p => identity(p) === identity(this.target)); }
  save(reset = false) {
    if (!this.live()) { this.error = "This pane is no longer available."; return; }
    const result = validateName(reset ? "" : this.input.value());
    if (result.error) { this.error = result.error; return; }
    setShared(stateKey(this.target), result.name || null);
    this.dismiss();
  }
  render() {
    const s = look(), live = this.live();
    const body = v_flex().p(18).gap(10)
      .child(div().text_color(s.dim).child(live ? (this.target.title || this.target.mod || "Pane") : "Focus a pane to rename it."))
      .when(Boolean(live), e => e
        .child(div().child("Pane name"))
        .child(Input.new(this.input).h(34).px(9).bg(s.field).text_color(s.fg).text_size(s.size)
          .border(1).border_color(s.accent).rounded(s.kind === "win98" || s.kind === "fallout" ? 0 : 4))
        .child(div().text_size(11).text_color(s.dim).child("Leave empty to restore the automatic name.")))
      .when(Boolean(this.error), e => e.child(div().text_color(s.fg).child(this.error)))
      .child(h_flex().pt(10).gap(8).justify_end()
        .when(Boolean(live), e => e.child(button(s, "rename-reset", "Reset", (_e, cx) => { this.save(true); cx.notify(); })))
        .child(button(s, "rename-cancel", "Cancel", () => this.dismiss()))
        .when(Boolean(live), e => e.child(button(s, "rename-save", "Save", (_e, cx) => { this.save(); cx.notify(); }, true))));
    return div().id("rename-root").track_focus(this.handle).w_full()
      .on_key_down((e, cx) => { if (e.key === "escape") { this.dismiss(); cx.stop_propagation(); } })
      .child(panel(s, body, "Rename pane", () => this.dismiss()));
  }
}
