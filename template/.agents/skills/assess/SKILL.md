---
name: assess
description: Assess an idea in the tracker for value, effort, risk and technical feasibility, optionally with a throwaway spike, and prepare it for a human decision (Gate G1). Use for issues in Triage or Discovery.
argument-hint: "<ID> [--spike]"
---

# /assess: evaluate an idea

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Target: $ARGUMENTS

1. **Load the issue** from the tracker. It should be `stream:idea` in `Triage` or `Discovery`. If not, tell the user and stop. Set status to `Discovery` and comment `🔎 Assessment started`.
2. **Read context:** `docs/product/PRODUCT.md` (priorities, non-negotiables), `docs/product/ARCHITECTURE.md`, related issues and specs in `docs/specs/`.
3. **Investigate the codebase** to ground effort and feasibility in reality: which modules change, what data model changes, which external services are involved, which protected areas (`AGENTS.md` §4) are touched.
4. **Spike (only if `--spike` is passed, or if a key unknown can't be resolved by reading):**
   - Branch `spike/<branch-name>` from `origin/main`.
   - Time-box it: prove or disprove the single riskiest assumption. Quick and dirty is fine.
   - Record findings, then push the branch. **Never open a PR to merge a spike.**
5. **Write the assessment** at `docs/assessments/<FILE-ID>-<slug>.md` using `docs/templates/assessment.md`. Be honest: "unknown" beats invented numbers. Always include at least two options plus "do nothing", and a recommendation (approve / park / reject + suggested priority).
6. **Commit and PR the assessment:** branch `docs/<issue-id>-assessment` from `origin/main` (`git fetch origin && git switch -c docs/<issue-id>-assessment origin/main`), commit `<ID>: assessment`, open a PR (docs-only).
7. **Update the tracker:** link the PR and spike branch, post a summary comment (recommendation, size, top risk, 3 lines max), set status `Decision`.
8. **Reply to the user** with the summary and: "Decide with `/decide <ID> approve|park|reject`."
