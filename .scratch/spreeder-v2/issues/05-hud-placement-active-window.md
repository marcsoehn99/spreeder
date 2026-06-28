# 05 — HUD placement over the last active window + draggable, remembered offset

Status: done

## Parent

`.scratch/spreeder-v2/PRD.md`

## What to build

Make the HUD appear where the reader is already working, and stay where they like it. By default the HUD is centered over the **last active window** — the window that was frontmost when the Capture fired — read via the Accessibility permission already needed for the hotkey (issue 04). This keeps the reader in context (their flow), instead of jumping their eye elsewhere.

The HUD is draggable: repositioning it stores an **offset relative to the active window's center**, which is reapplied on future Captures so the panel — and therefore the red ORP — reappears in a predictable spot.

Offset persistence uses the same `config.json` store introduced in issue 06.

## Acceptance criteria

- [x] On Capture, the HUD is centered over the window that was frontmost when the hotkey fired
- [x] If no active-window geometry is available, the HUD falls back to a sensible default (e.g. screen center)
- [x] The HUD can be dragged to reposition it
- [x] A drag is remembered as an offset relative to the active window and reapplied on subsequent Captures
- [x] The remembered offset persists across app restarts

## Blocked by

- `.scratch/spreeder-v2/issues/03-capture-hud-playback.md`
- `.scratch/spreeder-v2/issues/06-settings-persistence-autostart.md`
