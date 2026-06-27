# 06 — Adaptive pacing

Status: ready-for-agent

## Parent

`.scratch/spreeder-v1/PRD.md`

## What to build

An optional adaptive pacing mode that gives heavier chunks a little more time at the same **WPM**.

- Engine: when `settings.adaptive` is on, `chunkDurationMs` scales a chunk's base duration up for heavier chunks (longer words and/or sentence-ending punctuation). When off, duration depends only on WPM and word count.
- Shell: an adaptive toggle, off by default for this slice (persistence of the choice arrives in issue 07).

## Acceptance criteria

- [ ] With adaptive on, heavier chunks (long words / sentence-ending punctuation) display longer than lighter chunks at the same WPM
- [ ] With adaptive off, duration depends only on WPM and word count (no per-chunk weighting)
- [ ] Toggle defaults to off
- [ ] Unit tests show adaptive-on lengthens a heavier chunk relative to a lighter one at the same WPM, and adaptive-off does not

## Blocked by

- `.scratch/spreeder-v1/issues/02-pace-controls-wpm-chunk-size.md`
