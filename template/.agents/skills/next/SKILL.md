---
name: next
description: Pick the next most valuable unclaimed work item from the three streams (bugs, ready features, ideas needing assessment/spec) and start it. Use when asked "what's next", "pick something up", "work on the backlog" or when running unattended.
argument-hint: "[bugs|features|ideas]  (optional: restrict to one stream)"
---

# /next: pull the next work item

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Filter: $ARGUMENTS (empty = all streams)

## 0. Your own workspace
If the item you pick will change files (build, spec, assessment), you need your own worktree when other agent chats may be open on this machine (`AGENTS.md` §7). Run `python3 tools/haam/haam.py worktree status`. In the main folder: Claude Code, move into a new worktree first (as in `/work` step 1); other tools, ask the human whether other chats are running and, if so, follow `/work` step 1.

## 1. Build the queue (unassigned or assigned to the current user, not In Progress)

GitHub Projects: `python3 tools/haam/haam.py issue list --status Ready --unassigned --open-only` (and `--status Backlog`, `--status Triage` for steps 4–5). Linear: list the team's issues.

Take the first match, in this order:

0. **Rework**: status `Ready` with label `uat-failed` (the human tested it and found problems): always first.
1. **Bugs**: label `stream:bug`, status `Ready`, priority Urgent or High.
2. **Features**: status `Ready`, label `agent-ready`, by priority (Urgent → Low), then oldest first.
3. **Bugs**: label `stream:bug`, status `Ready`, priority Medium or Low.
4. **Specs to write**: status `Backlog`, label `stream:feature`, has a priority, no spec yet → run `/spec`.
5. **Ideas to assess**: label `stream:idea`, status `Discovery` and unassigned (triaged for assessment, by priority), then status `Triage` → run `/assess`. Epics (label `epic`) that are still ideas are assessed here as a whole. Skip ideas that belong to an epic still being decided: they are decided with their epic.

**Epics:** never build or spec an epic itself (steps 1–4 skip label `epic`); build and spec its sub-issues. Also skip any issue with label `human-only`, any with no priority (except ideas in step 5), and any whose `blocked by` relations are not Done.

## 2. Confirm or go
- **If a human is present**, show the top 3 candidates (ID, title, priority, stream, size if known) and recommend one. Wait for a choice.
- **If running unattended** (scheduled task, or the user said "just pick"), take the top one and say which and why in the first line of your output.

## 3. Execute
Run the matching skill: `/build` for Ready items, `/spec` for Backlog features, `/assess` for ideas, following that skill's steps exactly (including the claim protocol).

## 4. Nothing to do?
Report: count of items waiting on a human (status `Decision`, `UAT`, spec PRs open), and stop. Never invent work, and never start items that aren't through their gate.
