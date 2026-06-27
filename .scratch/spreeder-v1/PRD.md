# PRD: spreeder v1

Status: ready-for-agent

## Problem Statement

I read a lot of text that arrives as plain prose — especially long agent/LLM output — and reading it line-by-line is slower than I'd like. I want to train myself to read faster, but the tools for this are either web services I have to trust with my text, or heavyweight apps that nag me with stats and streaks. I just want to paste some text, have it shown to me one chunk at a time at a pace I control, and read it. No accounts, no upload, no setup, and nothing measuring me. It has to be frictionless enough that I'll actually reach for it every day, because the training only works through regular use.

## Solution

A single local speed-reader, `spreeder`, that I open by double-clicking a file. It works fully offline. I paste text into it, press play, and it presents the text via **RSVP** — one **chunk** at a time at a fixed focal position, with the **ORP** character pinned in place (marked red) so my eye never has to move. I control the pace in **WPM** and how many words appear per chunk, and I can turn on adaptive pacing so longer/heavier chunks linger a little. When I paste agent output, markdown markers are stripped and code blocks are dropped, so I get clean prose to read. The tool remembers my last settings between sessions, but it never records what I read or how I did — there's no progress tracking, by design.

## User Stories

### Getting text in

1. As a reader, I want to paste text into a single visible input area, so that I can start reading immediately without any setup.
2. As a reader, I want to paste agent/LLM output that contains markdown, so that I can read explanations without the syntax markers getting in the way.
3. As a reader, I want fenced code blocks removed from what I read, so that code isn't flashed at me word-by-word out of context.
4. As a reader, I want inline markdown markers (`#`, `*`, `-`, backticks, link brackets) stripped, so that the reading stream is clean prose.
5. As a reader, I want extra whitespace and blank lines collapsed sensibly, so that pacing isn't thrown off by formatting artifacts.
6. As a reader, I want to paste a new text and read it without reloading the page, so that I can run several sessions back to back.
7. As a reader, if I paste empty or whitespace-only text, I want the tool to do nothing harmful and tell me there's nothing to read, so that I'm not confused by a blank player.

### Reading (RSVP playback)

8. As a reader, I want text shown one chunk at a time at a fixed position, so that my eyes stay still and I read faster.
9. As a reader, I want the **ORP** character of each chunk pinned at the same horizontal spot and marked red, so that I have a stable focal point.
10. As a reader, I want the chunk laid out so the ORP stays aligned regardless of chunk length, so that the focal point never drifts left or right.
11. As a reader, I want to press play to start the session, so that I control when reading begins.
12. As a reader, I want to pause and resume, so that I can stop to think and pick up where I left off.
13. As a reader, I want the session to end cleanly when the last chunk has been shown, so that I know I've finished.
14. As a reader, I want to restart the current text from the beginning, so that I can re-read a passage without re-pasting it.
15. As a reader, I want a clear indication of where I am in the text (e.g. progress through the chunks), so that I have a sense of how much is left.
16. As a reader, I want play/pause to be reachable by keyboard (e.g. spacebar), so that I can control playback without leaving the keyboard.

### Controlling pace

17. As a reader, I want to set my reading pace in **WPM**, so that I can push myself faster or slow down as needed.
18. As a reader, I want to change WPM and have it take effect, so that I can tune the pace to the material.
19. As a reader, I want to set how many words make up a **chunk**, so that I can trade focal stability for throughput.
20. As a reader, I want each chunk's display time derived from my WPM and the number of words in it, so that the overall pace matches the WPM I asked for.
21. As a reader, I want an adaptive pacing toggle, so that longer or heavier chunks (e.g. long words, sentence-ending punctuation) get a little more time.
22. As a reader, I want adaptive pacing to be off by default unless I previously turned it on, so that the baseline behavior is predictable.

### Settings persistence

23. As a reader, I want my last-used WPM, chunk size, and adaptive toggle remembered, so that I don't reconfigure every time.
24. As a reader, I want my settings restored when I reopen the tool, so that it feels like *my* tool.
25. As a reader, I want sensible defaults the very first time I open it (before any settings are saved), so that I can start reading without configuring anything.
26. As a reader, I do NOT want my reading history, session counts, or WPM-over-time recorded, so that the tool stays a frictionless trainer and not a dashboard that judges me.

### Local / frictionless

27. As a reader, I want to open the tool by double-clicking a file, so that there's no server to run.
28. As a reader, I want it to work with no network connection, so that my text never leaves my machine and it works anywhere.
29. As a reader, I want it to load instantly with no build or install step, so that there's zero friction to using it daily.

## Implementation Decisions

### Architecture: engine + shell, no build step

- The app is split into **two files, still with no build step**, served as native ES modules:
  - `engine.js` — a pure module exporting the session-building logic. No DOM, no timers, no `localStorage` access. This is the single test seam.
  - `index.html` — the thin shell: inline CSS, plus a `<script type="module">` that imports `engine.js` and wires it to the DOM, the playback timer, the controls, and `localStorage`.
- This is a deliberate, mild refinement of **ADR-0001**: the app stays buildless, install-free, and double-click-to-open, but "single static HTML file" becomes "`index.html` + `engine.js`, native ESM, no build." The reason is testability — see Testing Decisions. ADR-0001 should be updated to reflect this two-file shape during implementation.
- ADR-0002 (no progress tracking) and ADR-0003 (strip markdown / remove code blocks) are honored as written.

