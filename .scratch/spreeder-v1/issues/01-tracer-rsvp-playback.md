# 01 — Tracer bullet: paste → RSVP playback

Status: done

## Parent

`.scratch/spreeder-v1/PRD.md`

## What to build

The walking skeleton end-to-end. A reader pastes text into the tool, presses play, and the text is presented one **chunk** at a time at a fixed focal position via **RSVP**, advancing on a timer until the last chunk has been shown, then stopping cleanly.

This slice establishes the project's two-file shape and the test seam:

- `engine.js` — a pure ES module exporting `buildSession(rawText, settings) → { chunks: [{ text, orpIndex }, …], chunkDurationMs(chunk) }`. For this slice it may split on whitespace into one-word chunks and return a simple fixed per-chunk duration; `orpIndex` may be a trivial value (refined in issue 03). No DOM, no timers, no storage.
- `index.html` — the thin shell: inline CSS plus a `<script type="module">` that imports `engine.js`, holds a textarea + play button, and runs the timer loop that renders each chunk centered.

No build step — native ES modules, double-click `index.html` to open, works fully offline. A test runner (test-only dev dependency) is set up here and runs `engine.js` directly in Node.

This is a deliberate refinement of ADR-0001 (single file → `index.html` + `engine.js`, still buildless); update ADR-0001 to document the two-file shape as part of this slice.

## Acceptance criteria

- [x] `index.html` opens by double-click with no server and no network, fully offline
- [x] Pasting text and pressing play shows the text chunk-by-chunk at a fixed focal position
- [x] Playback advances automatically on a timer and stops cleanly after the final chunk
- [x] A new text can be pasted and played without reloading the page
- [x] `engine.js` is a pure module with no DOM/timer/storage references
- [x] `buildSession` returns the documented shape (`chunks` with `text`/`orpIndex`, plus `chunkDurationMs`)
- [x] Test runner is configured; a unit test imports `engine.js` in Node and asserts chunking of a sample string
- [x] ADR-0001 updated to reflect the `index.html` + `engine.js` shape

## Blocked by

- None - can start immediately
