# Pane Rename for Herdr

Give each pane a useful name: **Build server**, **API tests**, **Release notes**. Open **Rename pane…** from a pane’s context menu, or press **Cmd+F2** on macOS (**Ctrl+Shift+F2** elsewhere).

The dialog belongs to the layout around it: XP blue title bars, Windows 98 bevels, LCARS slabs, Fallout phosphor, Pasture wood, StarCraft II consoles, TRON grid lines, Expanse ship panels, or Herdr’s current palette. Your names stay with the pane when you switch layouts.

## Use it

- Focus a pane and press the shortcut, or right-click its header and choose Rename pane.
- Enter a name and press **Enter** or **Save**. Right-clicking a different pane targets that pane explicitly.
- **Cancel** or **Escape** leaves the name alone. **Reset**, or saving an empty name, restores its automatic title.
- Names support Unicode, including emoji, up to 120 code points. Closed or replaced panes reject a stale dialog’s save.

This is a native GPUI mod for the **Herdr desktop app**. Names are persistent, client-local display overrides. They do not change the shell process, coding agent, tab, or workspace name, and other Herdr clients retain their own names.

## Layouts

| Layouts | Integration |
| --- | --- |
| Herdr, Terminals, Windows 98 personal copies | Existing title bars and controls; shipped headers are cloned before adaptation |
| Board, Pasture | Original palettes and switcher chips retained |
| Herdr T3, Space Folders, Traveler, Herdr Sim, Cockpit | Existing headers; T3 retains its guarded close routing |
| LCARS | Matching pane header, orange/purple menu and Antonio typography |
| Windows XP | Native window menu; names also appear in taskbar, drag previews and Task Manager |
| Fallout | Pane header and ··· menu; green/amber instrument-panel dialog |
| Evangelion | Entry-plug header and pane menu; native palette and typography |
| StarCraft II, Expanse | Their own headers and pane menus, through the helper vendored in each layout’s source |
| TRON | Dialog style included; header and menu integration offered to its author as [a reviewed patch](integrations/README.md) |

The installer adapts existing personal layouts. Independently maintained XP, Fallout and Evangelion sources use the optional [integration helper and patches](integrations/README.md), so their normal installers remain authoritative. New layouts can use the same small helper. StarCraft II and Expanse ship it in their own sources.

## Install

Requirements: a running Herdr desktop app, Python 3, Node.js for checks, and mise. The mod has no package dependencies or network calls.

```sh
daft clone https://github.com/avihut/herdr-pane-rename --install
# Enter the main worktree printed by daft.
mise trust
mise run test
mise run plan
mise run install
mise run check
```

`plan` writes nothing. Installation preserves layout roots and switchers, refuses occupied mod names or conflicting shortcuts, and backs up exact original files in `~/.config/herdr-app/.pane-rename-backup`. Set `HERDR_APP_HOME` to select another config. Complete owned mod folders are staged before publication to reduce hot reloads. Adapter patterns deliberately reject incompatible layout revisions.

Install the common mods first, then apply any source-repository integration described in [integrations](integrations/README.md). The optional helper checks the installed capability once on menu opening and preserves automatic titles when names are absent.

```sh
mise run uninstall
```

To deploy newer source for the three pane-rename mods over an existing installation, run `mise run update-plan`, then `mise run update`. It never touches layouts, keys or other mods. It refuses if an installed pane-rename file was edited after installation, or if Herdr reports errors. It swaps only the changed mod folders, one rename each, keeping the app's generated files. Uninstall still works afterwards.

Uninstall restores files this installer changed. It refuses if they were edited afterward, preserving subsequent work. Separate layout source integrations belong to those repositories. Saved names remain in Herdr’s shared state.

## Validation

- 21 automated tests cover target identity, Unicode limits, optional dependency failures, preserving layout roots, shortcut conflicts, complete installation, guarded updates and safe restoration.
- Native `herdr-app check` passes for the common mods and adapted headers. XP, Fallout and Evangelion also pass their source checks.
- A live native harness verified save, reset, cancellation, Unicode, overlength rejection, stale targets and isolation of an unfocused target. Physical shortcut and mouse interaction are separate from this programmatic verification.
- Dark-appearance dialog captures were inspected for XP, 98, LCARS, Board, Pasture, Fallout, Herdr, Terminals, T3, Space Folders, Traveler and Herdr Sim. After `mise run update` deployed the latest styles, the dialog was opened in StarCraft II (dark) through the same command Cmd+F2 runs and inspected; Herdr reported no errors.
- Not yet verified by a real keypress or click: Cmd+F2 and right-click → Rename pane. macOS denied synthetic keystrokes to the automation (no Accessibility permission). TRON, Expanse, Cockpit and Evangelion dialogs and all light-mode dialogs have not been inspected live.

**Host limitation:** the shared Herdr mod runtime exhausted memory during extended installation/layout QA. XP documents recovery by restarting Herdr.app; herdr-core need not be restarted. Avoid repeated file-by-file installs. An app-only restart recovered XP with no reported errors and preserved all six live terminal sessions; the user confirmed recovery. Passing native checks alone does not establish visual correctness. Live terminal screenshots are kept private.

## Design and API

See [RECIPE.md](RECIPE.md) for the visual and behavior contract and [integrations](integrations/README.md) for layout authors. The runtime uses native `InputState`, GPUI elements, Herdr pane snapshots and persistent `shared` state. No shell commands, external requests or polling are needed for renaming.

MIT licensed.
