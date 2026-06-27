# Workflow cheatsheet: Dayshift → Nightshift → Review

Your standing workflow for a new feature (or a new project).

- **Dayshift** = you + Claude (Opus), interactive: grill → PRD → issues.
- **Nightshift** = Ralph (Sonnet), fully AFK in the background: implements the issues.
- **Review** = you + Opus, with Matt's `/review` skill.

---

## 0. One-time machine setup (once ever — never discuss installs again)

```bash
brew install bun                          # the Ralph runtime
bun install -g @th0rgal/ralph-wiggum      # Ralph itself → ~/.bun/bin/ralph
echo 'export PATH="$HOME/.bun/bin:$PATH"' >> ~/.zshrc   # so `ralph` is on PATH
```

The `claude` CLI is assumed already installed. Do this **before** the first project /
`git init` — it has nothing to do with any repo.

Per project, once: run `/setup-matt-pocock-skills` so the repo has the grill / to-prd /
to-issues / review skills plus the issue-tracker + triage conventions.

---

## 0b. Adapt Ralph to Matt's workflow (after install)

`@th0rgal/ralph-wiggum` is a **generic** loop with its own defaults that do **not** match
the grill→prd→issues flow. You never edit Ralph's code — you adapt it entirely through
**flags + the prompt file**. Every overridden default and why:

| Ralph default | Override | Why |
| --- | --- | --- |
| `opencode` agent | `--agent claude-code` | you run Claude Code |
| its own model | `--model sonnet` | Sonnet does the building |
| `--tasks` mode → `.ralph/ralph-tasks.md` (Ralph's *own* task tracker) | **don't use it** — the prompt points Ralph at Matt's tracker `.scratch/<feature>/issues/` | one source of truth = your issues, not a parallel list |
| completion phrase `COMPLETE` | `--completion-promise ALL_ISSUES_DONE` | distinct phrase, no accidental match |
| interactive questions on | `--no-questions` | genuinely unattended |
| permission prompts | `--allow-all` (already default) | AFK |
| auto-commit after each iteration | leave **on** | git history is Ralph's memory between fresh sessions |

The real adaptation is the **prompt file** `ralph-prompt.md` — that is what teaches a
generic loop to speak Matt's workflow. It must tell the agent to:

- pick the lowest-numbered issue with `Status: ready-for-agent` (blockers `done`) from `.scratch/<feature>/issues/`;
- obey `CLAUDE.md` + the `CONTEXT.md` glossary + `docs/adr/*` + the PRD;
- build **test-first (RED→GREEN)** at the project's TDD seam;
- tick the acceptance-criteria checkboxes, set `Status: done`, then commit;
- **not** review (you run `/review` after) and **not** touch any other issue;
- emit `ALL_ISSUES_DONE` when no `ready-for-agent` issue remains, or `RALPH_ABORT: <reason>` on a hard blocker.

Only **one** line in `ralph-prompt.md` is project-specific: the **TDD seam**. Everything
else is reusable verbatim across projects.

---

## 1. Dayshift — interactive, you drive (Opus)

In the repo, in order:

1. `/grill-with-docs` — relentless interview; crystallises decisions into `CONTEXT.md`
   (glossary) + `docs/adr/*` (ADRs). **This is the durable memory** — anything not
   written here is lost on `/clear`.
2. `/to-prd` — synthesises a PRD into `.scratch/<feature>/PRD.md`.
3. `/to-issues` — breaks it into vertical-slice issues
   `.scratch/<feature>/issues/NN-*.md`, dependency-numbered, each `Status: ready-for-agent`.

**Dayshift output:** dependency-ordered issues with acceptance criteria, all
`ready-for-agent`. That is the entire contract the nightshift runs against.

---

## 2. Prep the nightshift (mechanical, once per feature)

Two files must sit in the repo root. Copy them from a previous project; they are
generic except for one line:

- **`ralph-prompt.md`** — the fixed Ralph "promise". Adapt only the **TDD seam** line
  to this project's highest test seam (here: the pure `engine.js`). Everything else
  (select next ready issue, red→green, tick criteria, set `Status: done`, commit, don't
  review, emit `ALL_ISSUES_DONE` when none left) is reusable as-is.
- **`scripts/nightshift.sh`** — the launcher (creates a baseline commit + impl branch if
  needed, then runs Ralph AFK in the background).

---

## 3. Launch the nightshift — one command, AFK, background

```bash
./scripts/nightshift.sh                 # defaults: branch spreeder-v1, max 20 iterations
# or: ./scripts/nightshift.sh my-feature 24
```

This is the answer to "what do I do after `/to-issues`": **run that script.** It:

1. makes a baseline commit if the repo has none (= your `/review` fixed point),
2. switches to an implementation branch (never commits straight to `main`),
3. launches Ralph in the background on Sonnet, fully unattended.

**Monitor:** `ralph --status`  ·  **Live log:** `tail -f .ralph/nightshift-*.log`

**The loop stops on** one of: `ALL_ISSUES_DONE` (all issues `done`), `RALPH_ABORT:<reason>`
(unrecoverable blocker), or hitting `--max-iterations` (safety cap).

Each iteration is a **fresh Sonnet session** — always in the "smart zone". State between
iterations lives only in **git commits** + the **issue files** (`Status:` + ticked
acceptance criteria). No in-session `/handoff` is needed; the loop boundary *is* the handoff.

---

## 4. Morning — review (you + Opus)

```bash
/review main
```

Two-axis review (Standards + Spec) of the whole branch diff against the baseline. Then
merge `spreeder-v1` into `main`, or feed findings back as fixes.

---

## The full launch command (what the script runs)

```bash
ralph \
  --prompt-file ./ralph-prompt.md \
  --agent claude-code \
  --model sonnet \
  --completion-promise ALL_ISSUES_DONE \
  --abort-promise RALPH_ABORT \
  --max-iterations 20 \
  --no-questions \
  --allow-all \
  --no-stream
```

## Per-project knobs

| Knob | Where | Rule of thumb |
| --- | --- | --- |
| TDD seam | `ralph-prompt.md` | your highest pure test seam |
| Branch name | `nightshift.sh` arg 1 | `<feature>-v1` |
| Max iterations | `nightshift.sh` arg 2 | ~2–3× number of issues |
| Model | `nightshift.sh` | `sonnet` (or explicit `claude-sonnet-4-6`) |

If Ralph ever prompts for permissions despite `--allow-all`, append a passthrough to the
agent: `… --allow-all -- --dangerously-skip-permissions`.
