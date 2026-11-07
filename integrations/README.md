# Optional layout integration

Layout authors keep ownership of their native headers, menus, and source repositories. Copy `pane-rename.js` into the host mod as an optional adapter; it imports only Herdr's built-in API, so the layout still loads without Pane Rename.

Use `renamedPane(p) || existingAutomaticTitle` in a pane header. It only reads shared state; absent names preserve the layout's existing title.

On each native menu opening, initialize `renameAvailable` to false and call `paneRenameAvailable()` inside `cx.spawn(async (cx) => { ...; cx.notify(); })`. Include Rename only after the check returns true. The check reads only the dependency's small `mod.json` capability manifest, and fails closed when missing, malformed, unreadable, or an unsupported version. Never read it per render or poll for it.

The menu action must capture the right-clicked pane ID and pass it to `openPaneRename(pane)`. Do not resolve the focused pane when the action runs. Preserve the native menu geometry, title fallback, and existing commands. The shared dialog chooses its style from the current layout.

Install the shared dependency before enabling the native menu hook. Require its native checks and the host layout's checks, then verify the rendered dialog, keyboard shortcut, nonfocused-pane targeting, reset, cancellation, and original layout switcher. Apply changes to each layout's source and run its own installer; do not patch a generated installed copy independently.

Active source repositories are intentionally deferred by the broad installer. Their owners integrate a reviewed patch after ongoing packaging work is complete. This coordination does not authorize bypassing a session's app-access or filesystem restrictions.

## Reviewed source patches

Install the three common mods first. Apply a patch only to its matching source revision, with a clean relevant working tree:

| Patch | Source base |
| --- | --- |
| `winxp.patch` | `avihut/herdr-xp` at `54bfd5b` |
| `fallout.patch` | `avihut/herdr-fallout` at `5b41b87` |
| `evangelion.patch` | `avihut/herdr-evangelion` at `d7daf8e` |

From the layout source worktree, run `git apply --check /path/to/patch` before `git apply /path/to/patch`. Run that repository’s checks and install task: XP uses `mise run install`; Fallout uses `mise run install-update`; Evangelion uses `mise run update`. The patches include the optional helper inside the host mod. They retain native controls and add a root `terminal_menu` reference; Herdr documents its built-in fallback if that optional menu mod is missing.

Evangelion public main at `3648742` already includes this integration; do not apply its patch twice. The patch is for the pre-integration `d7daf8e` baseline only. Its integration includes installer completeness checks. Do not copy only its main/kit files: the helper must be installed with them.
