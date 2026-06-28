# 02 — Menu-bar resident + lifecycle

Status: done

## Parent

`.scratch/spreeder-v2/PRD.md`

## What to build

Turn the app into a quiet, always-running **menu-bar** resident so it can later catch a global hotkey. Instead of being a normal windowed app, spreeder runs as a status-bar item with no dock window. Clicking the icon opens the **Full window** (the paste + playback from issue 01); a Quit item stops the app cleanly.

This establishes the resident process model the hotkey depends on: something is always running to listen. The Full window becomes the "opened without the hotkey" entry point.

## Acceptance criteria

- [x] The app runs as a menu-bar / status-bar item with no dock window
- [x] Clicking the menu-bar icon opens the Full window (paste + RSVP playback from issue 01)
- [x] A Quit action in the menu-bar stops the app cleanly
- [x] The app keeps running in the background after the Full window is closed
- [x] No browser engine or webview is used (ADR-0004)

## Blocked by

- `.scratch/spreeder-v2/issues/01-tracer-engine-fullwindow-playback.md`
