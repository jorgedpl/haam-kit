#!/usr/bin/env bash
# Scans uncommitted changes (staged and unstaged) for secrets with gitleaks.
# Used by both the git pre-commit hook (.githooks/pre-commit) and the
# Claude Code PreToolUse hook (.claude/hooks/block-secrets.sh).
#
# Exit codes: 0 = clean, 1 = secret found, 3 = gitleaks not installed.

cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" || exit 1

if ! command -v gitleaks >/dev/null 2>&1; then
  echo "gitleaks is not installed, so secrets can't be checked before committing." >&2
  echo "Install it: macOS 'brew install gitleaks' · Linux: see https://github.com/gitleaks/gitleaks/releases" >&2
  exit 3
fi

cfg=()
[ -f .gitleaks.toml ] && cfg=(--config "$PWD/.gitleaks.toml")

found=0
for mode in "--staged" ""; do
  # Current CLI (gitleaks >= 8.19)
  gitleaks git --pre-commit $mode "${cfg[@]+"${cfg[@]}"}" --redact --no-banner -v . >&2
  rc=$?
  if [ "$rc" = "126" ]; then
    # Older gitleaks: fall back to the deprecated command
    gitleaks protect $mode "${cfg[@]+"${cfg[@]}"}" --redact --no-banner -v >&2
    rc=$?
  fi
  [ "$rc" != "0" ] && found=1
done

# New files not yet added to git (an agent may `git add` and commit in one command).
untracked=$(git ls-files --others --exclude-standard 2>/dev/null)
if [ -n "$untracked" ]; then
  tmp=$(mktemp -d)
  printf '%s\n' "$untracked" | while IFS= read -r f; do
    case "$f" in haam.lock.json) continue ;; esac   # fingerprints, not secrets (see .gitleaks.toml)
    [ -f "$f" ] && mkdir -p "$tmp/$(dirname "$f")" && cp "$f" "$tmp/$f"
  done
  gitleaks dir "$tmp" "${cfg[@]+"${cfg[@]}"}" --redact --no-banner -v >&2
  rc=$?
  if [ "$rc" = "126" ]; then  # older gitleaks
    gitleaks detect --no-git --source "$tmp" "${cfg[@]+"${cfg[@]}"}" --redact --no-banner -v >&2
    rc=$?
  fi
  [ "$rc" != "0" ] && found=1
  rm -rf "$tmp"
fi

if [ "$found" = "1" ]; then
  echo "" >&2
  echo "Possible secret detected in your changes (shown redacted above)." >&2
  echo "Remove it, move it to .env (git-ignored) or a secret manager, and try again." >&2
  echo "If it is a false positive, add the fingerprint to .gitleaksignore in a separate, human-reviewed commit." >&2
  exit 1
fi
exit 0
