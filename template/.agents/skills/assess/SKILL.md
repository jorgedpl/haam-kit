---
name: assess
description: Assess an idea in the tracker for value, effort, risk and technical feasibility, optionally with a throwaway spike, and prepare it for a human decision (Gate G1). Use for issues in Triage or Discovery.
argument-hint: "<ID> [--spike]"
---

# /assess: evaluate an idea

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Target: $ARGUMENTS

1. **Load the issue** from the tracker. It should be `stream:idea` in `Triage` or `Discovery`. If not, tell the user and stop. If it belongs to an epic that is still an idea, stop and suggest assessing the epic instead (`/assess <epic>`): the pieces are decided together. Set status to `Discovery` and comment `🔎 Assessment started`.
2. **Epics:** if the issue is an epic, assess the feature as a whole: read its brief in `docs/epics/` (or, if the brief's PR isn't merged yet, from that PR's branch) and every sub-issue; size is the sum of the slices; risks cover all of them.
3. **Read context:** `docs/product/PRODUCT.md` (priorities, non-negotiables), `docs/product/ARCHITECTURE.md`, related issues and specs in `docs/specs/`.
4. **Investigate the codebase** to ground effort and feasibility in reality: which modules change, what data model changes, which external services are involved, which protected areas (`AGENTS.md` §4) are touched.
5. **Spike (only if `--spike` is passed, or if a key unknown can't be resolved by reading):**
   - Branch `spike/<branch-name>` from `origin/main`.
   - Time-box it: prove or disprove the single riskiest assumption. Quick and dirty is fine.
   - Record findings, then push the branch. **Never open a PR to merge a spike.**
6. **Write the assessment** at `docs/assessments/<FILE-ID>-<slug>.md` using `docs/templates/assessment.md`. Be honest: "unknown" beats invented numbers. Always include at least two options plus "do nothing", and a recommendation (approve / park / reject + suggested priority).
7. **Commit the assessment on the issue's own branch, without a PR** (every PR costs CI minutes and review time): `git fetch origin && git switch -c <branch name for this issue> origin/main` (`123-short-title` on GitHub, Linear's branch name on Linear), commit `<ID>: assessment`, `git push -u origin <branch>`. If the idea is approved, the spec and the code continue on this branch and the assessment ships with them. Then free the branch: `git switch --detach origin/main` (a branch can be checked out in only one worktree at a time). (An epic's assessment is the exception: open a docs PR so its sub-issues can read it from `main`.)
8. **Update the tracker:** link the assessment file on the branch (`https://github.com/<repo>/blob/<branch>/docs/assessments/<file>`) and the spike branch, post a summary comment (recommendation, size, top risk, 3 lines max), set status `Decision`.
9. **Reply to the user** with the summary and: "Decide with `/decide <ID> approve|park|reject`."
