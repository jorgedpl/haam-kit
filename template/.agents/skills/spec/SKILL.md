---
name: spec
description: Write a build-ready feature specification for an approved Linear issue so any agent can implement it (prepares Gate G2, Definition of Ready). Use for issues in Backlog, or bugs that need a clearer fix plan.
argument-hint: "APP-123"
---

# /spec: make an issue ready to build

Target: $ARGUMENTS

1. **Load the issue** and its assessment (`docs/assessments/`) and any linked ADRs. It should be `stream:feature` in `Backlog` (or a bug needing a fix plan).
2. **Read the code** the change will touch. Specs grounded in real file paths and functions are the point.
3. **Write `docs/specs/<ISSUE-ID>-<slug>.md`** from `docs/templates/feature-spec.md`:
   - User stories and **acceptance criteria as Given / When / Then**. Each must be testable by a unit or integration test.
   - Explicit **out of scope**.
   - Files/modules likely touched; data, migration and config impact.
   - Unit test plan (one or more tests per criterion) and a UAT outline (what a human will click through).
   - Rollout and rollback notes.
4. **Size check.** If it's more than ~1 day of agent work or ~400 changed lines, split it: create Linear sub-issues (each `stream:feature`, status `Backlog`), each with its own section in the spec, ordered so each slice is shippable on its own.
5. **Protected areas:** if any are touched (`AGENTS.md` §4), add label `human-review` to the issue(s) and flag it at the top of the spec.
6. **Self-check against the Definition of Ready** in `docs/process/GATES.md` (G2). List anything unmet.
7. **Open a docs PR** (branch `docs/<issue-id>-spec`, commit `APP-123: spec`). Link it in Linear with a comment: `📝 Spec ready for review: <PR link>`.
8. **Ask open questions** as a single numbered list in Linear and in chat. Don't fill gaps on verification logic, data handling or money by guessing.
9. **Reply:** "Spec ready for your review. When you approve it, merge the docs PR (or tell me 'spec approved') and I'll add `agent-ready` and move it to `Ready`."

**When the human says the spec is approved:** add label `agent-ready` and set status `Ready` for the issue and any sub-issues. This is the only time an agent applies `agent-ready`, and only on explicit human approval in this conversation or in a Linear comment from a human.
