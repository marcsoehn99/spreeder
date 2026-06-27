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

BRANCH="${1:-spreeder-v1}"
MAX_ITER="${2:-20}"

command -v ralph >/dev/null || { echo "✗ ralph not found — run: bun install -g @th0rgal/ralph-wiggum"; exit 1; }
[ -f ralph-prompt.md ] || { echo "✗ ralph-prompt.md missing in repo root"; exit 1; }

# 1. Ensure a baseline commit exists — this is the /review fixed point.
if ! git rev-parse HEAD >/dev/null 2>&1; then
  echo "• No commits yet — creating baseline on $(git branch --show-current)…"
  git add -A && git commit -q -m "chore: baseline before nightshift"
fi

# 2. Ensure we are on an implementation branch, never directly on main/master.
current="$(git branch --show-current)"
if [ "$current" = "main" ] || [ "$current" = "master" ]; then
  git checkout -q -b "$BRANCH" 2>/dev/null || git checkout -q "$BRANCH"
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
echo "   Morgens: /review main"
