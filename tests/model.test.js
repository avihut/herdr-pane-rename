import { test } from "node:test";
import assert from "node:assert/strict";
import { identity, stateKey, resolvePane, validateName } from "../mods/pane-rename/model.js";

const a = { pane: "p1", terminal: "t1", tab: "tab1" };
const b = { pane: "remote/p1", terminal: "remote/t1", tab: "remote/tab1" };

test("context menu target cannot be replaced by focus, including a stale explicit target", () => {
  assert.equal(resolvePane([a, b], { pane: b.pane }, { pane: a.pane }), b);
  assert.equal(resolvePane([a], { pane: b.pane }, { pane: a.pane }), null);
  assert.equal(resolvePane([a], { pane: null }, { pane: a.pane }), null);
  assert.equal(resolvePane([a], {}, { pane: a.pane }), a);
  assert.equal(resolvePane([a], {}, { pane: null }), null);
});
test("names follow panes across layouts, cwd changes and tabs; new terminal identities do not inherit them", () => {
  assert.equal(identity(a), identity({ ...a, tab: "tab2", cwd: "/new", title: "new title" }));
  assert.notEqual(stateKey(a), stateKey(b));
  assert.notEqual(stateKey(a), stateKey({ ...a, terminal: "t2" }));
  assert.notEqual(stateKey({ pane: "p1", mod: "files" }), stateKey({ pane: "p1", mod: "board" }));
  assert.equal(stateKey(null), null);
});
test("normalization supports empty reset, Unicode and 120 Unicode code points", () => {
  assert.deepEqual(validateName("  \n  "), { name: "" });
  assert.deepEqual(validateName("  בנייה 🛠️  "), { name: "בנייה 🛠️" });
  assert.deepEqual(validateName("one\ntwo\u0000"), { name: "one two" });
  assert.ok(validateName("🐑".repeat(120)).name);
  assert.ok(validateName("🐑".repeat(121)).error);
});
