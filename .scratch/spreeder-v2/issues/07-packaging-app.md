# 07 — Packaging: unsigned `.app` + readme

Status: ready-for-agent

## Parent

`.scratch/spreeder-v2/PRD.md`

## What to build

Package spreeder as a distributable native macOS `.app` bundle (e.g. with PyInstaller) that bundles the Python runtime and Tkinter, so it can run on the reader's locked-down work machine and be handed to friends — with no browser engine anywhere (ADR-0004).

The build is **unsigned** for now (signing/notarization and an Apple Developer account are deferred until real-world use proves the value). Distribute it as a zip with a short readme covering first-run on a fresh Mac: right-click → Open to clear the Gatekeeper warning once, then grant the **Accessibility** permission (which no installer can grant on the user's behalf, and which the global hotkey and active-window placement both require).

## Acceptance criteria

- [ ] The app builds into a self-contained `.app` bundle that launches on a Mac without a separate Python install
- [ ] The bundled app runs fully offline and uses no browser engine or webview (ADR-0004)
- [ ] The hotkey, HUD, Capture, Full window, and persistence all work from the packaged build
- [ ] A readme documents first-run (right-click → Open) and how to grant the Accessibility permission
- [ ] The artifact is shareable as a zip a friend can unpack and run

## Blocked by

- `.scratch/spreeder-v2/issues/01-tracer-engine-fullwindow-playback.md`
- `.scratch/spreeder-v2/issues/02-menu-bar-resident-lifecycle.md`
- `.scratch/spreeder-v2/issues/03-capture-hud-playback.md`
- `.scratch/spreeder-v2/issues/04-global-hotkey-accessibility.md`
- `.scratch/spreeder-v2/issues/05-hud-placement-active-window.md`
- `.scratch/spreeder-v2/issues/06-settings-persistence-autostart.md`
