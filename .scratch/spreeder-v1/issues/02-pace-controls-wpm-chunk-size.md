# 02 — Pace controls: WPM + chunk size

Status: done

## Parent

`.scratch/spreeder-v1/PRD.md`

## What to build

Let the reader control reading pace in **WPM** and how many words make up a **chunk**, with both feeding the pure engine.

- Engine: `buildSession` reads `settings.chunkSize` and splits the stream into chunks of that many words, in reading order, with a possibly shorter final chunk. `chunkDurationMs(chunk)` derives each chunk's display time from `settings.wpm` and the chunk's word count, so overall pace tracks the requested WPM.
- Shell: a WPM input and a chunk-size input, wired so changes take effect for the next session/playback.

## Acceptance criteria

- [x] Reader can set WPM and the playback pace reflects it
- [x] Reader can set chunk size and chunks contain that many words (final chunk may be shorter)
- [x] Per-chunk duration is derived from WPM and word count so total pace matches the WPM set
- [x] Engine changes are covered by unit tests: chunking respects `chunkSize`, preserves order, handles a short final chunk; duration tracks WPM and word count
- [x] Tests assert only on `buildSession` output / `chunkDurationMs`, not internal helpers

## Blocked by

- `.scratch/spreeder-v1/issues/01-tracer-rsvp-playback.md`
