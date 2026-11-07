# Pane Rename

A small native dialog gives an individual Herdr pane a durable display name, with a keyboard shortcut and a context-menu entry. It adopts the visual language of the layout containing the pane. Native dark-appearance captures are private because the surrounding terminals contain live work.

## What you see

The 460px dialog has a title bar, the pane's automatic title, a labelled input, a short reset hint, and Reset, Cancel, and Save buttons. Herdr uses theme colors and rounded controls. XP uses a blue gradient title, 30px height, Tahoma and a blue window border. Windows 98 uses two-pixel bevels, a 22px blue title bar and Pixelated MS Sans Serif. LCARS uses Antonio, orange and purple rounded slabs on black. Pasture uses brown wood colors. Fallout uses Geist Mono with green or amber lettering. Other layouts follow their native typography and theme colors.

The pane context menu starts with Rename pane… and preserves split, zoom, mouse-routing, sub-agent parking, and close actions where applicable. Its height follows its contents. Existing pane title bars gain the custom name without replacing their other controls. A headerless LCARS pane gains a 30px header.

## How it behaves

Cmd+F2 on macOS, or Ctrl+Shift+F2 elsewhere, opens the dialog for the focused model pane. Right-click targets the pane actually clicked. An explicit missing target never falls back to focus. Save/Enter applies a trimmed name of at most 120 Unicode code points; blank input and Reset restore the automatic name. Cancel/Escape do not save. A closed or replaced pane cannot receive a stale dialog's save. Names survive layout switches, tab moves, and window restarts on the same client. Agent status markers retain their existing working, blocked, done and idle appearance; renaming does not alter agent state.

## Built from

Three mods: `pane-rename` (dialog), `pane-rename-menu` (terminal context menu), `pane-rename-header` (LCARS header). All use `place: none`. The dialog uses `InputState`, `Input`, and ordinary native GPUI elements. Live inputs come from `props`, `focused`, `panes`, `terminals`, `theme`, `settings`, and `shared`. Writes use `setShared`; actions use `run`, `openOverlay`, and `closeOverlay`. Each stored key includes the opaque pane ID plus terminal/mod identity. No network, file, exec, or timer-polling dependencies; a one-shot timer initially focuses the input.

The installer adds guarded adapters to personal headers, clones shipped headers, changes layout terminal-menu references, and merges a free shortcut. It preserves root appearance and layout-switcher nodes. Independent source repositories use reviewed optional integration patches and their own installers.

## Watch out

Herdr currently lacks native pane renaming. These names are client-local UI overrides; other clients and unadapted mods see the automatic title. Do not replace shared.json directly. Do not use focus as a fallback for an explicit stale target. Write mod.json before main.js to avoid automatic docking. Never edit shipped mods in place or wrap layout roots. Preserve T3's guarded close commands. Do not edit XP's installed copy independently of its source repository. Adapter source patterns must match exactly. No screenshot or visual-quality claim is valid until native checks run in the real app.

## Done when

Pure model and adapter tests pass; every changed mod passes `herdr-app check`; `herdr-app status` reports no new errors. Keyboard and context menu reach the same dialog. Nonfocused targeting, save, cancel, reset, stale targets, persistence, and Unicode names work. Screenshots show every supported layout's native style and existing switcher in each supported appearance. XP and Evangelion patches are integrated after their active edits settle. Keep live captures private; use a synthetic illustration for public previews. See README for the current validation limits.
