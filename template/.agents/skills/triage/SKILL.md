---
name: triage
description: Go through the tracker with the product owner — the Triage inbox, the backlog's ranking, or stuck work — propose a priority and next step for each item, and apply only what the human confirms.
argument-hint: "[inbox|backlog|stale]  (default: inbox)"
disable-model-invocation: true
---

# /triage: prepare decisions, the human makes them

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Mode: $ARGUMENTS (empty = `inbox`)

This skill runs only when a human types it. You do the reading and propose; **the human decides**. Change nothing in the tracker until the human has confirmed the table in step 3. The rules you apply are in `docs/process/PRODUCT-MANAGER.md` §3–4.

## 1. Read the context
`docs/product/PRODUCT.md` (current priorities, non-negotiables, core journeys) and `docs/process/PRODUCT-MANAGER.md` §3–4 (outcomes, priority levels, bug matrix).

## 2. Collect the items
- **inbox:** every open issue in `Triage`, plus any open issue with no priority outside Done, Parked and Canceled. GitHub: `python3 tools/haam/haam.py issue list --status Triage --open-only --json`.
- **backlog:** every issue in `Ready` and `Backlog`. Look for: priorities that no longer fit the current priorities; too many Highs (more than about one in five); items larger than M that should be split; features in Backlog with no spec; Low items older than two months (suggest Park).
- **stale:** `In Progress` with no comment or commit for 3+ days; `UAT` waiting 3+ days; `Decision` waiting 7+ days; `Parked` items whose "revisit when" seems to have come true; open `override-followup` items.

Read each item fully (description and comments). For a bug, check whether the steps to reproduce are usable. Look for duplicates among open issues. Take at most 15 items per round; say how many are left.

## 3. Propose, as one table
| # | ID | Title | Stream | Priority | Next step | Why (≤ 12 words) |
|---|---|---|---|---|---|---|

- **Stream:** confirm or correct (`bug` = doesn't work as intended; `idea` = new or changed behaviour).
- **Priority:** Urgent / High / Medium / Low, using the levels and the bug matrix; say which current priority it serves, if any.
- **Next step**, one of:
  - inbox: `Ready` (bug with usable repro) · `needs info: <question>` · `assess` (idea → Discovery) · `park until <trigger>` · `reject: <reason>` · `duplicate of <ID>`
  - backlog: `keep` · `priority → X` · `split` · `needs spec` · `park until <trigger>`
  - stale: `nudge` (comment asking for status) · `release the claim` · `remind the human to test/decide` · `revisit now`
- Never propose approving an idea (G1) or approving a spec (G2); those are `/decide` and the spec PR. If an idea looks obviously right, propose `assess` and say "quick assessment".

Then ask: *"Reply `ok` to apply all of this, or tell me what to change (e.g. `#14 Low, #9 park until Q3`)."* Wait for the answer.

## 4. Apply exactly what was confirmed
For each item, in the tracker:
- Set the priority and fix the stream label.
- Status: `Ready` (bugs), `Discovery` (ideas to assess), `Parked` or `Canceled` (on GitHub these two need `--human`, allowed here because the human confirmed them; close Canceled issues as not planned or duplicate). Leave "needs info" items in `Triage`.
- Comment: `🗂️ Triaged by <user>: <priority> · <next step> · <why>`. For "needs info", comment the question and mention the reporter. For duplicates, link the original. For stale nudges, mention the assignee.
- "Release the claim": unassign, status back to `Ready`, comment why.
Anything the human didn't confirm stays exactly as it was.

## 5. Report
Counts by outcome; what is now in the **Agent queue**; anything Urgent (suggest starting an agent: new chat, `/work bugs`); what is waiting on the human (Decision, UAT, spec PRs). If items are left, offer the next round.
