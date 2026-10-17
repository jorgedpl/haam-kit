---
name: test
description: The product owner's one command for testing (Gate G4) and shipping (G5). Sets the change up on this machine, walks the human through the test plan, then on "pass" and "ship" merges, deploys and closes; on a failure records what's wrong and sends it straight back to an agent.
argument-hint: "[ID]  (empty: the oldest item waiting in UAT)"
disable-model-invocation: true
---

# /test: test it, then ship it or send it back

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Target: $ARGUMENTS

This skill runs only when a human types it, in their own chat in the project's main folder. The human gives the verdict; you do all the mechanics. Keep your messages short: the human wants to test, not read.

## 1. Pick what to test
If no ID was given, list what's waiting: issues in `UAT` (GitHub: `python3 tools/haam/haam.py issue list --status UAT --open-only`), oldest first. One item → take it. Several → show them (ID, title, waiting since) and suggest the oldest; wait for the choice.

## 2. Get it running
1. `python3 tools/haam/haam.py checkout-pr <ID>`. It refuses if the human has unsaved changes in this folder; if so, say so and offer `git stash`.
2. `make setup`, then start `make dev` **in the background** (if your tool can't run background commands, ask the human to run `make dev` in a terminal). Wait until it's up.
3. Tell the human, in one short message: the URL to open, any test account from the plan (synthetic only), and the test cases from the plan (`docs/uat/<FILE-ID>-*.md`) as a numbered checklist: *do this → you should see that*. Include the plan's "Agent pre-check" result if there is one.
4. End with: *"Reply `pass`, or tell me what went wrong (which step, what you saw)."* Wait.

## 3a. It passed
1. Record it as `/uat-result <ID> pass` does: fill the Results table in the plan, commit on the PR branch (you're on a detached checkout: `git commit` then `git push origin HEAD:<branch>`), add PR label `uat-passed`, remove `uat-failed` if present, comment `✅ UAT passed by <user>`.
2. Ask: *"Ship it to production now? Reply `ship` or `later`."* Wait.
3. On `ship`: `python3 tools/haam/haam.py ship <ID> --human`. It waits for the checks, merges, approves the production deploy for the human, waits for it, then closes the issue. If it hands back with "Still waiting…", run the same command again. If the human says it was deployed some other way, add `--no-deploy`.
4. If `make smoke` exists, run it against production and report. If it fails, tell the human at once and offer `/bug` with priority Urgent.
5. Reply: *"<ID> is live."* plus anything the tool said (for example, that it was the last issue in its epic).
6. On `later`: *"Passed. Type `/test <ID>` and reply `ship` when you're ready, or merge it in GitHub yourself."*

## 3b. It failed
1. Record it as `/uat-result <ID> fail` does: fill the Results table, comment `❌ UAT failed` on the issue with each failure as a checklist item (step, expected, actual), make sure the PR doesn't have `uat-passed`.
2. Send it back to the agents: add issue label `uat-failed`, set status `Ready`, remove the assignee. Agents take `uat-failed` items before anything else.
3. If something the human found is outside this change's scope, offer to log it as a separate `/bug` instead.
4. Restart the fix straight away if you can: in Claude Code, start a background worker in its own worktree that runs `/build <ID>` (it continues on the same branch). Otherwise tell the human: *"Open a new chat and type `/work bugs`: it takes this one first."*
5. Reply: *"Sent back with your notes. It'll come back to you for another test."*

## 4. Tidy up
Stop `make dev` and run `python3 tools/haam/haam.py checkout-pr --back`. If more items are waiting in UAT, offer the next one.
