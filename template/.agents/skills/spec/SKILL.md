---
name: spec
description: Write a build-ready feature specification for an approved issue so any agent can implement it (prepares Gate G2, Definition of Ready). Use for issues in Backlog, or bugs that need a clearer fix plan.
argument-hint: "<ID>"
---

# /spec: make an issue ready to build

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Target: $ARGUMENTS

1. **Load the issue** and its assessment (`docs/assessments/`) and any linked ADRs. It should be `stream:feature` in `Backlog` (or a bug needing a fix plan).
2. **Epic context:** if the issue belongs to an epic, read the epic and its brief (`docs/epics/`) first and keep the spec consistent with its scope and slices. If the issue *is* an epic, don't spec it as one piece: make sure each sub-issue has its own spec (run this skill on each, in the brief's order).
3. **Read the code** the change will touch. Specs grounded in real file paths and functions are the point.
4. **Write `docs/specs/<FILE-ID>-<slug>.md`** from `docs/templates/feature-spec.md`:
   - User stories and **acceptance criteria as Given / When / Then**. Each must be testable by a unit or integration test.
   - Explicit **out of scope**.
   - Files/modules likely touched; data, migration and config impact.
   - Unit test plan (one or more tests per criterion) and a UAT outline (what a human will click through).
   - Rollout and rollback notes.
5. **Size check.** If it's more than ~1 day of agent work or ~400 changed lines, split it: make the issue an epic (label `epic`) and create its slices as sub-issues (each `stream:feature`, status `Backlog`; GitHub: `issue create --stream feature --parent <n>`), each with its own section in the spec, ordered so each slice is shippable on its own.
6. **Protected areas:** if any are touched (`AGENTS.md` §4), add label `human-review` to the issue(s) and flag it at the top of the spec.
7. **Self-check against the Definition of Ready** in `docs/process/GATES.md` (G2). List anything unmet.
8. **Commit the spec on the issue's own branch, without a PR**: the branch from the assessment if there is one (`git fetch origin && git switch <branch>`), otherwise a new one from `origin/main`. Commit `<ID>: spec`, push, and comment on the issue: `📝 Spec ready for review: <link to the file on the branch>`. It ships with the code, in the same PR. (If you split it into an epic's sub-issues, open a docs PR instead, so every slice can read the spec from `main`.)
9. **Ask open questions** as a single numbered list on the issue and in chat. Don't fill gaps on verification logic, data handling or money by guessing.
10. **Reply:** "Spec ready for your review: <link>. When you're happy, tell me 'spec approved' (or comment it on the issue) and I'll add `agent-ready` and move it to `Ready`."

**When the human says the spec is approved:** add label `agent-ready` and set status `Ready` for the issue, or, if you split it into an epic, for its sub-issues only (the epic itself stays in `Backlog` and never gets `agent-ready`) (GitHub Projects: `haam.py issue label <n> --add agent-ready --human` then `haam.py issue status <n> Ready`). This is the only time an agent applies `agent-ready`, and only on explicit human approval in this conversation or in a Linear comment from a human.
