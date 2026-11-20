# UAT plan: <ID> <title>

- **Issue:** <#123 or APP-123> · **PR:** #NNN · **Spec:** docs/specs/<FILE-ID>-*.md
- **Estimated time:** ~N minutes

## Setup (local)
```bash
git fetch origin
git switch --detach origin/<branch-name>   # detached: works even while the agent's worktree has the branch
make setup
make dev
# when done: git switch main
```
- Open: http://localhost:XXXX
- Test account(s): <synthetic accounts / how to create them>
- Feature flag: none / <how to turn on>

## Test cases
<!-- Where: where each case can be shown. `test`: a test run, a local run or a test environment · `simulator`: a simulator or emulator · `device`: only a real phone or other device · `person`: a person's judgement (new design or wording, feel or speed, a third-party sign-in or payment). With `uat: agents-verify` an independent agent runs the `test` and `simulator` cases, and only the others come to the owner. A cell that says anything else counts as the owner's. -->
| # | AC | Steps | Expected result | Where | Pass? |
|---|---|---|---|---|---|
| 1 | AC1 | 1. … 2. … | … | <test / simulator / device / person> | [ ] |
| 2 | AC2 | | | | [ ] |
| 3 | Edge | | | | [ ] |
| 4 | Regression | Run the main journey end to end: <describe> | Works as before | | [ ] |

## Not in scope for this test
- 

## Agent pre-check
<!-- Filled by the agent: what it checked itself (tests, `make e2e`, a browser tool) and what it saw. -->
- **Fully verified by the agent:** no  <!-- "yes" only under the rules in /uat step 3; then the owner can pass it with "pass all verified" -->
- **Verified at:** <the 40-character commit your evidence is from>
- **Risk:** <low | medium | high>: <one line>
- **Undo:** <how to undo it>
- Evidence: <the commands or runs, and their results, one line per acceptance criterion>

## Results
Recorded as comments on the issue and the PR by `/test` (or `/uat-result`), so recording a result never changes the code that was tested.
