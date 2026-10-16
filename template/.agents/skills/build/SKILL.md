---
name: build
description: Implement a Ready Linear issue end to end — claim, branch, code, unit tests, local checks, PR — and hand it to review (Gate G3). Use for issues in Ready with label agent-ready, or Ready bugs.
argument-hint: "APP-123"
---

# /build: implement a ready issue

Target: $ARGUMENTS

## 0. Preconditions (stop if any fail and say why)
- Status is `Ready`.
- Features have label `agent-ready`. Bugs need clear reproduction steps.
- Not labelled `human-only`; no unfinished `blocked by` issues.
- A spec exists (`docs/specs/`) for features, or a fix plan in the issue for bugs.

## 1. Claim (AGENTS.md §6)
Re-fetch the issue → if claimed by someone else, stop → assign to current user → status `In Progress` → comment `🤖 Claimed by <user> via <agent tool> · branch <branch>`.

## 2. Branch
```bash
git fetch origin && git switch main && git pull --ff-only
git switch -c <branchName from Linear>
```

## 3. Plan
Read the spec and the code it points at. Post a short plan as a Linear comment (≤ 8 bullets: approach, files, tests). If the spec turns out wrong or ambiguous, comment the question, tell the user, and stop.

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

## 7. Pull request
- Commits: `APP-123: <imperative summary>`. Rebase on `origin/main`.
- `git push -u origin <branch>`, then `gh pr create` with title `APP-123: <summary>` and the body from `.github/pull_request_template.md`, fully filled in (acceptance criteria checklist with test names, screenshots/notes, risks).
- Add PR label `human-review` if the issue has it.
- Linear automation moves the issue to `In Review`. Comment the PR link on the issue.

## 8. Wait for checks and reviews
1. `gh pr checks` until `ci`, `secrets`, `dependencies`, `ai-review` and `security-review` have finished.
2. Failing `ci`/`dependencies`: fix and push.
3. Failing `secrets`: **stop and tell the human immediately**. A secret in a pushed commit must be rotated and the branch history rewritten; you can't fix that alone.
4. `ai-review` / `security-review` comments: fix every Blocking item, push, and comment on the PR which commit addresses which finding. If you disagree with a finding, reply with your reasoning and ask the human; don't change code just to satisfy the reviewer.
5. After **two** rounds that still fail, stop: post a handover comment on Linear and tell the human.
6. When everything is green, run `/uat <ISSUE-ID>`.

## 9. If you must stop early
Push, open the PR as **draft**, post the handover comment (Done / Not done / Next step / Gotchas).
