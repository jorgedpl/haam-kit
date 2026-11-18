---
name: haam-settings
description: Walk the product owner through this project's HAAM settings: when CI and the AI reviews run, what they test themselves, how changes are grouped and shipped, and the limits. Show each choice's trade-off with real numbers, apply what they choose, and sync GitHub. Use when the owner asks to change how HAAM works, or to cut CI cost.
argument-hint: "[area: testing | grouping | checks | shipping | limits | all]  (default: all)"
disable-model-invocation: true
---

# /haam-settings: the owner decides how HAAM runs here

Area: $ARGUMENTS (empty = all)

This skill runs only when a human types it, in their own chat in the project's main folder. You explain and apply; **the human chooses**. Never change a setting they didn't choose.

## 1. Where things stand
1. `python3 tools/haam/haam.py settings --explain --json`: every setting with its current value, default, options and trade-off. `docs/setup/DECISIONS.md` has when to choose each option, how to size the limits and what to protect: use it for your recommendations.
2. For real numbers, also run:
   - `python3 tools/haam/haam.py ci-usage --days 7`: Actions minutes by workflow;
   - `python3 tools/haam/haam.py capacity --list`: open PRs and the UAT queue.

   Use the numbers to make the trade-offs concrete, e.g. *"the AI reviews were 60% of your minutes last week"*.

## 2. Go through the choices, one area at a time
For each area (or only the one asked for), show a short table: setting · now · options · what it means for them. Recommend one option and say why in one line, based on their numbers, not in general. Ask: *"Keep, or change? (e.g. `ci local`, `review protected-only`)"*. Then wait.

The areas and their settings:
- **Testing:**
  - `flow` (test-first | checks-first);
  - `uat` (owner-decides | always | bugs-skip).
- **Grouping:** `grouping` (per-issue | per-epic | release).
- **Checks:**
  - `ci` (every-pr | local | off);
  - `nightly` (on | off);
  - `review` (github | local | protected-only | off);
  - `runner` (github | self-hosted).
- **Shipping:**
  - `deploy` (github | manual);
  - `deploy_approval` (each | automatic).
- **Limits:** `max_open_prs`, `max_in_uat`, `max_review_rounds`, `max_pr_lines` (whole numbers). To size them, ask how many people run agent chats, how many chats each, and how many hours a week the owner tests in how many sittings, then run `python3 tools/haam/haam.py settings --recommend --builders N --chats N --testing-hours N --sittings N` and show what it suggests.
  - In test-first, `max_in_uat` is the real limit: it's how much you can test. `max_open_prs` guards the CI cost of ready PRs. Drafts and docs-only PRs (briefs, split specs, assessments, ADRs) never count, and `capacity --list` shows the breakdown.
  - **Batch window**, for a weekend of agent work tested in one sitting: a temporary value for a limit that ends by itself, e.g. `settings --set max_in_uat=30 --until <last day, YYYY-MM-DD> --human`, or `--until "YYYY-MM-DD HH:MM"` (local time) to end it at a set moment. It's kept on this computer (in the git folder, next to the machine lock), not in `haam.config.json`: it counts at once for every agent chat on this computer, whatever the main folder has checked out, and needs no commit or PR. `settings` lists the open windows with their end; `settings --clear-window max_in_uat --human` ends one early. Only the limits (`max_open_prs`, `max_in_uat`, `max_review_rounds`, `max_pr_lines`) take a window; any other setting is a lasting choice. Agents on another computer don't see it: open it there too if agents run there. Suggest pairing it with `/test all` and "pass all verified" for the sitting.
