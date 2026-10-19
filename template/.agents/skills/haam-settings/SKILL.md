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
- **Protected areas:** `protected_paths`. Show the list. To add: `config --protected "src/auth/**"`. To remove: `config --unprotected "…"`.
- **Housekeeping:** `worktree_cleanup` (after-ship | manual).

Point out combinations that undo each other's safety, in one line each, and let them decide:
- `ci off` with `review off`: nothing checks the code before your test;
- `deploy_approval automatic` with `uat bugs-skip`: an agent's bug fix can reach production with no human looking at it;
- `review local` or `ci local`: those results aren't tamper-proof, so the no-UAT lane stops merging by itself;
- `grouping release`: one failing release check holds every change in it.

## 3. Apply
1. For each change: `python3 tools/haam/haam.py settings --set key=value` (repeat `--set` for several). It saves `haam.config.json` and refuses invalid values.
2. Show the summary: `python3 tools/haam/haam.py settings`.
3. On their OK, sync GitHub with `python3 tools/haam/haam.py settings --apply`. This needs repository admin. It sets:
   - the repository variables the workflows read;
   - the required checks (for example `ci-local` instead of `ci`);
   - the production approval.
4. The settings take effect for agents and the gate once `haam.config.json` is on `main`. Commit it on a branch (`chore/haam-settings`) and open the PR. `haam.config.json` is a protected file, so the human reviews and merges it: with `/test` and `ship`, or in GitHub.

## 4. Reply
List what changed, one line each, with what they'll notice. For example:
- *"PRs no longer run CI on GitHub. `/test` runs it on your computer before shipping."*
- *"Bugs now merge without your test."*

Say that `/haam-settings` changes them again any time.
