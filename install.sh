#!/usr/bin/env bash
# HAAM kit bootstrap: fetch a released version of the kit and run its setup tool.
#
# Usage (from your project's root folder):
#   bash install.sh install [--version v1.1.0] [tool options...]
#   bash install.sh update  [--version v1.1.0] [tool options...]
#
# Without --version, the latest release is used. The kit is downloaded from
# https://github.com/jorgedpl/haam-kit to a temporary folder; nothing outside
# your project is changed. Review this script before running it.
set -euo pipefail

REPO="jorgedpl/haam-kit"
cmd="${1:-}"
shift || true
version=""
args=()
while [ $# -gt 0 ]; do
  case "$1" in
    --version) version="${2:-}"; shift 2 ;;
    *) args+=("$1"); shift ;;
  esac
done

case "$cmd" in
  install|update) ;;
  *) echo "Usage: bash install.sh install|update [--version vX.Y.Z] [options]"; exit 1 ;;
esac

command -v python3 >/dev/null || { echo "Python 3 is required."; exit 1; }
command -v curl >/dev/null || { echo "curl is required."; exit 1; }
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "Run this from inside your project's git repository."; exit 1; }

if [ -z "$version" ]; then
  version=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["tag_name"])') \
    || { echo "Couldn't find the latest release. Pass --version vX.Y.Z."; exit 1; }
fi
case "$version" in v*) ;; *) version="v$version" ;; esac

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
echo "Fetching HAAM kit $version…"
curl -fsSL "https://github.com/$REPO/archive/refs/tags/$version.tar.gz" | tar -xz -C "$tmp" --strip-components=1

target=$(git rev-parse --show-toplevel)
echo "Running: haam.py $cmd --target $target ${args[*]:-}"
python3 "$tmp/template/tools/haam/haam.py" "$cmd" --target "$target" "${args[@]+"${args[@]}"}"

if [ "$cmd" = "install" ]; then
  echo
  echo "Next: open your coding agent here and ask it to follow .agents/skills/haam-setup/SKILL.md"
  echo "(Claude Code, Cursor, Grok: /haam-setup · Codex: \$haam-setup)"
fi