- **Protected areas:** `protected_paths`. Show the list. To add: `config --protected "src/auth/**" --human`. To remove: `config --unprotected "…" --human`.
- **Production code** (`DECISIONS.md` §8): `production_paths` minus `non_production_paths`. It tells agents and the owner what runs for users, and what a prototype must not reach without the gates. Change it with `config --production "src/**,…" --human`, `--not-production "…" --human` and `--remove-not-production "…" --human`.
- **Language:** `language` (`en`, `es`, `fr`, `de`, `it`, `nl`, `pt`): the language of the docs and of what agents write for people (specs, issues, UAT plans, messages). Change it with `config --language <code>`, then `python3 <kit-path>/tools/haam/haam.py update --target . --apply` with the kit at the project's version: docs nobody edited switch; edited ones stay as they are.
- **Housekeeping:** `worktree_cleanup` (after-ship | manual). After-ship never removes a worktree a program (an agent chat, a terminal) is still running in. `worktree_dir` (default `.claude/worktrees`): where agents' worktrees live; a sibling like `../connect-wt` keeps them outside the repo (`settings --set worktree_dir=../connect-wt --human`, or `config --worktree-dir … --human`). Claude Code's own `.claude/worktrees` is always cleaned too. If the project's rules once had agents use another folder, `worktree clean --also <that folder>` tidies the ones left there (`doctor` lists them). `stale_claim_days` (default 0): days with no comment on a claimed issue and no commit on its branch before an agent may release that claim and pick the work up (`issue release <n> --stale`). It's for chats that died mid-task (a session limit, a laptop asleep, a crash). 0: agents only list them for you (`issue stale`), and `/triage stale` frees them.
- **Required board fields** (GitHub Projects): `required_issue_fields` — names every new issue must get on create (e.g. Area, Kind, Code check). Set with `config --required-fields "Area,Kind,Code check" --human`. Epics use `config --required-epic-fields "…"` or, if unset, the same list without `Code check`. Empty (default): agents set a field only when the text clearly answers it.
- **Shared test resources:** `heavy_runs`. If tests use something the whole machine shares (a local database they clone, a simulator, a device), two chats running them at once break each other. List those commands as patterns: `config --heavy-run "make (check|test-integration)"` (`--clear-heavy-runs` empties the list). Agents then run them through `haam.py exclusive`, one at a time, and so does `local-ci`. A command run that way may call `exclusive` itself (a check script that takes the lock for its heavy steps): it runs straight through, inside its parent's turn. Empty (the default): nothing waits.

Point out combinations that undo each other's safety, in one line each, and let them decide:
- `ci off` with `review off`: nothing checks the code before your test;
- `ci off` without a release-time full check: Linux-only failures can reach production; keep secret scanning, the AI reviews and release-gate, and run `make check` (or the full CI workflow) on the commit you ship;
- `deploy_approval automatic` with `uat bugs-skip`: an agent's bug fix can reach production with no human looking at it;
- anything but `ci every-pr` with `review github` (or a Linear tracker, or no `HAAM_PROJECT_TOKEN` secret): the no-UAT lane stops merging by itself, and you ship those PRs (local results aren't tamper-proof; reduced checks aren't enough on their own);
- `grouping release`: one failing release check holds every change in it.

## 3. Apply
1. For each change: `python3 tools/haam/haam.py settings --set key=value --human` (repeat `--set` for several). It refuses invalid values. `--human` means the owner chose it in this session: never use it otherwise. Where it goes depends on the main folder:
   - **On a clean `main`:** it saves `haam.config.json` in the main folder (step 4 commits it).
   - **Busy** (another branch or a commit checked out, e.g. the owner's other chat is testing with `checkout-pr`, or unsaved changes besides `haam.config.json`): it leaves the main folder's files alone, makes the change in a temporary copy of `origin/main`, commits it on `chore/haam-settings-<date-time>`, pushes it and opens its PR, then removes the copy. Give the owner the PR link from the output (`settings_pr` in `--json`), and skip step 4. The change counts once that PR merges; for a limit that must count now, offer a window instead (above).
   - A temporary window (`--until`) never touches `haam.config.json`, so it works the same either way.
2. Show the summary: `python3 tools/haam/haam.py settings`.
3. On their OK, sync GitHub with `python3 tools/haam/haam.py settings --apply --human`. This needs repository admin. It sets:
   - the repository variables the workflows read;
   - the required checks (for example `ci-local` instead of `ci`, or dropping `ci` when `ci` is `off`);
   - the production approval.

   With the main folder busy, `--apply` on its own reads the settings on `origin/main`, not the open settings PR: when a change needs `--apply` (runner, review, ci, nightly, deploy_approval), run `settings --set key=value --apply --human` in one call once the owner said OK, or `--apply` after the PR merges.
4. The settings take effect for agents and the gate once `haam.config.json` is on `main`. If step 1 saved it in the main folder, commit it on a branch (`chore/haam-settings`) and open the PR (if step 1 already opened one, there's nothing to do here). `haam.config.json` is a protected file, so the human reviews and merges it: with `/test` and `ship`, or in GitHub.

## 4. Reply
List what changed, one line each, with what they'll notice. For example:
- *"PRs no longer run CI on GitHub. `/test` runs it on your computer before shipping."*
- *"Bugs now merge without your test."*

Say that `/haam-settings` changes them again any time.
