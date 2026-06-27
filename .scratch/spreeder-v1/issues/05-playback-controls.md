# 05 — Playback controls

Status: ready-for-agent

## Parent

`.scratch/spreeder-v1/PRD.md`

## What to build

Give the reader control over a running **session**. These are shell concerns (timer/DOM/keyboard glue) around the existing engine.

- Pause and resume: stop on the current chunk and pick up from the same chunk.
- Restart: replay the current text from the first chunk without re-pasting.
- Progress indication: a clear sense of position through the chunks (e.g. progress through the sequence).
- Keyboard: spacebar toggles play/pause so playback is controllable without leaving the keyboard.

## Acceptance criteria

- [ ] Reader can pause and resume; resuming continues from the chunk where it paused
- [ ] Reader can restart the current text from the beginning without re-pasting
- [ ] A progress indicator shows roughly how far through the text the reader is
- [ ] Spacebar toggles play/pause
- [ ] Controls behave sensibly at session boundaries (before start, after final chunk)

## Blocked by

- `.scratch/spreeder-v1/issues/01-tracer-rsvp-playback.md`
