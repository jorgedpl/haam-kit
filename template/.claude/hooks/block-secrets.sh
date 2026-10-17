#!/usr/bin/env bash
# Claude Code PreToolUse hook (matcher: Bash).
# Before any `git commit` an agent runs, scan the changes for secrets.
# Exit code 2 blocks the tool call and shows the message to Claude,
# so the agent has to remove the secret before it can commit.
#
# It scans the folder the commit happens in: the folder named by `git -C <dir> commit` or
# `cd <dir> && … git commit`, otherwise the session's current folder (which follows the agent
# into a worktree). Never the main folder by default.

input=$(cat)

# Where does this command commit? Prints the folder, or nothing if it doesn't commit.
where=""
if command -v python3 >/dev/null 2>&1; then
  # shellcheck disable=SC2016  # the Python below is meant to be literal
  where=$(printf '%s' "$input" | python3 -c '
import json, os, shlex, sys
try:
    d = json.load(sys.stdin)
except ValueError:
    sys.exit(0)
cmd = (d.get("tool_input") or {}).get("command", "")
here = d.get("cwd") or os.environ.get("PWD") or os.environ.get("CLAUDE_PROJECT_DIR") or "."
def resolve(base, p):
    p = os.path.expanduser(os.path.expandvars(p))
    return os.path.normpath(p if os.path.isabs(p) else os.path.join(base, p))
try:
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=";&|()")
    lex.whitespace_split = True
    toks = list(lex)
except ValueError:
    toks = cmd.split()
cur, i, hit = here, 0, None
while i < len(toks):
    t = toks[i]
    if t == "cd" and i + 1 < len(toks) and toks[i + 1] not in (";", "&&", "||", "|", "&"):
        cur = resolve(cur, toks[i + 1]); i += 2; continue
    if os.path.basename(t) == "git":
        j, gdir = i + 1, cur
        while j < len(toks) and toks[j].startswith("-"):
            if toks[j] == "-C" and j + 1 < len(toks):
                gdir = resolve(gdir, toks[j + 1]); j += 2; continue
            if toks[j] in ("-c", "--git-dir", "--work-tree", "--namespace") and j + 1 < len(toks):
                j += 2; continue
            j += 1
        if j < len(toks) and toks[j] == "commit":
            hit = gdir
            break
    i += 1
if hit is None and "commit" in cmd and "git" in cmd:
    hit = here   # unusual syntax: scan the current folder rather than nothing
if hit and not os.path.isdir(hit):
    hit = here   # e.g. `cd $WT` with a variable set earlier in the same command: use the session folder
if hit:
    print(hit)
' 2>/dev/null)
else
  # No python3: scan the session folder for anything that looks like a commit.
  if printf '%s' "$input" | grep -qE 'git[^|;&]*commit'; then
    where=$(printf '%s' "$input" | sed -n 's/.*"cwd"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
    where=${where:-$PWD}
  fi
fi
[ -n "$where" ] || exit 0

cd "$where" 2>/dev/null || cd "$PWD" || exit 0
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
