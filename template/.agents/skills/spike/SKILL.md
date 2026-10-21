---
name: spike
description: Build a throwaway working prototype of an idea or a Backlog feature, fast and freely, on a spike branch, so the owner can try it before deciding or before the spec is written. Use when the human asks for a prototype or a spike, or the issue has the label mode:prototype.
argument-hint: "<ID> [time box, e.g. 3h]"
---

# /spike: build it to find out

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Target: $ARGUMENTS

A spike is the one place where you build freely: no spec, no PR, no size limit, no full test suite. What keeps it safe:
- a spike branch never merges (the release gate refuses `spike/` branches);
- anything that touches production code reaches users only through `/spec` and the normal gates.

So build fast, and be honest about what you built.

1. **Load the issue.** It should be a `stream:idea` (Triage, Discovery or Decision) or a `stream:feature` in Backlog without an approved spec. An epic: prototype the whole feature only if the owner asked for that. **Claim it:** GitHub Projects: `python3 tools/haam/haam.py issue claim <number> --for spike --tool "<your tool>" --machine "<this computer>"` (keep the claim id it prints). Linear: as `docs/process/TRACKER.md` → **Claim** says. If it's already claimed, stop and pick another.
2. **Your own workspace** (`AGENTS.md` §7; `/work` step 1 sets one up). Then `git fetch origin`. If the issue already has a spike branch (a `🧪` comment names it, or the owner asked for changes), continue on it: `git switch spike/<…>`. Otherwise start one: `git switch -c spike/<branch name for this issue> origin/main` (for example `spike/123-voice-notes`; Linear: `spike/<Linear's branch name>`).
3. **Time box:** the one the human gave, or until the main question is answered, at most about a working day of agent time. Say it in your first line.
4. **Build it,** aiming for something the owner can use end to end, with the least code that shows the idea:
   - New code that can stand alone (a page, a script, a small service) goes in `prototypes/<slug>/`. That folder is never production code.
   - If the idea can only be tried by changing production code, change it on this branch. That's fine on a spike, but keep track: `python3 tools/haam/haam.py production --base origin/main` lists the production files you changed.
   - Skip what doesn't help the owner judge it: polish, edge cases, a full test suite.
   - Never change protected areas (`AGENTS.md` §4: CI workflows, `Makefile`, scripts, the agent setup…), and never add a workflow: the owner runs your branch on their computer, and GitHub runs workflows on branch pushes.
   - Test or sandbox accounts and keys only. If trying the idea needs real credentials or a production service, stop and ask the owner.
   - Still never: secrets or real personal data (synthetic fixtures only, `AGENTS.md` §3), and anything against production systems or data.
   - Commit as you go: `<ID>: spike: <what>`.
5. **Write the notes** in `prototypes/<slug>/README.md` (or `docs/spikes/<FILE-ID>-<slug>.md` when there's no prototype folder):
   - **The problem and who it's for,** in a line or two (from the issue).
   - **What it does,** in two or three lines.
   - **How to try it:** the exact commands (e.g. `make dev` on this branch and the URL to open, or `python3 prototypes/<slug>/run.py`) and any synthetic test account.
   - **What you learned:** what worked, what was hard, what surprised you.
   - **Production code changed:** the list from step 4, or "none".
   - **Doing it properly:** rough size, risks, protected areas it would touch (`AGENTS.md` §4), and at least one other way to do it.
   - **Your recommendation:** discard it, rebuild it properly, or keep the code, and why. For an idea, also approve, park or reject.
6. **Push it:** `git push -u origin spike/<…>`. Never open a PR. Then free the branch: `git switch --detach origin/main`.
7. **Tracker:**
   - comment ``🧪 Spike ready to try · branch `spike/<…>` ``, then the 3–5 line summary, how to try it and your recommendation;
   - add label `spike-ready` (GitHub: `haam.py issue label <n> --add spike-ready`);
   - release your claim. An idea moves to `Decision`, because the owner now has what they need to decide (GitHub: `haam.py issue release <n> --claim <id> --status Decision`). A Backlog feature stays where it is (`--claim <id>` alone).

   If you stop before finishing, push what you have, release the claim and say what's missing.
8. **Reply:** *"Ready to try: `/test <ID>`. Then tell me: discard, change (what to change), rebuild it properly, or keep the code."*
