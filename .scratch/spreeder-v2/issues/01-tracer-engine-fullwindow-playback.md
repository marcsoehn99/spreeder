# 01 — Tracer bullet: `engine.py` port + Full window paste → RSVP playback

Status: done

## Parent

`.scratch/spreeder-v2/PRD.md`

## What to build

The walking skeleton for v2: a native macOS Python app whose pure logic lives in `engine.py` and whose Full window plays pasted text as RSVP on a Tkinter Canvas.

A reader launches the app, gets a window with a paste field and a play button, pastes text, presses play, and the text is presented one **chunk** at a time at a fixed focal position via **RSVP** — with the **ORP** character pinned at a constant horizontal x and marked red — advancing on a timer until the last chunk has shown, then stopping cleanly.

This slice establishes the v2 two-layer shape and the single test seam (ADR-0004):

- **`engine.py`** — a pure module, ported from `engine.js`, exposing the v1 contract in Python: `build_session(raw_text, settings)` returning the full ordered sequence of chunks with ORP indices plus a per-chunk display duration. It performs normalization (ADR-0003: fenced code blocks removed, inline markdown stripped, whitespace collapsed), chunking by `chunk_size`, deterministic ORP computation, and WPM/word-count timing including the adaptive scaling rule (adaptive defaults off). No GUI, no timers, no clipboard, no file I/O.
- The **native shell** — a Tkinter Full window that imports `engine.py`, holds a paste field + play button, and runs the timer loop rendering each chunk on a Canvas with absolute positioning so the red ORP sits at a fixed x and the line never wraps.

Port the v1 `test/engine.test.js` cases to `pytest` against `engine.py`. Settings may be hardcoded defaults for this slice (moderate WPM, chunk size 1, adaptive off) — the settings UI and persistence come in issue 06. No menu bar, hotkey, HUD, or clipboard yet.

This is the v2 realization of ADR-0004; ADR-0001 (web version) stays frozen.

## Acceptance criteria

- [x] `engine.py` exposes the pure `build_session` contract and has no GUI/timer/clipboard/storage dependencies
- [x] Ported v1 engine tests pass under `pytest` (normalization, chunking, ORP, timing incl. adaptive on/off)
- [x] Launching the app shows a Full window with a paste field and a play button
- [x] Pasting text and pressing play renders RSVP one chunk at a time, advancing on a timer, stopping cleanly after the last chunk
- [x] The red ORP character is always present and sits at the same horizontal x across all chunks
- [x] Each chunk renders on a single line that never wraps
- [x] Empty / whitespace-only paste yields a "nothing to read" state, not a blank player
- [x] No browser engine or webview is used anywhere (ADR-0004)

## Blocked by

None - can start immediately
