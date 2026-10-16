---
name: uat-result
description: Record the human tester's UAT outcome (Gate G4). Pass labels the PR uat-passed; fail sends the issue back to In Progress with recorded failures.
argument-hint: "APP-123 pass|fail [notes on what failed]"
disable-model-invocation: true
---

# /uat-result: Gate G4 (human)

Result: $ARGUMENTS

You are recording the human's verdict. Never decide it yourself.

1. **Parse** issue ID and `pass`/`fail`. If unclear, ask.
2. **Update the UAT plan** `docs/uat/<ISSUE-ID>-*.md` on the PR branch: fill the Results table (date, tester = current user, outcome, notes). Commit `APP-123: UAT result <pass|fail>` and push.

### On pass
3. `gh pr edit <pr> --add-label uat-passed` (this satisfies the `release-gate` check).
4. Linear comment: `✅ UAT passed by <user>`. Status stays `UAT` until merge; Linear moves it to `Deploying` on merge.
5. Reply: "UAT passed. The PR is ready for you to merge. Merging starts the production deploy, which will ask you to approve it in GitHub."

### On fail
3. Linear: status `In Progress`; comment `❌ UAT failed` with each failure as a checklist item (step number, expected, actual).
4. Make sure the PR does **not** have `uat-passed`.
5. If any failure is outside the spec's scope, offer to log it as a separate `/bug` instead of blocking this PR.
6. Reply: "Sent back to In Progress. Run `/build APP-123` (or I can continue now) to fix the failures."
