# Gates and overrides

Five gates stand between an idea and production. Each one has a clear owner, a checklist, and where possible an automated enforcement point so the rule doesn't depend on anyone remembering it.

| Gate | Between | Owner | Enforced by |
|---|---|---|---|
| **G1 Decision** | Discovery → Backlog | Human (PO) | Tracker status: only humans run `/decide` |
| **G2 Ready** | Backlog → Ready | Human approves spec | `agent-ready` label; agents only build `agent-ready` issues |
| **G3 Verified** | In Progress → UAT | Automated checks + independent reviewer agent (+ human for protected areas) | Required checks `ci`, `secrets`, `dependencies`, `ai-review`, `security-review` |
| **G4 Accepted** | UAT → merge | Human tester | Required check `release-gate` (needs PR label `uat-passed` or `gate-override`). Only the owner's or a backup approver's labels count. |
| **G5 Released** | merge → production | Human (PO) | GitHub environment `production` with required reviewer |

The table shows the checks-first order. In the default test-first flow, G4 comes before G3: you test the agent's branch first, then the checks run once on what you passed (see the G4 checklist).

---

## G1 Decision checklist

The assessment (or, for an idea built as a prototype, the prototype's notes from `/spike`) must contain:
- [ ] Problem statement and who it's for
- [ ] Value estimate with evidence (or an explicit "no evidence yet")
- [ ] Effort size with reasoning from the codebase
- [ ] Risks: security, data protection (e.g. GDPR), regulatory, operational
- [ ] At least two options plus "do nothing"
- [ ] A recommendation

The human answers one of: **approve** (with priority), **park** (with revisit trigger), **reject** (with reason). For a prototype, they try it first (`/test`), so the decision rests on using it rather than reading about it.

## G2 Definition of Ready

An issue may get `agent-ready` only when:
- [ ] Spec exists in `docs/specs/` and is linked from the issue
- [ ] Acceptance criteria are written as Given / When / Then and each one is testable
- [ ] Scope and **out of scope** are explicit
- [ ] Files/modules likely touched are listed
- [ ] Data, migration and config impact stated (or "none")
- [ ] Unit test plan and UAT outline included
- [ ] Size ≤ 1 day of agent work (~400 changed lines); otherwise split into sub-issues
- [ ] Protected areas touched are flagged (`human-review` label added)
- [ ] Priority set
- [ ] Human approved the spec

## G3 Verified (Definition of Done for code)

- [ ] Every acceptance criterion has at least one automated test
- [ ] `make check` passes locally and in CI (lint, types, unit tests, build)
- [ ] No unrelated changes in the diff
- [ ] Docs touched by the change are updated (`ARCHITECTURE.md`, API docs, env var list)
- [ ] No secrets, no real personal data in code, tests or fixtures
- [ ] PR description follows the template and links the issue (`Refs #123` on GitHub Projects, ID in the title on Linear)
- [ ] `secrets` check green: no keys, tokens or passwords in any commit of the PR
- [ ] `dependencies` check green: no known high/critical vulnerabilities
- [ ] `ai-review` green: independent reviewer agent found no blocking issues
- [ ] `security-review` green: Claude security review found no vulnerabilities
- [ ] Human code review done if the `human-review` label is present

### How code review works

Review is layered so that **no agent ever reviews its own work** and **secrets are caught by deterministic tools, not by judgement**.

| Layer | When | What | Who / what does it |
|---|---|---|---|
| 1. Local secret guard | Before every commit | Blocks commits containing keys/tokens | gitleaks via the git pre-commit hook (everyone, any tool), plus agent-tool hooks where supported (Claude Code; Grok) |
| 2. Self-check | Before opening a PR | `make check` + `/security-review` on own changes | The building agent |
| 3. Deterministic CI | Every PR push | Tests, lint, types, secret scan of every commit, dependency audit | GitHub Actions (`ci`, `secrets`, `dependencies`) |
| 4. Independent AI review | Every PR push (not drafts or docs-only) | Spec conformance, honest tests, correctness, project rules; security vulnerabilities | A separate Claude in GitHub Actions that never saw the code being written (`ai-review`, `security-review`) |
| 5. Human review | PRs labelled `human-review` | Protected areas: core logic, auth, payments, personal data, migrations, infra | Product owner or a designated developer |
| 6. Human acceptance | Every code PR | Behaviour works for real (G4 UAT) | Product owner |

**Rules for the review loop**
- The building agent reads the reviewer's comment, fixes every **Blocking** item and pushes; the reviews re-run automatically.
- If the building agent believes a finding is wrong, it replies on the PR explaining why and asks the human. It never argues in circles: **after two review rounds** that still fail, it stops and hands over to the human.
- Only the owner (or a backup approver) can overrule an AI review, with the PR label `ai-review-overruled`. This is recorded on the PR. It counts only when the login that added it is `product_owner_github` or one of `backup_approvers_github` in `haam.config.json` on the base branch, never a bot.
- AI reviewers can't approve or merge. They can only block.

### If a secret ever reaches GitHub
1. **Revoke and rotate it immediately** with the provider. Assume it is compromised; removing it from the code does not un-leak it.
2. Remove it from the code; use an environment variable documented in `.env.example`.
3. A repo admin rewrites the branch history before merge (a new commit is not enough).
4. Log a `/bug` with priority Urgent to record what happened and what was rotated (never include the secret itself).

**The owner's settings change how G3 runs, not who decides** (`/haam-settings`):
- `ci`: every PR, local (`ci-local`, posted by `haam.py local-ci` on the owner's computer), or off.
- `review`: GitHub, local, protected areas only, or off.
- `nightly`.

The required checks follow the settings (`settings --apply`). The secret scan always runs.

## G4 Accepted (UAT)

In the default test-first flow, G4 comes before G3: the owner tests the agent's pushed branch before a PR exists, and G3 then checks exactly the commit they passed (`haam.py publish`, then `ship`, which refuses anything else).

**No-UAT lane:** G4 is decided up front instead. When the owner marks an issue `uat:skip` (in `/triage`, or "spec approved, no UAT"), the agent opens the PR with the same label and `release-gate` passes once every issue the PR is for carries it (GitHub Projects: the gate reads the issues; Linear: it trusts the PR label). Never when the PR changes a protected area: the gate checks the changed files against `protected_paths` in `haam.config.json` on `main` (agent and CI configuration by default, plus the project's own), adds `human-review` and keeps the lane closed, whatever the labels say. So a kit update never takes the lane: it changes agent configuration, and you review and ship it yourself. G3 still applies in full, and auto-merge (needs `HAAM_PROJECT_TOKEN`) merges only when every required check passes. There's no auto-merge on Linear, nor when CI or either AI review runs anywhere but on GitHub for every PR (auto-merge needs `ci: every-pr` and `review: github`): local results aren't tamper-proof and reduced checks aren't enough on their own, so the owner ships those lane PRs (`ship`), which is still one decision for many. Only a human's decision adds `uat:skip` to an issue (`issue create` and `issue label` refuse it without `--human`).

**Agents' lane** (the setting `uat: agents-verify`, GitHub Projects): for a change whose plan says `Needs a person: no` and that touches none of the owner's own areas (`owner_test_paths`), G4 is an independent verifier agent instead of the owner's test. `haam.py lane <ID>` decides, and the owner's lane always wins: the label `owner-test`, rework after `uat-failed`, a file under `owner_test_paths` (a renamed file by both names), commits kept from a prototype, or a plan that says `yes` or nothing. A fresh chat that didn't build the change checks it at the handed-over commit and records its verdict with its own marks: the commit status `agent-verified`, the label `verified-by-agents` and a `🔎 Verified by agents` comment, never `uat` or `uat-passed`. The owner is told, can pull any ticket back before `ship` (`test <ID> myself` adds the label `owner-test`, which only they remove), and nothing ships without their `ship`. A push after the verification ends it, unless it changes only `docs/uat/` or `docs/changes/`. The first `agents_verify_shadow` verified tickets (10 by default) still go to the owner's test as well, and every 10th one is verified again on another model (`spot-check`). Setting `uat` back to `owner-decides` makes every ticket not yet shipped the owner's test again.

- [ ] UAT plan exists in `docs/uat/` with numbered steps and expected results
- [ ] Human ran it locally on the branch (test-first: the agent's pushed branch, before any PR; checks-first: the PR branch)
- [ ] All steps pass, or failures are recorded and accepted as follow-up issues
- [ ] The human's pass (`/test` or `/uat-result <ID> pass`) adds the `uat-passed` label to the PR (test-first: `publish` also records it on the tested commit as the `uat` status)
- [ ] The pass covers the code that merges: a push after it removes `uat-passed` (`gates.yml`), unless the new head is the tested commit; `ship` merges only that commit

## G5 Released

- [ ] PR merged to `main` by a human, or by `haam.py ship --human` after the human said `ship`
- [ ] Production deploy approved (environment `production`): in GitHub, or by `ship` on the human's word
- [ ] Post-deploy smoke check passed (`make smoke`, if defined)
- [ ] The issue is marked Done (`ship`, or `/release` for changes merged another way); the release note in `docs/changes/` shipped with it

---

## Overrides

Sometimes production is on fire or a deadline won't wait. Overrides exist for that and are **human-only**.

### Level 1: skip UAT (most common)
Use when the fix is urgent and verified by tests but there's no time for a full UAT cycle.

1. Human runs `/override <ID> "<reason>"` (for a PR with no issue: `/override PR <number> "<reason>"`), or manually comments `OVERRIDE: <reason>` on the PR (the comment must start with `OVERRIDE:`) and adds the PR label `gate-override`. Both count only from the owner's or a backup approver's login (`product_owner_github`, `backup_approvers_github` in `haam.config.json` on main), never a bot; the same holds for `uat-passed` and for the issue's `uat:skip`. While agents sign in to GitHub as the owner, GitHub cannot tell the owner from an agent, so this stops bots and every other account, not an agent that ignores the rules. The release gate runs from main's copy of `gates.yml` (`pull_request_target`), so a PR cannot rewrite the gate that judges it.
2. The `release-gate` check passes on the override label.
3. CI (`ci` check) **still must pass**.
4. When the PR has an issue, the agent creates a follow-up issue in the tracker: `Post-override UAT for <ID>` (priority High, label `stream:bug`, `override-followup`), so the skipped verification still happens after the fact.

### Level 2: emergency bypass (rare)
Use only when CI itself is broken or blocking a production fix.

1. A repository admin merges with "bypass branch protections" in GitHub.
2. The admin comments `EMERGENCY BYPASS: <reason>` on the PR.
3. Follow-up issue created as above, plus a second one to fix whatever blocked CI.

### Override rules
- Agents **never** add `gate-override`, never bypass protections, and never suggest overriding unless the human raises it first.
- Every override must have a written reason on the PR.
- Overrides are reviewed at the weekly backlog review: filter the tracker by label `override-followup`.
