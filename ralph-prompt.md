# Ralph loop prompt — spreeder v1 implementation

You are running inside a Ralph loop. Each invocation is a **fresh session**. Your
job is to implement the spreeder v1 issues, **one issue per iteration**, until all
are done. State carries between iterations only via **git history** and the
**issue files on disk** — there is no other memory.

You are running **fully unattended (AFK)**. Never ask the user a question. Make the
most reasonable decision and proceed.

## First: check if the work is finished

Look at every file in `.scratch/spreeder-v1/issues/`. If **none** of them contains
a line `Status: ready-for-agent`, then all work is complete. In that case:

- Output exactly this phrase and nothing else, then stop: `ALL_ISSUES_DONE`

Otherwise, continue below.

## Select exactly ONE issue

Pick the **lowest-numbered** issue file whose `Status:` is `ready-for-agent` **and**
whose every "Blocked by" issue already has `Status: done`. (The numbering already
encodes dependency order, so the lowest-numbered ready issue is normally correct —
but verify the blockers are `done` before starting.)

Work on **only that one issue** this iteration. Do not touch any other issue's
scope or `Status`.

## Implement it

Read, and obey, in this order of authority:

1. `CLAUDE.md` (project conventions, issue-tracker rules)
2. `CONTEXT.md` (domain glossary — use this vocabulary: RSVP, chunk, ORP, WPM, session)
3. `docs/adr/*` (architecture decisions — especially: ADR-0001 two-file shape
   `index.html` + `engine.js`, no build step; ADR-0002 no progress tracking,
   settings-only persistence; ADR-0003 strip markdown / remove code blocks)
4. `.scratch/spreeder-v1/PRD.md` (the spec)
5. The selected issue file (the precise slice + acceptance criteria)

Build the work **test-first (RED → GREEN)** at the agreed seam: the pure module
`engine.js`. Write a failing unit test that imports `engine.js` directly in Node,
watch it fail, then make it pass. The shell (`index.html`: timer, DOM, the red ORP
rendering, controls, `localStorage`) is thin glue and is **not** unit-tested.

- Run the relevant single test file(s) frequently as you go.
- Run typechecking if the project has it configured.
- Run the **full test suite once** before you finish the issue; it must be green.

## Finish the issue

When the issue is fully implemented and all its tests pass:

1. Tick every acceptance-criteria checkbox in the issue file (`- [ ]` → `- [x]`).
2. Change that issue file's `Status:` line to `Status: done`.
3. Commit your work with a message referencing the issue, e.g.
   `feat: <slice> (issue NN)`. End the commit message with:
   `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`
4. **Do NOT run a review** — a human reviews with `/review` after the loop.
5. **Do NOT** start the next issue. End the iteration.

## If an issue is too large for one session

If you cannot finish the selected issue within this session, commit the partial,
**green** progress (never commit failing tests), leave its `Status:` as
`ready-for-agent` with whichever acceptance criteria are genuinely done ticked, and
end. The next fresh iteration will continue from your commit.

## If you hit an unrecoverable blocker

If something makes progress impossible (e.g. the repo is broken, tests can't run at
all, or an issue's spec is self-contradictory), do not burn iterations. Output a
line starting with `RALPH_ABORT:` followed by a one-line reason, and stop.
