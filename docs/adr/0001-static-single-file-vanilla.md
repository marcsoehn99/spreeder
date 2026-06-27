# Static single-file vanilla app, no build step

spreeder is built as a single static HTML file with inline CSS/JS (vanilla, no framework, no server, no build). The whole value of "local" is frictionlessness: double-click to open, runs offline anywhere, copy/paste of agent output is native. The RSVP core is small (a timer plus DOM updates), so a framework would add `npm install` + build overhead without earning its keep. If the feature set later outgrows this (e.g. real stats UI), migrating to Vite + a small framework is a deliberate, clean cut to make then.
