# spreeder

A local speed-reading tool for reading text (often agent output) via Rapid Serial Visual Presentation at a controlled pace, to train faster reading through regular use. As of v2 the primary form is a native macOS menu-bar app: a global hotkey performs a **Capture** of the clipboard and plays it in a small floating **HUD**, while the **Full window** holds the paste field and settings (ADR-0004). The original single-file web version (ADR-0001) is frozen but still runs. The tool stays frictionless and never tracks or measures progress — it only remembers the last-used settings.

## Language

**RSVP** (Rapid Serial Visual Presentation):
The presentation technique where text is shown as a timed sequence at a fixed focal position, instead of as static lines the eye scans.

**Chunk**:
The unit shown on screen at one tick — one or more words presented together.
_Avoid_: word, flash, frame

**ORP** (Optimal Recognition Point):
The single character within a chunk that stays pinned at a fixed horizontal position so the eye never moves. Visually marked (the red pivot letter).
_Avoid_: pivot point, focus letter

**WPM** (words per minute):
The reading pace the user sets, which determines how long each chunk is shown.

**Session**:
One run of reading a text from start to finish. The text enters either by being pasted (full window) or by **Capture** (HUD via hotkey).

**Capture**:
Grabbing the current clipboard contents as the source of a Session, triggered by the global hotkey. The fast path that replaces pasting.
_Avoid_: grab, snatch, paste (paste is the deliberate full-window alternative)

**HUD**:
The borderless, always-on-top overlay window the hotkey opens. It auto-plays a Capture with the last-saved settings and carries no settings UI of its own.
_Avoid_: popup, modal, widget

**Full window**:
The ordinary application window, opened by launching the app *without* the hotkey. Home of the paste field and the settings (WPM, chunk size, adaptive). Source of the settings the HUD reuses.
