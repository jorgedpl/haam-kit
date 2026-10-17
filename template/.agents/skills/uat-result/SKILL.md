---
name: uat-result
description: Record the human tester's UAT outcome (Gate G4). Pass labels the PR uat-passed; fail sends the issue back to In Progress with recorded failures.
argument-hint: "<ID> pass|fail [notes on what failed]"
disable-model-invocation: true
---

# /uat-result: Gate G4 (human)

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Result: $ARGUMENTS

You are recording the human's verdict. Never decide it yourself. (Most of the time the human uses `/test`, which does this and more.)

1. **Parse** issue ID and `pass`/`fail`. If unclear, ask.
2. **Update the UAT plan** `docs/uat/<FILE-ID>-*.md` on the PR branch: fill the Results table (date, tester = current user, outcome, notes). Commit `<ID>: UAT result <pass|fail>` and push.

### On pass
3. `gh pr edit <pr> --add-label uat-passed` (this satisfies the `release-gate` check); remove issue label `uat-failed` if present.
4. Comment on the issue: `✅ UAT passed by <user>`. Status stays `UAT` until merge; the tracker moves it to `Deploying` on merge.
5. Reply: "UAT passed. Say `ship` and I'll merge, deploy and close it (`haam.py ship <ID> --human`), or merge it in GitHub yourself."

### On fail
3. Tracker: add label `uat-failed`, status `Ready`, remove the assignee (agents take `uat-failed` items first); comment `❌ UAT failed` with each failure as a checklist item (step number, expected, actual).
4. Make sure the PR does **not** have `uat-passed`.
5. If any failure is outside the spec's scope, offer to log it as a separate `/bug` instead of blocking this PR.
6. Reply: "Sent back with your notes. The next agent (`/work bugs`, or `/build <ID>`) fixes it first."
