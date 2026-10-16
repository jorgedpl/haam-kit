#!/usr/bin/env bash
# Claude Code PreToolUse hook (matcher: Bash).
# Before any `git commit` an agent runs, scan the changes for secrets.
# Exit code 2 blocks the tool call and shows the message to Claude,
# so the agent has to remove the secret before it can commit.

input=$(cat)

# Only act on git commit commands (including `git -C dir commit` and `&& git commit`).
if ! printf '%s' "$input" | grep -qE '"command"[[:space:]]*:[[:space:]]*"[^"]*git([[:space:]]+-C[[:space:]]+[^[:space:]]+)?[[:space:]]+commit'; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
output=$(bash scripts/scan-secrets.sh 2>&1)
rc=$?

case "$rc" in
  0) exit 0 ;;
  3) echo "BLOCKED: gitleaks is not installed, so this commit can't be checked for secrets. Ask the human to install gitleaks (docs/ONBOARDING.md), then retry. Do not commit any other way." >&2
     exit 2 ;;
  *) echo "BLOCKED: possible secret in the changes you are about to commit." >&2
     echo "$output" | tail -n 40 >&2
     echo "Remove the secret from the code (use an environment variable documented in .env.example), unstage it, and tell the human what you found. Never commit it, never weaken the scan, never add it to .gitleaksignore yourself." >&2
     exit 2 ;;
esac
