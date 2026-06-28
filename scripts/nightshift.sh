#!/usr/bin/env bash
#
# nightshift.sh — launch the Ralph AFK loop over the ready-for-agent issues.
#
# Prereqs (one-time per machine): bun + @th0rgal/ralph-wiggum installed, claude CLI
# on PATH, and a ralph-prompt.md in the repo root. See the workflow cheatsheet at
# docs/agents/workflow-dayshift-nightshift.md.
#
# Usage:  ./scripts/nightshift.sh [branch-name] [max-iterations]
#
set -euo pipefail
export PATH="$HOME/.bun/bin:$PATH"

BRANCH="${1:-spreeder-v2}"
MAX_ITER="${2:-20}"

command -v ralph >/dev/null || { echo "✗ ralph not found — run: bun install -g @th0rgal/ralph-wiggum"; exit 1; }
[ -f ralph-prompt.md ] || { echo "✗ ralph-prompt.md missing in repo root"; exit 1; }

# 1. Switch to the feature's implementation branch (create it from the current HEAD if
#    needed). This is how a fresh run of v2 lands on spreeder-v2 rather than on the v1
#    line it branches from.
current="$(git branch --show-current)"
if [ -n "$current" ] && [ "$current" != "$BRANCH" ]; then
  echo "• Switching to implementation branch '$BRANCH' (from '$current')…"
  git checkout -q -b "$BRANCH" 2>/dev/null || git checkout -q "$BRANCH"
fi

# 2. Commit anything pending (PRD, issues, ADRs, this prompt) as the baseline — this is
#    the /review fixed point, so the loop's diff is pure implementation work.
if [ -n "$(git status --porcelain)" ]; then
  echo "• Committing pending planning artifacts as the baseline…"
  git add -A && git commit -q -m "chore: baseline before nightshift"
fi

# 3. Launch Ralph in the background (Sonnet, fully AFK), logging to .ralph/ (gitignored).
mkdir -p .ralph
LOG=".ralph/nightshift-$(date +%Y%m%d-%H%M%S).log"
nohup ralph \
  --prompt-file ./ralph-prompt.md \
  --agent claude-code \
  --model sonnet \
  --completion-promise ALL_ISSUES_DONE \
  --abort-promise RALPH_ABORT \
  --max-iterations "$MAX_ITER" \
  --no-questions \
  --allow-all \
  --no-stream \
  > "$LOG" 2>&1 &

echo "🌙 Nightshift gestartet"
echo "   PID:     $!"
echo "   Branch:  $(git branch --show-current)"
echo "   Log:     $LOG"
echo "   Status:  ralph --status     |     Live:  tail -f $LOG"
echo "   Morgens: /review spreeder-v1   (Basislinie, von der v2 abzweigt)"
