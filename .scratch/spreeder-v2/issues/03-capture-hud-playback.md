# 03 — Capture → HUD playback (menu-triggered for now)

Status: done

## Parent

`.scratch/spreeder-v2/PRD.md`

## What to build

The headline reading path, minus the global hotkey: a **Capture** that reads the clipboard and plays it in a small floating **HUD**. For this slice the trigger is a temporary menu-bar item (e.g. "Read clipboard now") — the real global hotkey arrives in issue 04.

On trigger: read the clipboard. If it's empty, whitespace-only, or not text (image/file), show a brief unobtrusive "nothing to read" cue and open no HUD. Otherwise build a Session via `engine.py` (normalization inherited from the seam — ADR-0003) and play it in the HUD.

The HUD is a small, borderless, always-on-top, **opaque** panel (clear edge, so the busy background doesn't pull the eye off the red ORP) rendered on a Tkinter Canvas, reusing the RSVP rendering from issue 01 so the ORP stays at a fixed x and chunks never wrap. It starts playing immediately with the current settings. Controls: spacebar = pause/resume, Esc = close instantly, R = restart from the beginning; a thin progress bar shows position. When the last chunk has shown, the HUD holds briefly (~1s) then auto-closes.

Placement is not yet over the active window (that's issue 05) — center it on screen for now.

## Acceptance criteria

- [x] A menu-bar item triggers a Capture of the current clipboard
- [x] Empty / whitespace-only / non-text clipboard shows a brief "nothing to read" cue and opens no HUD
- [x] Valid text plays in a small, borderless, always-on-top, opaque floating HUD, starting immediately
- [x] Captured text is normalized identically to pasted text via `engine.py` (ADR-0003)
- [x] The red ORP is always present, fixed-x, and chunks render on a single non-wrapping line in the HUD
- [x] Spacebar pauses/resumes, Esc closes instantly, R restarts; a thin progress bar reflects position
- [x] After the last chunk, the HUD holds briefly then auto-closes
- [x] No length cap is imposed on captured text

## Blocked by

- `.scratch/spreeder-v2/issues/01-tracer-engine-fullwindow-playback.md`
- `.scratch/spreeder-v2/issues/02-menu-bar-resident-lifecycle.md`
