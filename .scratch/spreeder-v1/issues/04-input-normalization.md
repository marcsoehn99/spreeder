# 04 — Input normalization (ADR-0003)

Status: done

## Parent

`.scratch/spreeder-v1/PRD.md`

## What to build

Normalize pasted text — typically agent/LLM output — into a clean prose reading stream before chunking, per ADR-0003. This happens inside the engine so it is covered by the single test seam.

- Engine: before chunking, `buildSession` removes fenced code blocks entirely, strips inline markdown markers (`#`, `*`, `-`, backticks, link brackets), and collapses extra whitespace/blank lines.
- Empty or whitespace-only input yields no chunks; the shell surfaces a "nothing to read" state rather than entering playback.

## Acceptance criteria

- [x] Fenced code blocks are removed entirely from the reading stream (not flashed word-by-word)
- [x] Inline markdown markers are stripped so the stream is clean prose
- [x] Extra whitespace and blank lines are collapsed so pacing isn't disrupted by formatting
- [x] Empty / whitespace-only input produces no chunks and the shell shows a clear "nothing to read" state, no harmful behavior
- [x] Unit tests cover code-block removal, marker stripping, whitespace collapse, and empty-input handling

## Blocked by

- `.scratch/spreeder-v1/issues/01-tracer-rsvp-playback.md`
