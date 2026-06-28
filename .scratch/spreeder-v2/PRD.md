# PRD: spreeder v2 — native macOS hotkey app

Status: ready-for-agent

## Problem Statement

I'm now hooked on reading with spreeder, but the web version costs me friction every time: I have to find the tab or file, click into the textarea, paste, and press play. When I'm working with an agent and want to read its output *right now*, that's too many steps — it pulls me out of my flow. Worse, my work machine is a locked-down corporate macOS box where I want to use this for real work, and I'm not allowed to rely on a browser engine there. I want to copy some text, hit one key combo, and read it instantly, right over whatever I'm doing — without a browser anywhere in the picture, and without anything that measures or records me.

## Solution

A native macOS app, `spreeder`, that lives quietly in the **menu bar** and listens for a global hotkey (default ⌃⌘R). Pressing it performs a **Capture**: it reads the clipboard, normalizes the text, and immediately plays it as **RSVP** in a small, always-on-top **HUD** that floats over the window I was just in — one **chunk** at a time with the **ORP** character pinned and marked red. It starts playing at once with my last-saved settings, so there's nothing to click. When the last chunk has shown, the HUD auto-closes after a brief hold and I'm back in my work. Opening the app *without* the hotkey gives me the **Full window**, where I can paste text manually and adjust my settings (**WPM**, chunk size, adaptive). It uses no browser engine at all (ADR-0004), works offline, and — as always — never tracks what I read or how I did (ADR-0002); it only remembers my preferences.

## User Stories

### Capture & the hot path

1. As a reader, I want a global hotkey that works from any app, so that I can start reading the clipboard without switching to spreeder first.
2. As a reader, I want the hotkey to read my clipboard and start playing immediately, so that copy → hotkey → read is the whole interaction.
3. As a reader, I want playback to start with my last-saved settings, so that I never reconfigure in the hot path.
4. As a reader, I want the HUD to appear over the window I was just working in, so that I stay in context and don't get yanked elsewhere.
5. As a reader, I want the HUD to be a small floating panel (not a full-screen takeover), so that I'm not ripped out of my flow.
6. As a reader, I want the panel to be opaque with a clear edge, so that the busy background behind it doesn't pull my eye off the red ORP.
7. As a reader, if my clipboard is empty, whitespace-only, or not text (image/file), I want a brief unobtrusive "nothing to read" cue and no panel, so that I'm never surprised by an empty or broken HUD.
8. As a reader, I want captured text run through the same normalization as pasted text (code blocks removed, markdown stripped, whitespace collapsed), so that agent output reads as clean prose (ADR-0003).
9. As a reader, I want no length cap on captured text, so that a long passage is simply a longer Session.

### HUD playback & controls

10. As a reader, I want each chunk shown at a fixed position with the ORP pinned and red, so that my eyes stay still (RSVP).
11. As a reader, I want the ORP to sit at the same horizontal spot regardless of chunk length, so that the focal point never drifts.
12. As a reader, I want the red ORP character to always be present and never jump between chunks, so that the focal point is rock-steady.
13. As a reader, I want each chunk to render on a single line that never wraps, so that I never see two or three stacked lines.
14. As a reader, I want the spacebar to pause and resume, so that I can stop to think and pick up where I left off.
15. As a reader, I want Esc to close the HUD instantly, so that I can drop back into my work the moment I'm done or interrupted.
16. As a reader, I want R to restart the current text from the beginning, so that I can re-read a passage without re-capturing.
17. As a reader, I want a thin progress bar in the HUD, so that I have a sense of how much is left.
18. As a reader, I want the HUD to auto-close after a brief hold when the last chunk has shown, so that I return to work without pressing anything.

### HUD placement

19. As a reader, I want the panel centered over the last active window by default, so that it appears where I'm already looking.
20. As a reader, I want to drag the panel to reposition it, so that I can place it where it suits me.
21. As a reader, I want my drag remembered as an offset relative to the active window, so that the panel reappears where I like it across captures and the ORP stays in a predictable spot.

### Menu-bar resident & lifecycle

22. As a reader, I want the app to run as a quiet menu-bar item with no dock window, so that it's always ready to catch the hotkey without cluttering my screen.
23. As a reader, I want to open the Full window by clicking the menu-bar icon, so that I have an obvious way in when I'm not using the hotkey.
24. As a reader, I want to quit the app from the menu-bar icon, so that I can stop it cleanly when I want to.
25. As a reader, I want to be asked once whether spreeder should start at login, so that the hotkey is ready after a reboot without forcing it on me.
26. As a reader, I want to change the autostart choice later, so that I'm not locked into my first answer.

