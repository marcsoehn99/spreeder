# 07 — Settings persistence + defaults

Status: ready-for-agent

## Parent

`.scratch/spreeder-v1/PRD.md`

## What to build

Remember the reader's last-used settings between sessions, and provide sensible first-run defaults — without recording anything else (ADR-0002).

- Shell: on load, read WPM, chunk size, and adaptive toggle from `localStorage` and restore them; on change, write them back. These three keys are the only things persisted — no reading history, session counts, or WPM-over-time.
- First run (nothing in `localStorage`): apply sensible defaults (moderate WPM, chunk size 1, adaptive off) so the reader can start without configuring anything.

## Acceptance criteria

- [ ] WPM, chunk size, and adaptive toggle persist across reloads
- [ ] Reopening the tool restores the last-used settings
- [ ] First run (empty storage) applies sensible defaults and is immediately usable
- [ ] Nothing beyond those three settings is written to storage — no session/progress data (ADR-0002)

## Blocked by

- `.scratch/spreeder-v1/issues/02-pace-controls-wpm-chunk-size.md`
- `.scratch/spreeder-v1/issues/06-adaptive-pacing.md`
