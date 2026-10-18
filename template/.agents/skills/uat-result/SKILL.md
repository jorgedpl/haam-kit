---
name: uat-result
description: Record the human tester's UAT outcome (Gate G4). Pass opens the PR (test-first) or labels it uat-passed (checks-first); fail labels the issue uat-failed and sends it back to Ready with the failures recorded.
argument-hint: "<ID> pass|fail [notes on what failed]"
disable-model-invocation: true
---

# /uat-result: Gate G4 (human)

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Result: $ARGUMENTS

You are recording the human's verdict. Never decide it yourself. (Most of the time the human uses `/test`, which does this and more.)

1. **Parse** issue ID and `pass`/`fail`. If unclear, ask.
2. **Record the result as comments**, not commits (a commit would change what was tested and re-run the checks): on the issue (and the PR, if there is one), `UAT <pass|fail> by <user> on <date>` plus the notes.

### On pass
3. Remove issue label `uat-failed` if present.
   - **Test-first (`"flow"` in `haam.config.json`, the default; no PR yet, or one turned back into a draft):** the pass only counts for the commit the human tested, so it must have been set up with `python3 tools/haam/haam.py checkout-pr <ID>`. If it was, run `python3 tools/haam/haam.py publish <ID> --human` (as `/test` step 3a describes): it opens the PR labelled `uat-passed` and moves the issue to `In Review`. If it wasn't, say so and suggest `/test <ID>` instead.
   - **Checks-first (the PR exists and its checks passed):** `gh pr edit <pr> --add-label uat-passed` (this satisfies the `release-gate` check). Status stays `UAT` until merge; the tracker moves it to `Deploying` on merge.
4. A push after the pass removes `uat-passed` again (the gate does it), so the new code is tested again.
5. Reply: "UAT passed. Say `ship` and I'll merge, deploy and close it (`haam.py ship <ID> --human`), or merge it in GitHub yourself."

### On fail
3. Tracker: add label `uat-failed`, status `Ready`, remove the assignee (agents take `uat-failed` items first); comment `❌ UAT failed` with each failure as a checklist item (step number, expected, actual).
4. Run `python3 tools/haam/haam.py test-failed <ID> --human`: it withdraws any earlier pass of that commit and removes `uat-passed` from the PR, if there is one.
5. If any failure is outside the spec's scope, offer to log it as a separate `/bug` instead of blocking this PR.
6. Reply: "Sent back with your notes. The next agent (`/work bugs`, or `/build <ID>`) fixes it first."
