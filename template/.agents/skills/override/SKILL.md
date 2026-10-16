---
name: override
description: Human-only emergency override that skips the UAT gate for an urgent release, with a recorded reason and automatic follow-up issue.
argument-hint: '<ID> "<reason>"'
disable-model-invocation: true
---

# /override: skip Gate G4 (human only, Level 1)

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Request: $ARGUMENTS

See `docs/process/GATES.md` § Overrides. This skips UAT only. **CI must still pass.**

1. **Require a reason.** If none was given, ask for one sentence and wait.
2. **Confirm once:** "This will let <ID> merge without UAT. CI is still required. Proceed? (yes/no)". Continue only on an explicit yes.
3. Find the PR for the issue. Run:
   - `gh pr edit <pr> --add-label gate-override`
   - `gh pr comment <pr> --body "OVERRIDE (Level 1, skip UAT) by <user>: <reason>"`
4. **Tracker:** comment on the issue `⚠️ Gate G4 overridden by <user>: <reason>`.
5. **Create the follow-up issue** in the tracker: title `Post-override UAT for <ID>`, labels `stream:bug`, `override-followup`, priority High, status `Ready`, description linking the original issue, PR and the UAT plan (or "UAT plan to be written").
6. Report `gh pr checks <pr>` status. If `ci` is failing, say clearly that a Level 1 override does not bypass CI and a Level 2 emergency bypass needs a repo admin in GitHub (`docs/process/GATES.md`). Do not attempt it yourself.
7. Reply with the PR link and follow-up issue ID: "Ready for you to merge."
