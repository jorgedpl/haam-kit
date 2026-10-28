---
name: bug
description: Report a bug or production issue as an issue in the tracker, with reproduction steps and a first root-cause hypothesis. Use when something is broken, wrong, failing or a UAT step failed.
argument-hint: "<what is wrong>"
---

# /bug: report an issue

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Problem: $ARGUMENTS

1. **Check for duplicates** in the tracker (label `stream:bug`, open statuses). If found, add a comment there with the new information and stop.
2. **Fill `docs/templates/bug.md`**: what happened, what was expected, steps to reproduce, environment (local / production), impact (who is affected, how many), first seen.
3. **Investigate briefly (≤ 15 minutes of work):** search the codebase for the likely area, read the relevant code and recent commits (`git log -p --since="2 weeks ago" -- <path>`). Write a *Root cause hypothesis* section. Do **not** fix anything yet.
4. **Suggest a priority** using `docs/process/LIFECYCLE.md` §6. If production is broken or customer data could be affected, say so clearly at the top of your reply and suggest `Urgent`.
5. **Create the issue in the tracker:** status `Triage`, label `stream:bug` (+ `human-review` if it touches a protected area from `AGENTS.md` §4), priority = your suggestion, description = filled template. Board fields (GitHub: `haam.py issue fields`): if `haam.config.json` lists `required_issue_fields`, set **every** name there with `--field NAME=VALUE` (pick the closest option; create refuses without them). Otherwise set only fields the report clearly answers; leave out any you'd have to guess.
6. **Never** include real personal data from logs or screenshots in the issue. Redact names, emails, DOBs, document numbers.
7. **Reply** with issue ID, link, suggested priority and the one-line hypothesis. If reproduction steps and root cause are solid, say: "Ready to move to `Ready`. Confirm the priority and I can `/build` it."
