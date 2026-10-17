---
name: release
description: After a production deploy, verify it, close the issue as Done and update the changelog (Gate G5 wrap-up). Human-invoked.
argument-hint: "<ID>"
disable-model-invocation: true
---

# /release: close out after production deploy

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Target: $ARGUMENTS

0. **Usually not needed:** `/test` → `ship` does all of this. Use `/release` when the PR was merged some other way.
1. **Ship it:** `python3 tools/haam/haam.py ship <ID> --human`. It finds the merged PR, approves the waiting production deploy, waits for it and closes the issue (status `Done`, with a comment linking the deploy run). If it says "Still waiting…", run it again. If the deploy failed, show the human the run and stop.
2. **Smoke check:** if `make smoke` exists, run it against production (`SMOKE_URL` from `docs/product/ARCHITECTURE.md`). Report results. If it fails, tell the user immediately and suggest `/bug` with priority Urgent.
3. **Changelog:** the entry was added to `CHANGELOG.md` on the PR branch by `/uat`, so it shipped with the change. If it's missing, add it in a small docs PR.
4. **Linear projects:** set the issue to `Done` and comment the deploy link (the tool tells you).
5. If the release was an override, remind the user that the `override-followup` issue is still open.
6. **Epic:** if the issue belongs to an epic and every other sub-issue is now Done or Canceled, tell the user and offer to close the epic too (status `Done`; GitHub: `haam.py issue close <epic> --human`, after they say yes).
7. Reply with a one-line summary.