### The engine seam

- The engine exposes a pure entry point along the lines of:

  ```
  buildSession(rawText, settings) → {
    chunks: [{ text: string, orpIndex: number }, …],
    chunkDurationMs(chunk) → number
  }
  ```

  This shape came from sketching the seam, not a working prototype; the exact names are for the implementer to finalize, but the contract is: **pure input (raw text + settings) → the full ordered sequence of chunks with ORP indices, plus a way to get each chunk's display duration.** The shell iterates `chunks` on a timer and renders each one.
- `settings` carries at least `{ wpm, chunkSize, adaptive }`.
- **Normalization** (per ADR-0003) happens inside the engine, before chunking: remove fenced code blocks entirely, strip inline markdown markers, collapse whitespace. It is part of `buildSession`, not the shell, so it is covered by the one seam.
- **Chunking**: the normalized stream is split into chunks of `chunkSize` words, in order, preserving reading order. The last chunk may be shorter.
- **ORP computation**: a pure function of the chunk's text returns the index of the pinned character. Use a simple, deterministic rule based on chunk length (a standard RSVP-style "slightly left of center" pivot); the exact rule is an implementation detail but must be deterministic and unit-testable.
- **Timing**: `chunkDurationMs` derives base duration from `wpm` and the chunk's word count so that overall pace tracks the requested WPM. When `adaptive` is on, duration is scaled up for heavier chunks (longer words and/or sentence-ending punctuation). When `adaptive` is off, duration depends only on WPM and word count.

### The shell (untested glue)

- Renders the current chunk with the ORP character in red, horizontally aligned so the ORP stays at a fixed x-position across chunks.
- Owns the play/pause/restart state and the `setTimeout`/`requestAnimationFrame` loop that advances through `chunks`.
- Reads settings from `localStorage` on load (falling back to defaults on first run) and writes them back when changed. The persisted keys are exactly WPM, chunk size, and adaptive toggle — nothing else (ADR-0002).
- Handles the empty/whitespace-only input case by surfacing a "nothing to read" state rather than entering playback.
- Binds the keyboard shortcut(s) for play/pause.

### Defaults

- First-run defaults (used when nothing is in `localStorage`): a moderate WPM, a chunk size of 1 word, adaptive off. Exact default WPM to be chosen by the implementer within a sensible reading range.

## Testing Decisions

- **What makes a good test here:** it exercises external behavior of the engine through its public contract (`buildSession` + the returned `chunkDurationMs`), asserting on the produced chunks, ORP indices, and durations for given input strings and settings. Tests must not reach into private helpers or assert on implementation details (internal function names, regex internals, intermediate strings) — only on the input→output behavior an implementer is free to refactor underneath.
- **The single seam under test is `engine.js`.** Because it is pure (no DOM, no timers, no storage), tests import it directly in Node with a test runner and need no browser/jsdom harness.
- **Coverage to include:**
  - Normalization: fenced code blocks removed entirely; inline markdown markers stripped; whitespace collapsed (ADR-0003).
  - Chunking: respects `chunkSize`, preserves order, handles a short final chunk, handles empty/whitespace-only input (yields no chunks).
  - ORP: returns a deterministic in-range index for chunks of varying length, including 1-character and single-word chunks.
  - Timing: `chunkDurationMs` tracks WPM and word count with adaptive off; adaptive on lengthens heavier chunks relative to lighter ones at the same WPM.
- **The shell (`index.html` glue) is intentionally not unit-tested.** Playback timing, DOM rendering of the red ORP, control wiring, and `localStorage` are thin glue verified by manually opening the file. If a regression suite for the shell is ever wanted, it can be added later via a jsdom/browser harness without changing the engine seam.
- **Prior art:** none yet — this is the first code in the repo. This PRD therefore also establishes the testing convention (pure engine, tested directly) that later features should follow.

## Out of Scope

- Any progress tracking, session logging, WPM-over-time stats, streaks, or charts (ADR-0002).
- Reading code blocks via RSVP, or an "include code blocks" toggle (ADR-0003 leaves this as a future option).
- File upload / drag-and-drop of files, fetching text from URLs, or any network feature — input is paste-only.
- Accounts, sync, cloud storage, or anything that sends text off the machine.
- Frameworks, bundlers, package installs for the shipped app (test-only dev dependencies are fine).
- Themes, font pickers, or extensive visual customization beyond what RSVP legibility requires.
- Mobile-specific layouts; v1 targets a desktop browser opened from a local file.

## Further Notes

- The split into `engine.js` + `index.html` is the only deviation from ADR-0001 and exists solely to keep the core logic on a single clean test seam. Update ADR-0001 to document the two-file shape when implementing.
- The "fewer seams is better" goal is met: there is exactly one test seam (`engine.js`). Everything stateful or side-effecting is pushed into the untested shell so the tested surface stays pure.
- Keep the ORP alignment robust: the red character must sit at the same horizontal position for every chunk, which usually means a three-part layout (pre-ORP / ORP / post-ORP) with the ORP column fixed. This is a shell concern but worth calling out because it's the most visually fiddly part.
