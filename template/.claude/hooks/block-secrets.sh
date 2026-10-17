#!/usr/bin/env bash
# Claude Code PreToolUse hook (matcher: Bash).
# Before any `git commit` an agent runs, scan the changes for secrets.
# Exit code 2 blocks the tool call and shows the message to Claude,
# so the agent has to remove the secret before it can commit.
#
# It scans the folder the commit happens in: the session's current folder (which follows the
# agent into a worktree), or the folder named by `git -C <dir> commit` / `cd <dir> && git commit`.

input=$(cat)

# Only act on git commit commands (including `git -C dir commit` and `&& git commit`).
if ! printf '%s' "$input" | grep -qE '"command"[[:space:]]*:[[:space:]]*"[^"]*git([[:space:]]+-C[[:space:]]+[^[:space:]]+)?[[:space:]]+commit'; then
  exit 0
fi

dir=$(printf '%s' "$input" | python3 -c '
import json, os, re, sys
try:
    d = json.load(sys.stdin)
except ValueError:
    d = {}
cmd = (d.get("tool_input") or {}).get("command", "")
base = d.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or "."
m = re.search(r"git\s+-C\s+(\S+)\s+commit", cmd) or re.search(r"(?:^|&&|;)\s*cd\s+(\S+)\s*(?:&&|;)", cmd)
sub = m.group(1).strip("\"'"'"'") if m else ""
print(os.path.normpath(os.path.join(base, os.path.expanduser(sub))) if sub else base)
' 2>/dev/null)

cd "${dir:-${CLAUDE_PROJECT_DIR:-.}}" 2>/dev/null || cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
top=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$top" || exit 0
scan="$top/scripts/scan-secrets.sh"
[ -f "$scan" ] || scan="${CLAUDE_PROJECT_DIR:-$top}/scripts/scan-secrets.sh"
output=$(bash "$scan" 2>&1)
rc=$?

case "$rc" in
  0) exit 0 ;;
  3) echo "BLOCKED: gitleaks is not installed, so this commit can't be checked for secrets. Ask the human to install gitleaks (docs/ONBOARDING.md), then retry. Do not commit any other way." >&2
     exit 2 ;;
  *) echo "BLOCKED: possible secret in the changes you are about to commit (in $top)." >&2
     echo "$output" | tail -n 40 >&2
     echo "Remove the secret from the code (use an environment variable documented in .env.example), unstage it, and tell the human what you found. Never commit it, never weaken the scan, never add it to .gitleaksignore yourself." >&2
     exit 2 ;;
esac
