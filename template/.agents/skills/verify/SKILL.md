---
name: verify
description: Verify a handed-over change as an independent agent, at the exact commit the builder handed over, and record the verdict with the lane's own marks (verified, not-verified or needs-owner). Use with the setting uat agents-verify, for issues in In Review with the label verifying or spot-check.
argument-hint: "<ID>"
---

# /verify: an independent check at the handed-over commit

> **Tracker:** GitHub Projects only (`python3 tools/haam/haam.py issue …`). The setting `uat: agents-verify` needs it. `<ID>` means `#123`.

Target: $ARGUMENTS

With the setting `uat: agents-verify`, a change that needs no person to judge it, and touches none of the owner's own areas (`owner_test_paths`), is checked by you instead of waiting in `UAT`. You stand in for the owner's test, so you are independent and strict. Your verdict is recorded with its own marks (the commit status `agent-verified`, the label `verified-by-agents`, a `🔎` comment), never the owner's. The owner is told, can pull the ticket back, and it ships only on their `ship`.

**What you never do:**
- **Never edit the branch.** You fix nothing, commit nothing, push nothing. Problems go in your verdict.
- Never verify a change you built, or one whose builder briefed you. Read nothing from the builder's chat.
- Never post the `uat` status, never add `uat-passed`, `uat:skip` or `verified-by-agents` yourself, never remove `owner-test`. You record only through `haam.py verify-result`.
- Never use a production host, a deploy, ssh or credentials. Use the test accounts and fixtures the plan names (synthetic only).

## 1. Claim it
1. `python3 tools/haam/haam.py issue claim <number> --for verify --tool "<your tool and model>" --machine "<this computer>"`. It refuses an issue that isn't waiting for a verifier (status `In Review` with `verifying`, or `spot-check`) or that another verifier claimed. Keep the claim id it prints.
2. **A spot-check** (label `spot-check`): the ticket was verified already, and you are the second verifier. Use another model or tool than the first one (its `🔎 Verified by agents` comment names it); `verify-result` refuses the same one.

## 2. Your own worktree, detached at the handed-over commit
1. Your own worktree (`AGENTS.md` §7; `/work` step 1 sets one up), then `python3 tools/haam/haam.py worktree prep`.
2. Read the head from the newest `🧪 Ready for verification` comment (``branch `<branch>` · head <sha>``). Then `git fetch origin && git switch --detach <sha>`. Never `git switch <branch>`: a worktree with the branch checked out can't record a verdict.
3. If `git rev-parse origin/<branch>` isn't that head, the branch moved after the hand-over. Verify the new head only if a new `🧪 Ready for verification` names it; otherwise release the claim (`issue release <number> --claim <id>`) and say so.

## 3. Read, and only these
- the issue and its comments (the `🔍 Pre-UAT review` comment, if there is one, is evidence to weigh, not a verdict);
- the spec (`docs/specs/<FILE-ID>-*.md`) and its acceptance criteria;
- the UAT plan (`docs/uat/<FILE-ID>-*.md`), with its *Agent pre-check* and *Evidence*;
- the change: `git diff origin/main...HEAD`;
- `.github/review/REVIEWER.md` (section D for protected areas) and the project's own checklists, if `AGENTS.md` names any.

## 4. Check the lane
`python3 tools/haam/haam.py lane <number>`. If it says `owner`, stop: release your claim and say why. Then answer for yourself: *would a person have to use this to judge it?* (a screen's layout, wording the spec doesn't fix word for word, anything on a phone or another device, feel or speed, a third-party sign-in or payment). If yes, the verdict is `needs-owner`.

## 5. Run it and try to break it
1. Run the tests the plan's evidence names, at this commit. Heavy runs (anything `heavy_runs` in `haam.config.json` lists, or any `make check`) go through `python3 tools/haam/haam.py exclusive "<this chat, #ID>" -- <command>`. A failure right after another chat's run is worth one rerun through `exclusive` before you call the change broken.
2. For each acceptance criterion: check it holds, then try once to break it (an edge case, a bad input, an empty state, the order of steps). Note how.
3. Run the plan's test cases yourself where you can (`make dev`, `make e2e`, a browser tool), and the regression check of the main journey.
4. Read the diff against the checklists of step 3: what it changes beyond the spec, what it forgets (errors, tests, docs), data handling, secrets.

## 6. Write the card
A short markdown file (not committed): **what changed**, **the risk** (low, medium or high, in one line), **what you checked** (each criterion: the command or run, and what you saw), **what you didn't check**, and **how to undo it**. For `not-verified`, list each finding as a `- ` line: step, expected, actual.

## 7. Before `not-verified`: a second look at each serious finding
A finding that would send the ticket back goes to a **second fresh session** first (Claude Code: a subagent with no context but the finding, the spec and the diff; other tools: a new chat). Ask it to **disprove** the finding: reproduce it at this commit, or show why it isn't one. Keep only the findings it couldn't disprove. If none survive, the verdict is `verified` (say in the card what was raised and why it fell).

## 8. Record the verdict
`python3 tools/haam/haam.py verify-result <number> --verdict <verdict> --head <sha> --claim <id> --tool "<your tool and model>" --body-file <card>`. It checks that `<sha>` is the branch's tip on GitHub, that the lane is still `agents`, that your claim isn't the build's claim and that this worktree doesn't have the branch checked out. Then it records the verdict and releases your claim:
- **`verified`**: the status `agent-verified` on that commit, a `🔎 Verified by agents` comment with your card, `verifying` → `verified-by-agents`. The issue stays `In Review` and joins the next release when the owner says `ship`. (During the shadow start, `agents_verify_shadow`, it also goes to `UAT` for the owner's test. Every 10th verified ticket gets `spot-check`.)
- **`not-verified`**: a `🔎 Not verified` comment with each finding as a checklist item, label `verify-failed`, status `Ready`, no assignee. An agent reworks it (`/build`) and hands it over again; it comes back to a verifier.
- **`needs-owner`** (add `--reason "<why>"`): a `🔎 Needs your test: <reason>` comment, label `owner-test`, status `UAT`. Use it when a person must judge it, when the change can't be checked where you are, or when it was sent back `max_review_rounds` times (then it's the only verdict left).

A later push to the branch ends a verification: only a tip that differs from the verified commit in `docs/uat/` or `docs/changes/` alone still counts.

## 9. Reply
One line: the ID, the verdict, the commit, and the card's risk line. If the builder disagrees with your findings, they reply on the issue and ask the owner; no third agent decides (`AGENTS.md` §5).
