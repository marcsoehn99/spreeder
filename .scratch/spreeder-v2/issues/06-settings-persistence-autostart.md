# 06 — Settings: Full-window controls + `config.json` persistence + defaults + autostart

Status: ready-for-agent

## Parent

`.scratch/spreeder-v2/PRD.md`

## What to build

Give the reader real, remembered settings — and the login-autostart choice — without recording anything else (ADR-0002).

- **Full-window controls**: WPM, chunk size, adaptive toggle, and the global hotkey combination are all adjustable in the Full window. Changing them takes effect for subsequent Sessions (both paste and Capture). Adaptive defaults off.
- **Persistence**: a single `config.json` at `~/Library/Application Support/spreeder/` replaces v1's `localStorage`. It persists exactly: WPM, chunk size, adaptive, hotkey, panel offset (from issue 05), and the autostart preference — and nothing about *what* was read or *how* (ADR-0002).
- **Defaults**: first run (no `config.json`) applies moderate WPM, chunk size 1, adaptive off, default hotkey ⌃⌘R, and is immediately usable.
- **Autostart (opt-in)**: on first run, ask once whether spreeder should start at login. The choice is stored and is changeable later from the Full window. Not forced on.

## Acceptance criteria

- [ ] WPM, chunk size, adaptive, and hotkey are adjustable in the Full window and take effect for subsequent Sessions
- [ ] All settings persist to `config.json` in Application Support and are restored on relaunch
- [ ] First run with empty storage applies sensible defaults and is immediately usable
- [ ] Nothing beyond preferences is persisted — no reading history, session counts, or WPM-over-time (ADR-0002)
- [ ] First run prompts once for login autostart; the choice is stored and later changeable from the Full window
- [ ] Autostart is opt-in (not enabled unless chosen)

## Blocked by

- `.scratch/spreeder-v2/issues/01-tracer-engine-fullwindow-playback.md`
- `.scratch/spreeder-v2/issues/02-menu-bar-resident-lifecycle.md`
