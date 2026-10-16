---
name: uat
description: Prepare a user acceptance test cycle for a built issue — a step-by-step local test plan for the human — and move it to UAT (prepares Gate G4). Use when a PR's CI is green.
argument-hint: "<ID>"
---

# /uat: prepare user acceptance testing

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Target: $ARGUMENTS

1. **Check preconditions:** the PR for this issue exists, is not a draft, and `gh pr checks` shows `ci`, `secrets`, `dependencies`, `ai-review` and `security-review` green (or the AI reviews overruled by a human). If not, stop and say what's missing.
2. **Write `docs/uat/<FILE-ID>-<slug>.md`** from `docs/templates/uat-plan.md`, on the **same PR branch**:
   - *Setup:* exact commands to run it locally (`git fetch && git switch <branch> && make setup && make dev`), URL to open, any seed/test accounts (synthetic only), feature flags.
   - *Test cases:* one per acceptance criterion, plus key edge cases and one "nothing else broke" regression check of the main journey. Each has numbered steps, expected result, and a `[ ]` checkbox. Write for someone who did not read the code.
   - *Out of scope:* what not to test.
   - *Results* table left empty for the human.
3. **Optional automation assist:** if a browser tool or `make e2e` is available, run through the plan yourself first and note anything that failed. Fix it before handing over. This does **not** replace the human test.
4. Commit `<ID>: UAT plan`, push.
5. **Tracker:** status `UAT`; comment with a link to the plan and a 3–5 line "how to test in 5 minutes" summary. Mention the product owner so they get notified.
6. **Reply** to the user: what to test, the commands, and "When done: `/uat-result <ID> pass` or `/uat-result <ID> fail <what went wrong>`."
