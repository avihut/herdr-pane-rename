import { shared, openOverlay } from "herdr";
import { stateKey } from "./model.js";

export function paneName(p) {
  const key = stateKey(p);
  const value = key && shared(key);
  return typeof value === "string" && value ? value : null;
}
export function renamePane(pane) {
  if (typeof pane !== "string" || !pane) return;
  return openOverlay({ mod: "pane-rename", kind: "dialog", frame: "none", width: 460, props: { pane } });
}
export function paneMenu(p) {
  if (!p?.pane) return;
  return openOverlay({ mod: "pane-rename-menu", kind: "popup", frame: "none", width: 290,
    props: { tab: "pane", target: { pane: p.pane, terminal: p.terminal } } });
}
