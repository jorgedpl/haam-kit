---
name: build
description: Implement a Ready issue end to end — claim, branch, code, unit tests, local checks, PR — and hand it to review (Gate G3). Use for issues in Ready with label agent-ready, or Ready bugs.
argument-hint: "<ID>"
---

# /build: implement a ready issue

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Target: $ARGUMENTS

## 0. Preconditions (stop if any fail and say why)
- Status is `Ready`.
- Features have label `agent-ready`. Bugs need clear reproduction steps.
- Not labelled `human-only`, and not an epic (label `epic`: build its sub-issues instead); no unfinished `blocked by` issues.
- If it belongs to an epic, read the epic and its brief in `docs/epics/` for context.
- A spec exists (`docs/specs/`) for features, or a fix plan in the issue for bugs.

## 1. Claim (AGENTS.md §6)
Re-fetch the issue → if claimed by someone else, stop → assign to current user → status `In Progress` → comment ``🤖 Claimed by <user> via <agent tool> [on <machine>] · branch `<branch>` ``.
If the issue belongs to an epic that is still in `Backlog`, also move the epic to `In Progress`.
On GitHub Projects one command does it all and refuses if someone got there first: `python3 tools/haam/haam.py issue claim <number> --tool "<your tool>" --machine "<this computer>"` (bugs not yet in Ready: only with the human's OK, add `--force`).

## 2. Workspace and branch
If other agent chats may be open on this machine, work in your own worktree (`AGENTS.md` §7; `/work` sets one up). In a worktree, first run `python3 tools/haam/haam.py worktree prep` (copies local files like `.env` that `make check` may need; a worktree made with plain `git worktree add` has none) and, if it says the secret hook is off, `make hooks`.

If the issue's branch already exists on `origin` (the assessment and spec were committed there), continue on it; otherwise branch from the latest `main`:
```bash
git fetch origin
git switch <branch>                      # existing branch: tracks origin/<branch>
                                         # "already checked out at …"? the other worktree must
                                         # `git switch --detach origin/main` first (ask the human if it's another chat's)
git switch -c <branch> origin/main       # new: 123-short-title (GitHub) or Linear's branch name
```
**Batch of an epic's items** (from `/next` or `/work epic <ID>`): claim each one (GitHub: `issue claim <n> --branch <branch>`), use one branch named after the first (`12-<epic-slug>`), and one PR titled `#12 #13 #14: <summary> (epic #9)` whose description has a `Refs #n` line for each. Each bug still gets its own failing test first, and each feature's acceptance criteria their tests. Keep the batch under `max_pr_lines` changed lines (default 400); if it grows past that, open a second batch.
Reworking an issue that already has a branch (review feedback, or label `uat-failed`): read the `❌ UAT failed` comment and fix every item on it; `git switch <branch> && git pull`. If git says the branch is checked out in another worktree under `.claude/worktrees/`, continue in that worktree (Claude Code: enter it); otherwise ask the human. Then hand it over again as step 7 says for your flow, so it comes back to the human.

## 3. Plan
Read the spec and the code it points at. Post a short plan as a comment on the issue (≤ 8 bullets: approach, files, tests). If the spec turns out wrong or ambiguous, comment the question, tell the user, and stop.

## 4. Implement, test-first where practical
- For bugs: **write a failing test that reproduces the bug first**, then fix.
- For features: at least one automated test per acceptance criterion. Name tests after the criterion.
- Use only synthetic test data.
- Keep the diff in scope. Note unrelated problems as `/bug` or `/idea` issues instead.
- Update `docs/product/ARCHITECTURE.md`, `.env.example` and other docs if your change affects them.

## 5. Verify locally
Run `make check` until it passes. Also run any project-specific test skills listed in `AGENTS.md` §8 that apply to the change, and report their results. Never skip or weaken tests to get green.

## 6. Self-review before the PR
Do a security self-review of your diff and fix anything you find (Claude Code: `/security-review`; other tools: check `git diff origin/main...` against section D of `.github/review/REVIEWER.md`). Re-read your own diff (`git diff origin/main...`) against each acceptance criterion.

## 7. Hand it over
First check the issue's labels and the settings (`python3 tools/haam/haam.py settings`). **`uat:skip`** (the owner decided this change needs no test of theirs; with the setting `uat: bugs-skip`, `/triage` marks bugs that way by default): use the no-UAT lane below, whatever the flow. With `uat: always`, never use the lane. Otherwise check `"flow"` in `haam.config.json` (default `test-first`).

### No-UAT lane (`uat:skip` on the issue, every issue of a batch)
- Run `python3 tools/haam/haam.py protected`: it lists changed files in protected areas (`protected_paths` in `haam.config.json`). If it lists any, the lane doesn't apply (the gate checks the same files and won't let it through): if a PR is open, first `gh pr merge <pr> --disable-auto`, then add `human-review`, tell the owner, and hand it over through your flow as usual.
- Commits as usual; rebase on `origin/main`, `make check` green, the release note `docs/changes/<FILE-ID>.md`. No UAT plan.
- `git push -u origin <branch>`, then open the PR **ready, not draft**: `gh pr create` with the title `<ID>: <summary>`, the body from the template, and `--label uat:skip`. The checks and both AI reviews run once. The gate checks that the owner marked the issue, and on GitHub Projects the PR merges by itself when everything is green (auto-merge); the owner's next `ship` deploys it with everything else. On Linear the gate can't read the issue, so copy the label only when the Linear issue has it; the owner then ships it (`ship APP-12 --human`).
- If `"review"` is `"local"`, run `python3 tools/haam/haam.py review <ID>`. The lane then never merges by itself (local review results aren't tamper-proof): tell the owner it's ready for their `ship`.
- Fix review findings in one push per round, as usual. Don't run `/uat`: the issue goes from `In Review` to `Deploying` by itself.

### Test-first (default): the owner tests before any PR exists
Pushing a branch costs nothing; pull requests are what start CI and the reviews. So the owner tests your work first, and the PR is only opened once they've passed it.
- Commits: `<ID>: <imperative summary>`. Rebase on `origin/main`, `make check` green.
- Put everything the owner needs on the branch: the UAT plan `docs/uat/<FILE-ID>-<slug>.md` and the release note `docs/changes/<FILE-ID>.md` (as `/uat` describes).
- `git push -u origin <branch>` (free: no workflow runs on branch pushes). **Don't open a PR**: the owner's `/test` opens it after they pass the test (`haam.py publish`), already labelled `uat-passed`, and the checks run once, on exactly what they tested.
- Run `/uat <ID>`: it moves the issue to `UAT` and tells the owner.
- **Rework** (label `uat-failed`: the owner's test or the checks found problems): fix every item, push once. If a PR is already open, first turn it back into a draft (`gh pr ready --undo <number>`) so your push doesn't start the checks; the owner's next pass makes it ready again. Then `/uat <ID>` again: changed code is always tested again before it ships.
- The owner's chat handles everything after the test: the PR, the checks, the reviews and shipping. If the checks or reviews find problems, the issue comes back to you with `uat-failed` and their findings.

### Checks-first: PR and checks, then the owner tests
- Commits: `<ID>: <imperative summary>`.
- **Rework** (label `uat-failed` or review feedback): the PR already exists; collect all the fixes for the round, push them in **one** push, and comment on the PR what you changed.
- `git push -u origin <branch>`, then `gh pr create --draft` with title `<ID>: <summary>`, the body from `.github/pull_request_template.md` fully filled in (acceptance criteria checklist with test names, screenshots/notes, risks), and `--label human-review` if the issue has it. CI and the reviews don't run on drafts.
- Before marking it ready, put the UAT plan and the release note on the branch (each push after ready re-runs CI and both reviews), rebased on `origin/main`, `make check` green. Then `gh pr ready <number>`: CI and the reviews run once.
- On GitHub Projects the PR description must contain `Refs #<number>` (not `Closes`). The tracker moves the issue to `In Review` when the PR is marked ready; if it hasn't moved after a few minutes, move it yourself. Comment the PR link on the issue.

## 8. Checks and reviews (checks-first only)
1. If `haam.config.json` says `"review": "local"`, run the AI reviews on this computer now, in fresh sessions: `python3 tools/haam/haam.py review <ID>` (give it a timeout of at least 20 minutes; skip this for PRs labelled `human-review`, which GitHub reviews). It posts the `ai-review` and `security-review` results on the PR.
   Then `gh pr checks` until `ci`, `secrets`, `dependencies`, `ai-review` and `security-review` have finished.
2. Failing `ci`/`dependencies`: fix and push.
3. Failing `secrets`: **stop and tell the human immediately**. A secret in a pushed commit must be rotated and the branch history rewritten; you can't fix that alone.
4. `ai-review` / `security-review` comments: fix every Blocking item, push once, run the local review again if the project uses it, and comment on the PR which commit addresses which finding. If you disagree with a finding, reply with your reasoning and ask the human; don't change code just to satisfy the reviewer.
5. After **two** rounds that still fail, stop: post a handover comment on the issue and tell the human.
6. When everything is green, run `/uat <ID>`.

## 9. If you must stop early
Push the branch (checks-first: as a **draft** PR), and post the handover comment (Done / Not done / Next step / Gotchas).
