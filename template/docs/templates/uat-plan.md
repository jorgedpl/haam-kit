# UAT plan: <ID> <title>

- **Issue:** <#123 or APP-123> · **PR:** #NNN · **Spec:** docs/specs/<FILE-ID>-*.md
- **Estimated time:** ~N minutes

## Setup (local)
```bash
git fetch origin
git switch <branch-name>
make setup
make dev
```
- Open: http://localhost:XXXX
- Test account(s): <synthetic accounts / how to create them>
- Feature flag: none / <how to turn on>

## Test cases
| # | AC | Steps | Expected result | Pass? |
|---|---|---|---|---|
| 1 | AC1 | 1. … 2. … | … | [ ] |
| 2 | AC2 | | | [ ] |
| 3 | Edge | | | [ ] |
| 4 | Regression | Run the main journey end to end: <describe> | Works as before | [ ] |

## Not in scope for this test
- 

## Agent pre-check
<!-- Filled by the agent if it ran the plan with a browser tool or `make e2e` first. -->

## Results
| Date | Tester | Outcome | Notes |
|---|---|---|---|
| | | | |