### Full window (paste & settings)

27. As a reader, I want a Full window with a paste field and a play button, so that I can read text I type or paste deliberately, not just via Capture.
28. As a reader, I want to set WPM, chunk size, and the adaptive toggle in the Full window, so that I can tune how reading feels.
29. As a reader, I want adaptive pacing off by default unless I previously turned it on, so that the baseline is predictable.
30. As a reader, I want to change the hotkey combination, so that I can pick something that doesn't clash with an app I use.
31. As a reader, if I paste empty or whitespace-only text in the Full window, I want a "nothing to read" state rather than a blank player, so that I'm not confused.

### Settings persistence

32. As a reader, I want my WPM, chunk size, adaptive toggle, hotkey, panel offset, and autostart preference remembered between launches, so that the tool feels like mine.
33. As a reader, I want sensible defaults the first time I run it (moderate WPM, chunk size 1, adaptive off, default hotkey), so that I can read immediately.
34. As a reader, I do NOT want my reading history, session counts, or WPM-over-time recorded, so that spreeder stays a frictionless trainer and not a dashboard that judges me (ADR-0002).

### Local / no browser engine / shareable

35. As a reader, I want spreeder to use no browser engine of any kind, so that it runs on my locked-down work machine where that's not allowed (ADR-0004).
36. As a reader, I want it to work fully offline, so that my text never leaves my machine.
37. As a reader, I want it packaged as a `.app` I can hand to friends, so that they can benefit from it too.
38. As a friend receiving it, I want a short readme explaining first-run (right-click → Open) and granting the Accessibility permission, so that I can get it working on my own Mac.

## Implementation Decisions

### Architecture: native Python, one test seam, no browser engine (ADR-0004)

- The app is a native macOS program written in Python with a **Tkinter** GUI. No browser engine, no webview — this is the decisive constraint (locked-down work machine) and the reason v2 exists. See ADR-0004.
- It splits into the same shape as v1, one layer up the stack:
  - **`engine.py`** — a pure module exporting the session-building logic, ported from `engine.js`. No GUI, no timers, no clipboard, no file I/O. **This is the single test seam.**
  - The **native shell** — the menu-bar resident, the HUD window, the Full window, the global hotkey listener, clipboard reads, active-window geometry, the playback timer, and `config.json` persistence. This is thin glue, not unit-tested, verified by running the app.
- The existing web version (`index.html` + `engine.js`, ADR-0001) is **frozen**, not co-developed. ADR-0001 carries a status note pointing here.

### The engine seam (`engine.py`)

- Mirrors the v1 contract as pure Python, e.g.:

  ```
  build_session(raw_text, settings) -> Session
    Session.chunks            -> list of Chunk(text, orp_index)
    Session.chunk_duration_ms(chunk) -> int
  ```

  The exact names are the implementer's to finalize; the contract is: **pure input (raw text + settings) → the full ordered sequence of chunks with ORP indices, plus a way to get each chunk's display duration.**
- `settings` carries at least `wpm`, `chunk_size`, `adaptive`.
- **Normalization** (ADR-0003) happens inside `build_session` before chunking: remove fenced code blocks entirely, strip inline markdown markers, collapse whitespace. It is part of the seam, so Capture and Full-window paste inherit it identically.
- **Chunking**: the normalized stream is split into chunks of `chunk_size` words in reading order; the last chunk may be shorter; empty/whitespace-only input yields no chunks.
- **ORP computation**: a deterministic, unit-testable function of the chunk text returns the pinned character index (standard RSVP "slightly left of center"), in range for chunks of any length including 1-character and single-word chunks.
- **Timing**: `chunk_duration_ms` derives base duration from `wpm` and word count so overall pace tracks WPM; with `adaptive` on, heavier chunks (long words, sentence-ending punctuation) are scaled up; with it off, duration depends only on WPM and word count.

### The native shell (untested glue)

