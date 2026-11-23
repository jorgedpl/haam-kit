---
name: cadence
description: Check whether a release is due by the owner's cadence (enough passed changes, the oldest waiting too long, an urgent fix) or a phone build is due, and prepare it, asking the owner for ship, the deploy and live. Human-invoked, in the owner's chat.
argument-hint: "[now]"
disable-model-invocation: true
---

# /cadence: release on a rhythm, not every day

> **Who:** the owner's own chat in the main project folder (like `/test`): it ends in `ship`. Agent chats never run it. The owner's word stays at every gate: nothing merges without their `ship`, nothing deploys without their `go`, and nothing is closed before they say it's live.
> **When:** whenever the owner likes, e.g. at the start of the day, or on a timer in the owner's chat (`/loop 4h /cadence`). With `now`, prepare a release whatever the cadence says (on request).

Arguments: $ARGUMENTS

The owner sets the rhythm with `/haam-settings` (`grouping: release` only):
- `release_after_passed`: a release once this many changes have passed (0: only on request).
- `release_after_days`: or once the oldest passed change has waited this many days (0: off), so a quiet week still ships.
- An issue with priority `Urgent`, or the label `security`, makes a release due at once.
- `release_targets` (`config --release-target ios='apps/ios/**,packages/core/**' --human`): builds that ship on their own, such as phone apps. A build is due once `release_after_passed` changes touch its paths since its last build.

## 1. Is anything due?
1. `python3 tools/haam/haam.py cadence` (add `--json` to read it). It changes nothing.
2. If nothing is due and the argument isn't `now`: say so in one line (how many passed, the oldest's age, the next trigger) and stop.

## 2. A release is due (or `now`)
1. `python3 tools/haam/haam.py ship --all --plan`. It shows the exact release, in the tool's order (issue number), with what's left out and why, any clash, the files, protected areas and anything that looks like a migration. It changes nothing.
2. **A clash** (exit 3): two passed changes edit the same lines. Ask the owner which goes first. Their answer is `--first <ID>`; the other is left out, to rebase and test again. Never pick yourself.
3. If the project's quick checks don't run on the release PR (`ci: off`), run `make check` on a throwaway branch of the planned release only if the owner asks. The release PR still gets the AI reviews, and the full check runs before the deploy as the project's settings say.
4. Show the owner the plan in a few lines: the changes (ID, title), what's left out and why, protected areas, migrations. Ask: **`ship`**, **`ship without <IDs>`** or **`later`**.
5. On `ship`: `python3 tools/haam/haam.py ship --all --human [--first <ID>] [--without <IDs>]`. Exit 2: run it again (checks still running). Exit 3 with `deploy: manual`: the release is merged and waits for the deploy. A release merged earlier doesn't block this one: one deploy of `main` carries them all.
6. **The deploy** (`deploy: manual`): ask the owner for their `go`. Deploy the way the project's runbook says only on their `go`, verify it, then ask them to confirm it's live. On their word: `python3 tools/haam/haam.py ship --all --human --live`. That closes every release the deployed commit contains. With `deploy: github`, `ship` approves and waits for the deploy itself.
7. On `later`: nothing changes; the next `/cadence` asks again.

## 3. A build is due
For each target the report marks due ("a build is due"):
1. Tell the owner: `<target>: <N> changes since its last build` and the IDs.
2. On their word, prepare the build the way the project's runbook says (for example a phone build through the project's own make target or script). Agents never upload to a store or release to users without the owner's explicit word.
3. Once the owner says the build is done: `python3 tools/haam/haam.py cadence --built <target> --human`. The count starts again from there.

## Rules
- The cadence prepares; the owner decides. Silence ships nothing.
- Never change the cadence settings yourself; that's `/haam-settings`.
- If `ship` stops (a failed check, a conflict), show the owner what it said and stop; a failed change goes back through `/test`.
