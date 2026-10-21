---
name: epic
description: Shape an epic with the product owner — gather the issues that make up one feature, write a short epic brief, interview the human with focused questions, then tidy the issues (duplicates, gaps, slices, order). Use on an existing epic, or with a theme to find related issues and propose a new epic.
argument-hint: "<epic ID> | \"<theme, e.g. reporting>\""
disable-model-invocation: true
---

# /epic: turn a pile of related issues into one well-understood feature

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Target: $ARGUMENTS

An **epic** is a parent issue (label `epic`) whose sub-issues together deliver one outcome. It holds the context the individual issues lack. Agents never build an epic itself; they build its sub-issues. This skill runs only when a human types it: you research and ask, the human answers and decides. Nothing changes in the tracker until the human confirms (step 5).

## 1. Find the epic and its issues
- **An epic ID:** load it and its sub-issues (GitHub: `python3 tools/haam/haam.py issue children <n>`).
- **A theme in quotes:** search open issues for ones that belong to it (titles, descriptions, comments, the screens, journeys or modules they mention). Show the candidates with a one-line reason each and ask the human which belong. On their OK, create the epic (GitHub: `issue create --epic --stream idea --title "<outcome-focused title>"`, status Triage; if none of the issues is an idea, use `--stream feature --status Backlog`) and link each confirmed issue (`issue link <n> --parent <epic>`).
- **Nothing:** list open epics without a brief in `docs/epics/` and ask which one to shape.

## 2. Read everything first
The epic and every sub-issue in full (descriptions and comments), `docs/product/PRODUCT.md` (current priorities, non-negotiables, core journeys), `docs/product/ARCHITECTURE.md`, any existing brief in `docs/epics/`, related specs and assessments, and enough of the code the issues point at to know what exists today. Don't ask the human anything this reading answers.

## 3. Draft the brief
Write `docs/epics/<FILE-ID>-<slug>.md` from `docs/templates/epic.md`. Summarise each issue in one line; mark duplicates, overlaps and unclear ones; list the gaps (what's still missing to reach the outcome) and the risks; propose slices that each ship on their own, in order. Write "unknown" where you don't know. Never invent evidence or business facts.

## 4. Interview the human
Ask the open questions, **at most 5 per round**, most important first. Make each quick to answer: offer 2–4 options plus "something else" (use your tool's multiple-choice question feature if it has one). Ask about what only the human knows:
- who exactly it's for, and what success looks like;
- must-have versus nice-to-have; what's out of scope;
- constraints: deadline, customer commitments, compliance, budget;
- existing behaviour that must not change;
- how it ranks against the current priorities.
Record every answer in the brief's *Questions and answers* (with the date) and update the other sections. Repeat until nothing blocking is left, the human says stop, or after three rounds (leave the rest marked "open").

## 5. Propose the clean-up, as one table
| # | Change | Issue(s) | Why |
|---|---|---|---|

Possible changes: close a duplicate (link the original), merge two issues (move the content into one, close the other as a duplicate), rewrite an unclear issue's title or description (add the context and a line `Part of epic <ID>: <outcome>`), split one that is bigger than M, create a missing issue (a gap), move an issue out of the epic, set order (a `Blocked by <ID>` line in the description), suggest a priority for the epic and its issues. Then ask: *"Reply `ok` to apply, or tell me what to change."* Wait.

## 6. Apply what was confirmed
- Tracker: create, link, rewrite, comment, set priorities exactly as confirmed. GitHub: new issues `issue create … --parent <epic>`; rewrites `issue edit <n> --title "…" --body-file <file>`; moving out `issue unlink <n>`. Closing duplicates is a Canceled move: on GitHub add `--human` (allowed here because the human confirmed it). Comment on each changed issue: `🧩 Epic <ID>: <what changed and why>`.
- Git: commit the brief on a docs branch from `origin/main` (`docs/<issue-id>-epic`), open a docs PR, and link it on the epic with a comment.

## 7. Next step
Tell the human where the epic stands and what comes next:
- First, the human merges the brief's docs PR, so other agents (who branch from `main`) can read it.
- **Not decided yet** (stream `idea`): `/assess <epic>` adds effort and feasibility for the whole, then `/decide <epic> approve|park|reject`. Approving the epic approves its idea sub-issues too.
- **Approved** (stream `feature`): the sub-issues without a spec get one (`/spec <ID>`, or agents via `/work specs`), in the order of the slices table.
- Bugs inside the epic keep their own path and can be fixed at any time.
