#!/usr/bin/env bash
# SessionStart hook: gives every new Claude Code session a quick picture of
# where it is, so it can link the current branch to a Linear issue.
# Output is added to the session's context. Keep it short and never fail.

set +e
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null

branch=$(git branch --show-current 2>/dev/null)
issue=$(echo "$branch" | grep -oiE '[a-z]+-[0-9]+' | head -1 | tr '[:lower:]' '[:upper:]')
changes=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
behind=$(git rev-list --count HEAD..origin/main 2>/dev/null)

echo "## Session context"
echo "- Branch: ${branch:-detached}"
if [ -n "$issue" ] && [ "$branch" != "main" ]; then
  echo "- Linked Linear issue (from branch name): $issue. Fetch it from Linear before continuing work."
fi
echo "- Uncommitted changes: ${changes:-0} file(s)"
[ -n "$behind" ] && [ "$behind" != "0" ] && echo "- Local branch is $behind commit(s) behind origin/main (as of last fetch). Rebase before opening a PR."
if [ "$branch" = "main" ]; then
  echo "- You are on main. Do not commit here; create a branch from the Linear issue first."
fi
echo "- Process: AGENTS.md, docs/process/LIFECYCLE.md. Use /next to pick up work."
exit 0
