# Spec: <ID> <title>

- **Issue:** <#123 or APP-123> · **Assessment:** docs/assessments/<FILE-ID>-*.md · **ADRs:** <links or none>
- **Status:** Draft / Approved · **Approved by:** <human> on YYYY-MM-DD
- **Protected areas:** none / <list> → `human-review`

## 1. Goal
<!-- One paragraph: what changes for whom, and why. -->

## 2. User stories
- As a <role>, I want <capability>, so that <benefit>.

## 3. Acceptance criteria
<!-- Each criterion must be testable. Number them; tests and UAT steps refer to these numbers. -->
**AC1:** <name>
- Given …
- When …
- Then …

**AC2:** …

## 4. Out of scope
- 

## 5. Design notes
- **Files / modules likely touched:** 
- **Data model / migrations:** none / <describe, incl. backfill and reversibility>
- **Config / env vars:** none / <names, and add to .env.example>
- **External APIs:** 
- **UI notes / copy:** 
- **Error states and edge cases:** 

## 6. Test plan
| AC | Unit / integration test(s) | Notes |
|---|---|---|
| AC1 | `test_…` | |

**UAT outline:** <what a human will click through locally>

## 7. Rollout and rollback
- **Feature flag:** none / <name>
- **Rollout:** 
- **Rollback:** <revert PR is enough? data to clean up?>

## 8. Slices (if split)
| Sub-issue | Scope | Depends on |
|---|---|---|

## 9. Open questions
1. 
