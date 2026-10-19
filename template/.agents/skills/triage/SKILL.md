---
name: triage
description: Go through the tracker with the product owner — group loose issues into epics, the Triage inbox, the backlog's ranking, or stuck work — propose a grouping, priority and next step for each item, and apply only what the human confirms.
argument-hint: "[group|inbox|backlog|stale]  (default: inbox)"
disable-model-invocation: true
---

# /triage: prepare decisions, the human makes them

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Mode: $ARGUMENTS (empty = `inbox`)

This skill runs only when a human types it. You do the reading and propose; **the human decides**. Change nothing in the tracker until the human has confirmed the table in step 3. The rules you apply are in `docs/process/PRODUCT-MANAGER.md` §3–5. In group mode, "the table" is the epics table in step 2a.

## 1. Read the context
`docs/product/PRODUCT.md` (current priorities, non-negotiables, core journeys) and `docs/process/PRODUCT-MANAGER.md` §3–5 (outcomes, epics, priority levels, bug matrix).

## 2. Collect the items
- **group:** open issues that aren't in an epic and aren't epics (GitHub: `issue list --open-only --no-parent --no-label epic --json`), plus the open epics (`--label epic`). Go to step 2a.
- **inbox:** every open issue in `Triage`, plus any open issue with no priority outside Done, Parked and Canceled. GitHub: `python3 tools/haam/haam.py issue list --status Triage --open-only --json`.
- **backlog:** every issue in `Ready` and `Backlog`. Look for: priorities that no longer fit the current priorities; too many Highs (more than about one in five); items larger than M that should be split; features in Backlog with no spec; Low items older than two months (suggest Park).
- **stale:** `In Progress` with no comment or commit for 3+ days; `UAT` waiting 3+ days; `Decision` waiting 7+ days; `Parked` items whose "revisit when" seems to have come true; open `override-followup` items.

Read each item fully (description and comments). For a bug, check whether the steps to reproduce are usable. Look for duplicates among open issues. Take at most 15 items per round; say how many are left.

In **inbox** mode, if there are more than about 8 items, or several lack context or look related, suggest running `/triage group` first: triaging one feature at a time is faster than triaging fragments.

## 2a. Group mode: propose epics
Cluster the issues that belong to the same outcome: the same journey, screen, module, customer request or problem. Fit issues into an existing epic where one matches. Then show:

| # | Epic (new or existing) | Outcome in one line | Issues | Why they belong together | Confidence |
|---|---|---|---|---|---|

plus a short list of issues that stay on their own, and of likely duplicates. At most 6 epics per round. Ask: *"Reply `ok`, or tell me what to change (e.g. `merge 2 and 3`, `#40 out of 1`, `rename 4 to …`)."* Wait.

Then apply exactly what was confirmed: create each new epic (GitHub: `issue create --epic --stream idea --title "<outcome-focused title>" --body-file <short summary and member list>`, status Triage; if none of its members is an idea, i.e. only bugs and approved features, use `--stream feature --status Backlog` instead, since there's nothing to decide), link each member (`issue link <n> --parent <epic>`), and comment on each member `🧩 Grouped into epic <ID>: <title>`. Finish by listing the epics in suggested order and offering `/epic <ID>` for the first: that's where the questions about each feature get asked. Skip steps 3–4 in group mode.

## 3. Propose, as one table
| # | ID | Title | Stream | Priority | Next step | UAT | Why (≤ 12 words) |
|---|---|---|---|---|---|---|---|

- **Stream:** confirm or correct (`bug` = doesn't work as intended; `idea` = new or changed behaviour).
- **Priority:** Urgent / High / Medium / Low, using the levels and the bug matrix; say which current priority it serves, if any.
- **Next step**, one of:
  - inbox: `Ready` (bug with usable repro) · `needs info: <question>` · `assess` (idea → Discovery; for an idea inside an undecided epic, propose `decided with epic <ID>` and leave it in Triage) · `park until <trigger>` · `reject: <reason>` · `duplicate of <ID>`
  - backlog: `keep` · `priority → X` · `split` · `needs spec` · `park until <trigger>`
  - stale: `nudge` (comment asking for status) · `release the claim` · `remind the human to test/decide` · `revisit now`
- **UAT:** `test` (the default) or `skip`. Propose `skip` only for changes the owner can't meaningfully test by using the product: a kit or config update, a dependency bump, a refactor with no visible change, CI or internal tooling. With `skip` (label `uat:skip`), the agent opens the PR straight away and it merges by itself once CI and both AI reviews pass: no test, no merge by the owner. Never propose `skip` for anything in a protected area (`AGENTS.md` §4) or anything a user would notice.
- Never propose approving an idea (G1) or approving a spec (G2); those are `/decide` and the owner's "spec approved". If an idea looks obviously right, propose `assess` and say "quick assessment".

Then ask: *"Reply `ok` to apply all of this, or tell me what to change (e.g. `#14 Low, #9 park until Q3`)."* Wait for the answer.

## 4. Apply exactly what was confirmed
For each item, in the tracker:
- Set the priority and fix the stream label. For `UAT: skip`, add the label `uat:skip` (GitHub: `haam.py issue label <n> --add uat:skip --human`, allowed here because the human confirmed it).
- Status: `Ready` (bugs), `Discovery` (ideas to assess), `Parked` or `Canceled` (on GitHub these two need `--human`, allowed here because the human confirmed them; close Canceled issues as not planned or duplicate). Leave "needs info" items in `Triage`.
- Comment: `🗂️ Triaged by <user>: <priority> · <next step> · <why>`. For "needs info", comment the question and mention the reporter. For duplicates, link the original. For stale nudges, mention the assignee.
- "Release the claim": unassign, status back to `Ready` (GitHub: `issue status <n> Ready --force`, allowed here because the human confirmed it), comment why.
Anything the human didn't confirm stays exactly as it was.

## 5. Report
Counts by outcome; what is now in the **Agent queue**; anything Urgent (suggest starting an agent: new chat, `/work bugs`); what is waiting on the human (Decision, UAT, specs waiting for approval). If items are left, offer the next round.
