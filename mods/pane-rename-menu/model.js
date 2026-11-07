// Pure identity and validation helpers, also exercised without GPUI.
export function identity(p) {
  return p?.pane ? JSON.stringify([p.pane, p.terminal ?? null, p.mod ?? null]) : null;
}
export function stateKey(p) {
  const id = identity(p);
  return id === null ? null : `pane-rename.v1:${id}`;
}
export function normalizeName(value) {
  return String(value ?? "").replace(/[\u0000-\u001f\u007f-\u009f]/g, " ").trim();
}
export function validateName(value) {
  const name = normalizeName(value);
  return Array.from(name).length > 120 ? { error: "Use 120 characters or fewer." } : { name };
}
// Explicit targets must never fall back to whichever pane happens to be focused.
export function resolvePane(all, input, focus) {
  const explicit = Object.prototype.hasOwnProperty.call(input ?? {}, "pane");
  const id = explicit ? input.pane : focus?.pane;
  return typeof id === "string" ? all.find(p => p.pane === id) ?? null : null;
}
