import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const state = { name: null, manifest: null, reads: 0, opened: [] };
globalThis.__paneRenameIntegrationTest = state;
const stub = `
const state = globalThis.__paneRenameIntegrationTest;
export function shared(key) { state.key = key; return state.name; }
export function appHome() { return '/test/herdr'; }
export async function readTextFile(path) { state.path = path; state.reads++; if (state.fail) throw Error('unavailable'); return state.manifest; }
export function openOverlay(value) { state.opened.push(value); return 'overlay-1'; }
`;
const data = source => `data:text/javascript;base64,${Buffer.from(source).toString("base64")}`;
const source = await readFile(new URL("../integrations/pane-rename.js", import.meta.url), "utf8");
const api = await import(data(source.replace('from "herdr"', `from ${JSON.stringify(data(stub))}`)));

test("optional capability fails closed and reads only the manifest", async () => {
  for (const manifest of [null, "{", "{}", '{"pane_rename_api":2}', '{"pane_rename_api":"1"}']) {
    state.manifest = manifest;
    assert.equal(await api.paneRenameAvailable(), false);
  }
  state.fail = true;
  assert.equal(await api.paneRenameAvailable(), false);
  state.fail = false;
  state.manifest = '{"place":"none","pane_rename_api":1}';
  const before = state.reads;
  assert.equal(await api.paneRenameAvailable(), true);
  assert.equal(state.reads, before + 1);
  assert.equal(state.path, "/test/herdr/mods/pane-rename/mod.json");
});

test("optional title lookup preserves fallback without file reads", () => {
  const before = state.reads;
  state.name = null;
  const pane = { pane: "remote/p2", terminal: "remote/t2" };
  assert.equal(api.renamedPane(pane) || "Automatic", "Automatic");
  state.name = "Build";
  assert.equal(api.renamedPane(pane), "Build");
  assert.equal(state.key, 'pane-rename.v1:["remote/p2","remote/t2",null]');
  assert.equal(state.reads, before);
});

test("optional native menu action requires an explicit valid pane ID", () => {
  api.openPaneRename(undefined);
  api.openPaneRename(null);
  api.openPaneRename(42);
  assert.equal(state.opened.length, 0);
  api.openPaneRename("remote/p2");
  assert.deepEqual(state.opened[0].props, { pane: "remote/p2" });
});
