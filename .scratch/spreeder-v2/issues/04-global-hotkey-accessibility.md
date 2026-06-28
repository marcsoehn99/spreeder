# 04 — Global hotkey + Accessibility

Status: ready-for-agent

## Parent

`.scratch/spreeder-v2/PRD.md`

## What to build

Replace the temporary menu trigger from issue 03 with a real system-wide global hotkey, so the reader can fire a Capture from any app. Default combination ⌃⌘R.

The hotkey works regardless of which app is focused and immediately runs the Capture → HUD path. On macOS this requires the **Accessibility** permission; the app should detect when it isn't granted and clearly guide the user to grant it (System Settings → Privacy & Security → Accessibility) rather than failing silently. The same permission later enables reading the active window's geometry (issue 05).

The hotkey value is read from settings (defaulting to ⌃⌘R); making it user-configurable in the Full window is part of issue 06 — this slice just needs to consume a configured value and register it globally.

## Acceptance criteria

- [ ] A system-wide global hotkey (default ⌃⌘R) fires a Capture from any focused app
- [ ] The hotkey path opens the HUD and plays immediately with the current settings
- [ ] When Accessibility permission is missing, the app surfaces a clear prompt guiding the user to grant it, instead of failing silently
- [ ] Once granted, the hotkey works without restarting (or the app clearly instructs to restart if required)
- [ ] No browser engine or webview is used (ADR-0004)

## Blocked by

- `.scratch/spreeder-v2/issues/03-capture-hud-playback.md`
