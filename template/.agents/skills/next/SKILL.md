---
name: next
description: Pick the next most valuable unclaimed work item from the three streams (bugs, ready features, ideas needing assessment/spec) and start it. Use when asked "what's next", "pick something up", "work on the backlog" or when running unattended.
argument-hint: "[bugs|features|specs|ideas]  (optional: restrict to one kind of work)"
---

# /next: pull the next work item

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Filter: $ARGUMENTS (empty = all streams)

What each filter takes, from the queue in step 1: `bugs` → items 0–1 and 3 (bugs only) · `features` → items 0 and 2 (features only), then 4 · `specs` → item 4 only (specs to write) · `ideas` → item 5 only (ideas and epics to assess).

## 0. Room for new work?
Run `python3 tools/haam/haam.py capacity` (Linear: first count the issues in `UAT` with the Linear connection and add `--in-uat <count>`). If it says **hold** (too many open PRs, or too many changes waiting for the owner to test; limits in `haam.config.json`; it lists what it counted), only take rework (label `uat-failed`), finish a PR that's already open, or write specs and assessments (items 4–5 in step 1): those open no PR and add nothing to the owner's test queue, so a hold never stops them. If there's none of that, report the hold and stop: more PRs now would only cost CI minutes and wait.

## 0b. Your own workspace
If the item you pick will change files (build, spec, assessment), you need your own worktree when other agent chats may be open on this machine (`AGENTS.md` §7). Run `python3 tools/haam/haam.py worktree status`. In the main folder: Claude Code, move into a new worktree first (as in `/work` step 1); other tools, ask the human whether other chats are running and, if so, follow `/work` step 1.

## 1. Build the queue (unassigned or assigned to the current user, not In Progress)

GitHub Projects: `python3 tools/haam/haam.py issue list --status Ready --unassigned --open-only` (and `--status Backlog --no-label claimed`, `--status Discovery --unassigned --no-label claimed`, `--status Triage --no-label claimed` for steps 4–5). Linear: list the team's issues.

Take the first match, in this order. **Batch an epic's items** (always when the setting `grouping` is `per-epic`; otherwise when it helps): when two or more Ready items of the same epic share a priority (bugs, and small features (XS/S) with approved specs), offer them as one item (one branch, one PR; see `/build`). One PR instead of several means one CI run and one review instead of several, and the human tests them together.

0. **Rework**: status `Ready` with label `uat-failed` (the human tested it and found problems): always first.
1. **Bugs**: label `stream:bug`, status `Ready`, priority Urgent or High.
2. **Features**: status `Ready`, label `agent-ready`, by priority (Urgent → Low), then oldest first.
3. **Bugs**: label `stream:bug`, status `Ready`, priority Medium or Low.
4. **Specs to write**: status `Backlog`, label `stream:feature`, has a priority, not `claimed`, and no spec yet: no `docs/specs/<FILE-ID>-*.md` on `main` or on the issue's branch, and no `📝 Spec ready for review` comment (that one waits for the owner's approval, not for an agent) → run `/spec`.
5. **Ideas to assess**: label `stream:idea`, status `Discovery`, unassigned and not `claimed` (triaged for assessment, by priority), then status `Triage` → run `/assess`. Epics (label `epic`) that are still ideas are assessed here as a whole, but only once the owner has shaped them: skip an epic with no brief yet (no `docs/epics/<FILE-ID>-*.md` on `main` and none in an open docs PR); it waits for the owner's `/epic`. Skip ideas that belong to an epic still being decided: they are decided with their epic.

**Avoid collisions** (when two or more branches are waiting in `UAT`): before you take a Ready item to build, read its spec's *Files/modules likely touched* and run `python3 tools/haam/haam.py overlap --files <those paths, comma-separated; folders end in />` (Linear: add `--branch <name>` for each branch in UAT). Branches waiting together that change the same files end in merge conflicts after the first one merges, and the conflicted one needs a fresh test. So if it overlaps, prefer the next candidate of the same priority that doesn't. If every candidate overlaps, take the top one anyway, and say in the claim comment and later in the UAT comment `changes the same files as <ID>: test and ship after it`.

**Epics:** never build or spec an epic itself (steps 1–4 skip label `epic`); build and spec its sub-issues. Also skip any issue with label `human-only`, any with no priority (except ideas in step 5), and any whose `blocked by` relations are not Done.

## 2. Confirm or go
- **If a human is present**, show the top 3 candidates (ID, title, priority, stream, size if known) and recommend one. Wait for a choice.
- **If running unattended** (scheduled task, or the user said "just pick"), take the top one and say which and why in the first line of your output.

## 3. Execute
Run the matching skill: `/build` for Ready items, `/spec` for Backlog features, `/assess` for ideas, following that skill's steps exactly (including the claim protocol).

## 4. Nothing to do?
Report: count of items waiting on a human (status `Decision`, `UAT`, specs waiting for approval, epics waiting for `/epic` because they have no brief), and stop. Never invent work, and never start items that aren't through their gate.
