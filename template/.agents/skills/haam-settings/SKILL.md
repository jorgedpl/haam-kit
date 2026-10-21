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
1. `python3 tools/haam/haam.py settings --explain --json`: every setting with its current value, default, options and trade-off.
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
- **Limits:** `max_open_prs`, `max_in_uat`, `max_review_rounds`, `max_pr_lines` (whole numbers).
  - In test-first, `max_in_uat` is the real limit: it's how much you can test. `max_open_prs` guards the CI cost of ready PRs. Drafts and docs-only PRs (briefs, split specs, assessments, ADRs) never count, and `capacity --list` shows the breakdown.
  - **Batch window**, for a weekend of agent work tested in one sitting: a temporary raise that ends by itself after its last day, e.g. `settings --set max_in_uat=30 --until 2026-10-27 --human` (or `config --max-in-uat 30 --until … --human`). `config --end-batch-window --human` ends it early. It counts at once for every agent chat on this computer. Suggest pairing it with `/test all` and "pass all verified" for the sitting.
- **Protected areas:** `protected_paths`. Show the list. To add: `config --protected "src/auth/**" --human`. To remove: `config --unprotected "…" --human`.
- **Housekeeping:** `worktree_cleanup` (after-ship | manual). After-ship never removes a worktree a program (an agent chat, a terminal) is still running in.
- **Shared test resources:** `heavy_runs`. If tests use something the whole machine shares (a local database they clone, a simulator, a device), two chats running them at once break each other. List those commands as patterns: `config --heavy-run "make (check|test-integration)"` (`--clear-heavy-runs` empties the list). Agents then run them through `haam.py exclusive`, one at a time, and so does `local-ci`. Empty (the default): nothing waits.

Point out combinations that undo each other's safety, in one line each, and let them decide:
- `ci off` with `review off`: nothing checks the code before your test;
- `deploy_approval automatic` with `uat bugs-skip`: an agent's bug fix can reach production with no human looking at it;
- anything but `ci every-pr` with `review github`: the no-UAT lane stops merging by itself, and you ship those PRs (local results aren't tamper-proof; reduced checks aren't enough on their own);
- `grouping release`: one failing release check holds every change in it.

## 3. Apply
1. For each change: `python3 tools/haam/haam.py settings --set key=value --human` (repeat `--set` for several). It saves `haam.config.json` and refuses invalid values. `--human` means the owner chose it in this session: never use it otherwise.
2. Show the summary: `python3 tools/haam/haam.py settings`.
3. On their OK, sync GitHub with `python3 tools/haam/haam.py settings --apply --human`. This needs repository admin. It sets:
   - the repository variables the workflows read;
   - the required checks (for example `ci-local` instead of `ci`);
   - the production approval.
4. The settings take effect for agents and the gate once `haam.config.json` is on `main`. Commit it on a branch (`chore/haam-settings`) and open the PR. `haam.config.json` is a protected file, so the human reviews and merges it: with `/test` and `ship`, or in GitHub.

## 4. Reply
List what changed, one line each, with what they'll notice. For example:
- *"PRs no longer run CI on GitHub. `/test` runs it on your computer before shipping."*
- *"Bugs now merge without your test."*

Say that `/haam-settings` changes them again any time.
