---
name: release
description: After a production deploy, verify it, close the issue as Done and update the changelog (Gate G5 wrap-up). Human-invoked.
argument-hint: "<ID>"
disable-model-invocation: true
---

# /release: close out after production deploy

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Target: $ARGUMENTS

1. **Check the deploy:** `gh run list --workflow deploy.yml --limit 5`. Find the run for the merge commit of this issue's PR. If it is waiting for approval, tell the user to approve it in GitHub (Actions → the run → Review deployments) and stop. If it failed, show the failing step and stop.
2. **Smoke check:** if `make smoke` exists, run it against production (`SMOKE_URL` from `docs/product/ARCHITECTURE.md`). Report results. If it fails, tell the user immediately and suggest `/bug` with priority Urgent. Don't close the issue.
3. **Changelog:** on a branch `docs/<issue-id>-release`, add an entry under today's date in `CHANGELOG.md`: `- <ID>: <user-facing summary>`. Open a docs PR.
4. **Tracker:** status `Done` (GitHub Projects: `haam.py issue close <number> --human`, which also closes the issue); comment `🚀 Released to production <date> · deploy run <link>`.
5. If the release was an override, remind the user that the `override-followup` issue is still open.
6. Reply with a one-line summary.
