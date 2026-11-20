---
name: uat
description: Prepare a user acceptance test cycle for a built issue — a step-by-step local test plan for the human — and move it to UAT (prepares Gate G4). Use when the change is built: test-first, once its branch is pushed with `make check` green (no PR yet); checks-first, once the PR's checks are green.
argument-hint: "<ID>"
---

# /uat: prepare user acceptance testing

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Target: $ARGUMENTS

1. **Check preconditions.** Test-first (`"flow"` in `haam.config.json`, the default): the branch is pushed, `make check` passed on it, and there's no PR yet (or, for rework, the PR is back in draft). Checks-first: the PR exists, isn't a draft, and `gh pr checks` shows `ci`, `secrets`, `dependencies`, `ai-review` and `security-review` green (or the AI reviews overruled by a human). If not, stop and say what's missing.
2. **Write `docs/uat/<FILE-ID>-<slug>.md`** from `docs/templates/uat-plan.md`, on the issue's branch (the PR's branch, if there is one):
   - *Setup:* exact commands to run it locally (`git fetch origin && git switch --detach origin/<branch> && make setup && make dev`: detached, so it works even while an agent's worktree has the branch; `git switch main` afterwards), URL to open, any seed/test accounts (synthetic only), feature flags.
   - *Test cases:* one per acceptance criterion, plus key edge cases and one "nothing else broke" regression check of the main journey. Each has numbered steps, expected result, and a `[ ]` checkbox. Write for someone who did not read the code.
   - *Out of scope:* what not to test.
   - *Results* table left empty for the human.
3. **Agent pre-check:** if a browser tool or `make e2e` is available, run through the plan yourself first and note anything that failed. Fix it before handing over. Record what you checked under *Agent pre-check*.
   **Fully verified by the agent: yes** (so the owner can pass it with one reply in `/test all`) only when all of these hold; otherwise leave it at `no`:
   - every acceptance criterion is proven by a test or a run you made, written under *Evidence*, one line each;
   - nothing in it needs a person's eyes, hands or judgement: no layout or visual change, nothing on a phone or other device, no feel or speed, no third-party sign-in or payment flow, no wording that isn't exactly what the spec says;
   - typically: changes to tests only, text that must match the spec word for word, logic fully covered by tests, internal tooling;
   - never for a protected area (label `human-review`, `AGENTS.md` §4), and never for rework after a failed test (`uat-failed`): the owner found problems there, so they test it again themselves.

   **With the setting `uat: agents-verify`** (`python3 tools/haam/haam.py settings`), the plan decides case by case who checks the change, so also fill in:
   - the **`Where`** column of every test case, with one of four words (a short note may follow, as in `device (a chip read)`):
     - `test`: a test run, a local run (`make dev`, a browser tool) or a test environment can show it;
     - `simulator`: a simulator or emulator can show it;
     - `device`: only a real phone or other device can (a chip or NFC read, a camera on a real document, biometrics on a real face, two devices, a store or attested build);
     - `person`: a person's judgement (new or changed layout or wording that the spec doesn't fix word for word, feel or speed, a third-party sign-in or payment).
     An independent agent runs every `test` and `simulator` case; only the `device` and `person` cases go to the owner. Write `test` or `simulator` only where you ran the case that way yourself: a cell that says anything else, or nothing, counts as the owner's. A protected area alone changes nothing here: the owner's own areas are `owner_test_paths`, the tool checks those, and there the approval stays the owner's after the verifier ran every case it could;
   - `Verified at: <the 40-character commit your evidence is from>`. It may differ from the head you hand over only in `docs/uat/` and `docs/changes/`;
   - `Risk: low|medium|high: <one line>`;
   - `Undo: <how>` (revert the commit, turn off a flag, …).
   `python3 tools/haam/haam.py lane <number>` shows the lane, the cases on each side and the reason before you hand over.
4. **Release note:** create `docs/changes/<FILE-ID>.md` with one line a user would understand (`- <ID>: <what changed for them>`). One file per change, so parallel PRs never conflict.
   **Rework after a failed test** (label `uat-failed`): keep the existing plan, update only what changed, and add a regression case for each reported failure; don't add a second release note.
5. Usually `/build` already wrote the plan and the release note, so there's nothing to commit here. If they're missing: commit `<ID>: UAT plan` and push. Test-first that's free (no PR yet); checks-first it re-runs CI and the reviews, so avoid it there.
6. **Tracker:** status `UAT`; comment with the branch name written as ``branch `<branch>` `` (so `/test` finds a batch's branch from any of its issues), a link to the plan and a 3–5 line "how to test in 5 minutes" summary, starting with `✔ Fully verified by the agent` when the plan says so. Mention the product owner so they get notified.
   **Rework after a failed test** (label `uat-failed`): the label comes off now, since the issue is no longer waiting for an agent, and the comment starts with `🔁 Rework, round <N>` instead, where N is the number of `❌ UAT failed` comments on the issue (1 after the first failure). GitHub Projects: `haam.py issue status <n> UAT` removes the label and prints the round to use. Linear: remove `uat-failed` and count the `❌ UAT failed` comments yourself with the Linear connection.
   **With the setting `uat: agents-verify`** (GitHub Projects), hand over with one command instead: write the 3–5 line summary to a file outside the repository, then `python3 tools/haam/haam.py handover <number> --body-file <summary>` (add `--claim <id>` when you aren't on the branch). It runs the lane rule on what's pushed:
   - lane `agents` (an agent can show every case): status `In Review`, label `verifying`, and the comment ``🧪 Ready for verification · branch `<branch>` · head <sha>``. It refuses until the plan has the three lines of step 3. An independent verifier takes it (`/verify`); the owner isn't asked. Rework after `verify-failed` is handed over the same way, and goes back to a verifier;
   - lane `agents, then owner` (some cases need a real device or a person, or the change is in one of the owner's own areas): the same hand-over, and the comment says which cases the verifier runs and what is left for the owner. After the verifier's run the ticket is `partly-verified` and moves to `UAT` for the owner's part only;
   - lane `owner` (pulled back, rework after the owner's failed test, a kept prototype, or no case an agent can show): status `UAT` and ``🧪 Ready for UAT · your test: <reason> · branch `<branch>` · head <sha>``, mentioning the owner, as today.
7. **Reply** to the user: what to test in one line, and "When you're ready: `/test <ID>`. I'll set it up, and you just tell me `pass` or what went wrong."
   Lane `agents`: "Handed to a verifier (`/work verify` in a new chat, or `/next`). It goes with your next `ship`; say `test <ID> myself` to test it yourself."
   Lane `agents, then owner`: "Handed to a verifier (`/work verify` in a new chat, or `/next`). Afterwards only <the cases, or your approval> is yours: `/test <ID>`."
