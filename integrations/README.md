# Optional layout integration

Layout authors keep ownership of their native headers, menus, and source repositories. Copy `pane-rename.js` into the host mod as an optional adapter; it imports only Herdr's built-in API, so the layout still loads without Pane Rename.

Use `renamedPane(p) || existingAutomaticTitle` in a pane header. It only reads shared state; absent names preserve the layout's existing title.

On each native menu opening, initialize `renameAvailable` to false and call `paneRenameAvailable()` inside `cx.spawn(async (cx) => { ...; cx.notify(); })`. Include Rename only after the check returns true.

Don't let the row shift the menu under the pointer. If the check finishes after the menu has drawn, a row that appears above others pushes them down, and a click aimed at Zoom can land on Split down. When the layout opens its own pane menu, run the check before opening and pass the result in the menu's props (XP and Evangelion do this); Rename can then sit first. When Herdr opens the menu itself (`terminal_menu`), the layout can't check beforehand, so put Rename **last**, after Close pane…. Then nothing already drawn moves, and a click just below the old bottom edge lands on Rename, which is harmless. Don't put it just above Close: that pushes Close down to where such a click lands, and `pane.close` has no confirmation (it ends the terminal). Expanse and TRON do this. The check reads only the dependency's small `mod.json` capability manifest, and fails closed when missing, malformed, unreadable, or an unsupported version. Never read it per render or poll for it.

The menu action must capture the right-clicked pane ID and pass it to `openPaneRename(pane)`. Do not resolve the focused pane when the action runs. Preserve the native menu geometry, title fallback, and existing commands. The shared dialog chooses its style from the current layout.

Install the shared dependency before enabling the native menu hook. Require its native checks and the host layout's checks, then verify the rendered dialog, keyboard shortcut, nonfocused-pane targeting, reset, cancellation, and original layout switcher. Apply changes to each layout's source and run its own installer; do not patch a generated installed copy independently.

Active source repositories are intentionally deferred by the broad installer. Their owners integrate a reviewed patch after ongoing packaging work is complete. This coordination does not authorize bypassing a session's app-access or filesystem restrictions.

## Reviewed source patches

Install the three common mods first. Apply a patch only to its matching source revision, with a clean relevant working tree:

| Patch | Source base |
| --- | --- |
| `winxp.patch` | `avihut/herdr-xp` at `54bfd5b` |
| `fallout.patch` | `avihut/herdr-fallout` at `5b41b87` (puts Rename first after an async check; see the row-shift note above) |
| `evangelion.patch` | `avihut/herdr-evangelion` at `d7daf8e` |
| `tron.patch` | `avihut/herdr-tron` at `aacd7db` (already in `bb7428e` and later; don't apply twice) |

From the layout source worktree, run `git apply --check /path/to/patch` before `git apply /path/to/patch`. Run that repository’s checks and install task: XP uses `mise run install`; Fallout uses `mise run install-update`; Evangelion and TRON use `mise run update`. The patches include the optional helper inside the host mod. They retain native controls; the older three also add a root `terminal_menu` reference (TRON's layout already routes terminal right-clicks to its own menu); Herdr documents its built-in fallback if that optional menu mod is missing.

Evangelion public main at `3648742` already includes this integration; do not apply its patch twice. The patch is for the pre-integration `d7daf8e` baseline only. Its integration includes installer completeness checks. Do not copy only its main/kit files: the helper must be installed with them.

The TRON patch is the integration TRON's author applied and released (`bb7428e`): `Rename pane…` comes last, after `Close pane…`, in TRON's own pane menu (its `···` button, header right-click and terminal right-click all open it). Custom names appear in the console header and tooltip, and the helper ships as `mods/tron/pane-rename.js`. A native fixture renders the menu with the row present: 19 tests and 181 isolated renders pass. The live row and dialog still need a look.

StarCraft II and Expanse vendor the helper in their own sources; no patch is needed for them.
