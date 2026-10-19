---
name: override
description: Human-only emergency override that skips the UAT gate for an urgent release, with a recorded reason and automatic follow-up issue.
argument-hint: '<ID> "<reason>"  (or: PR <number> "<reason>" for a PR with no issue)'
disable-model-invocation: true
---

# /override: skip Gate G4 (human only, Level 1)

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Request: $ARGUMENTS

See `docs/process/GATES.md` § Overrides. This skips UAT only. **CI must still pass.**

The target is an issue (`<ID>`) or, for a PR with no issue (a kit update, a config change), the PR itself: `/override PR 445 "<reason>"` or a PR link.

1. **Require a reason.** If none was given, ask for one sentence and wait.
2. **Confirm once:** "This will let <ID or PR> merge without UAT. CI is still required. Proceed? (yes/no)". Continue only on an explicit yes.
3. Find the PR (for an issue: `gh pr list --search "<ID>"`, or the PR link on the issue). Run, in this order:
   - `gh pr comment <pr> --body "OVERRIDE: <reason> (Level 1, skip UAT, by @<user>)"`. The comment **must start with `OVERRIDE:`**: that's what the `release-gate` check looks for.
   - `gh pr edit <pr> --add-label gate-override` (after the comment, so the gate's run sees both).
4. **Only when there's an issue:**
   - Tracker: comment on the issue `⚠️ Gate G4 overridden by <user>: <reason>`.
   - **Create the follow-up issue** in the tracker: title `Post-override UAT for <ID>`, labels `stream:bug`, `override-followup`, priority High, status `Ready`, description linking the original issue, PR and the UAT plan (or "UAT plan to be written").
   For a PR without an issue, skip both: there's nothing to test later against.
5. Report `gh pr checks <pr>`. `release-gate` should turn green within a minute; if it says the override comment is missing, show the human the comment you posted. If `ci` is failing, say clearly that a Level 1 override does not bypass CI and a Level 2 emergency bypass needs a repo admin in GitHub (`docs/process/GATES.md`). Do not attempt it yourself.
6. Reply with the PR link (and the follow-up issue, if any): "Ready for you to merge."
