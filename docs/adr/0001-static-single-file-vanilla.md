# Two-file vanilla app — `index.html` + `engine.js`, no build step

> **Status (v2):** This web track is **frozen** as of v2 — see ADR-0004. The native macOS app is now the primary product; the pure logic was ported to `engine.py`. The two files below still run, but are no longer co-developed.

spreeder ships as two files: `index.html` (thin shell with inline CSS + `<script type="module">`) and `engine.js` (pure ES module, no DOM/timers/storage). There is no build step, no bundler, no npm install for the app itself. The whole value of "local" is frictionlessness: open the files in a browser, runs offline anywhere, copy/paste of agent output is native.

The original plan was a single HTML file. It was split into two during v1 implementation solely for testability: `engine.js` is the one test seam — a pure function `buildSession(rawText, settings)` that can be imported directly in Node by a test runner (dev-only dependency, not shipped). The shell (`index.html`) is intentionally thin glue that is not unit-tested.

The split does not add any build overhead. Both files are loaded as native ES modules. The RSVP core remains small; a framework would add `npm install` + build overhead without earning its keep. If the feature set later outgrows this (e.g. real stats UI), migrating to Vite + a small framework is a deliberate, clean cut to make then.

**Note on `file://` protocol:** Native ES module imports work in Safari and Firefox when opened via `file://`. Chrome blocks cross-origin imports on `file://` URLs; use `npx serve .` or VS Code Live Server if Chrome is required.
