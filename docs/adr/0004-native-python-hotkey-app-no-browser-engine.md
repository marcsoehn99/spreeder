# Native Python menu-bar app with a global hotkey — no browser engine

For v2 the primary product becomes a native macOS app: a resident **menu-bar** process (Python + Tkinter) that listens for a global hotkey (default ⌃⌘R). The hotkey performs a **Capture** — it reads the clipboard and plays it as RSVP in a small, always-on-top **HUD** floating over the last active window, starting immediately with the last-saved settings. Launching the app *without* the hotkey opens the **Full window** (paste field + WPM/chunk/adaptive settings). We deliberately use **no browser engine** of any kind.

## Why

The decisive constraint is the target: a locked-down corporate **macOS** machine on which the user wants to read agent output for work. A browser engine is ruled out by that environment; Python apps can be installed there with extra permissions. So a webview wrapper around the existing web app — the otherwise-obvious, much cheaper path that would have preserved the single JS codebase — is exactly what the environment forbids. The whole value of v2 is *less* friction than pasting into a web page: copy → hotkey → read.

## Considered options

- **Webview wrapper** (pywebview/WKWebView around `index.html` + `engine.js`) — rejected: relies on a browser engine, the one thing barred on the work machine. "Shareable with friends" does not distinguish it from native (both can be packaged), so it carried no compensating advantage.
- **PyQt/PySide** — rejected for now: heavier install, licensing nuance, harder to approve on a locked-down machine. Tkinter ships with Python (zero extra native deps) and its `Canvas` gives pixel-perfect ORP positioning with no line-wrapping.

## Consequences

- The single JS **test seam** is given up. The pure logic (normalization per ADR-0003, chunking, ORP, pacing) is **ported to `engine.py`**, which keeps the same "one pure, directly-tested module" discipline in Python. The web version (`index.html` + `engine.js`, ADR-0001) is **frozen**, not co-developed.
- A **global hotkey** and reading the active window's geometry both require the macOS **Accessibility** permission, granted **per user** (the user via extra rights at work; friends on their own Macs). No installer can grant it.
- ADR-0002 (no progress tracking) is unchanged: `config.json` in `~/Library/Application Support/spreeder/` persists only *preferences* — WPM, chunk size, adaptive, hotkey, panel offset, autostart — never reading history or stats.
- Distribution is an **unsigned** `.app` (first run: right-click → Open) until real-world use justifies a signed/notarized build (Apple Developer account, $99/yr).