- **Menu-bar resident**: runs with no dock window; a status-bar icon opens the Full window on click and offers Quit. On first run, asks once whether to enable **login autostart** (opt-in), changeable later from the Full window.
- **Global hotkey**: a configurable combination (default ⌃⌘R) registered system-wide. Requires the macOS **Accessibility** permission, granted per user — surfaced to the user, not bundled.
- **Capture**: on hotkey, read the clipboard. If empty/whitespace-only/non-text, show a brief "nothing to read" cue and open no HUD. Otherwise build a Session via `engine.py` and play it in the HUD.
- **HUD**: a small, borderless, always-on-top, opaque panel rendered on a Tkinter **Canvas** with absolute text positioning — this is what guarantees the ORP sits at a fixed x and chunks never wrap (constructively fixing the two rendering bugs seen in the frozen web version). Placed centered over the last active window by default (geometry read via the Accessibility permission already needed for the hotkey); draggable, with the offset relative to that window persisted. Controls: space = pause/resume, Esc = close, R = restart, thin progress bar. Auto-closes after a brief hold when the last chunk has shown.
- **Full window**: paste field + play, plus the settings UI (WPM, chunk size, adaptive, hotkey, autostart). Handles empty/whitespace paste with a "nothing to read" state.
- **Persistence**: a single `config.json` at `~/Library/Application Support/spreeder/`, replacing v1's `localStorage`. Persists exactly: WPM, chunk size, adaptive, hotkey, panel offset, autostart preference — and nothing about *what* was read or *how* (ADR-0002).

### Defaults

- First run (no `config.json`): moderate WPM, chunk size 1, adaptive off, default hotkey ⌃⌘R, autostart unset (prompted), panel default-centered over the active window.

### Distribution

- Packaged as an **unsigned** `.app` (e.g. PyInstaller), shared as a zip with a short readme: first run = right-click → Open, then grant Accessibility. Signing/notarization (Apple Developer account, $99/yr) is deferred until real-world use proves the value warrants it.

## Testing Decisions

- **What makes a good test here:** it exercises the external behavior of `engine.py` through its public contract (`build_session` + the returned per-chunk duration), asserting on the produced chunks, ORP indices, and durations for given input strings and settings. Tests must not reach into private helpers or assert on implementation details (function names, regex internals, intermediate strings) — only input→output behavior an implementer is free to refactor underneath. This mirrors the v1 testing convention exactly, one layer up the stack.
- **The single seam under test is `engine.py`.** Because it is pure (no GUI, no timers, no clipboard, no storage), tests import it directly with a Python test runner (e.g. `pytest`) and need no GUI harness.
- **Coverage to include** (port the v1 `test/engine.test.js` cases as the starting point):
  - Normalization: fenced code blocks removed entirely; inline markdown markers stripped; whitespace collapsed (ADR-0003).
  - Chunking: respects `chunk_size`, preserves order, handles a short final chunk, handles empty/whitespace-only input (yields no chunks).
  - ORP: returns a deterministic in-range index for chunks of varying length, including 1-character and single-word chunks.
  - Timing: tracks WPM and word count with adaptive off; adaptive on lengthens heavier chunks relative to lighter ones at the same WPM.
- **The native shell is intentionally not unit-tested.** Global hotkey, menu-bar lifecycle, HUD rendering of the red ORP, active-window placement, clipboard reads, autostart, and `config.json` are thin glue verified by running the app. A GUI/integration harness can be added later without changing the engine seam.
- **Prior art:** the v1 engine suite (`test/engine.test.js`) is the direct model; v2 establishes the equivalent Python convention (`pytest` against `engine.py`).

## Out of Scope

- Any progress tracking, session logging, WPM-over-time stats, streaks, or charts (ADR-0002).
- Reading code blocks via RSVP, or an "include code blocks" toggle (ADR-0003 leaves this a future option).
- Co-developing or porting features back to the frozen web version (ADR-0001).
- A signed/notarized build and an Apple Developer account — deferred until the tool's value is proven in real use.
- Windows and Linux builds; v2 targets locked-down corporate **macOS**.
- A full-screen focus mode; the HUD is deliberately a small floating panel to preserve flow.
- Themes, font pickers, or visual customization beyond what RSVP legibility and HUD opacity require.
- Any network feature (URL fetch, sync, cloud) — input is clipboard or paste only, fully offline.

## Further Notes

- The two rendering issues observed in the web version (the red ORP occasionally missing or jumping; chunks wrapping onto up to three lines) are expected to be resolved constructively by the Canvas-based HUD with absolute positioning. They remain in the frozen web version; fix there only if separately wanted.
- The whole v2 leap rests on one constraint: **no browser engine on a locked-down macOS work machine.** That is recorded in ADR-0004; if that constraint ever disappears, a webview wrapper around the existing web app becomes the cheaper path again.
- "Fewer seams is better" still holds: exactly one test seam (`engine.py`); everything stateful or side-effecting lives in the untested native shell.
