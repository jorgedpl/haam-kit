# Linear setup (one-time, ~30 minutes, workspace admin)

> **Only if your tracker is Linear** (`"tracker": "linear"` in `haam.config.json`). Using GitHub Projects? Run `python3 tools/haam/haam.py github-project` instead and see `docs/process/TRACKER.md`.

This configures Linear to match `docs/process/LIFECYCLE.md`. Do it once; every developer and agent then uses the same structure.

> **Automated:** sections 1–4 are done by `python3 tools/haam/haam.py linear --apply`, run by you in your own terminal (it asks for your Linear personal API key securely and never stores it). This page is the manual equivalent, plus sections 5–9 which only exist in Linear's web app.

## 1. Team
- Create (or reuse) a team named after your product, with a short identifier (the examples use **`APP`**).
  `python3 tools/haam/haam.py config --team-key KEY` replaces `APP` in every HAAM file.
- Invite each human contributor with their own Linear account. Agents act as the human running them, so no separate agent seats are needed.

## 2. Workflow statuses
Team settings → **Workflow**. Create these, in this order, in the category shown:

| Status | Category | Notes |
|---|---|---|
| Triage | Triage | Turn on Triage for the team |
| Discovery | Backlog | |
| Decision | Backlog | |
| Backlog | Backlog | Mark as the default for new non-triage issues |
| Ready | Unstarted | |
| In Progress | Started | |
| In Review | Started | |
| UAT | Started | |
| Deploying | Started | |
| Done | Completed | |
| Parked | Canceled | |
| Canceled | Canceled | |

Delete or rename Linear's defaults (`Todo`, `Duplicate`, etc.) so only these remain. Names must match exactly; skills refer to them by name.

## 3. Labels
Team settings → **Labels**. Create these labels (flat labels, no group needed):
- `stream:idea`
- `stream:feature`
- `stream:bug`

And these standalone labels:

| Label | Meaning | Who applies it |
|---|---|---|
| `agent-ready` | Passed G2; agents may build it | Agent, only after human approves spec |
| `human-review` | Touches a protected area; human code review required | Agent or human |
| `human-only` | Agents must not pick this up | Human |
| `override-followup` | Created after a gate override | `/override` |

Optional: area labels (`area:onboarding`, `area:billing`, `area:checkout`…) to filter the board.

## 4. Priorities
Use Linear's built-in priority (Urgent / High / Medium / Low / No priority). No custom fields needed.

## 5. Issue templates
Team settings → **Templates** → create three issue templates, pasting the body from:
- **Idea**: `docs/templates/idea.md` · default label `stream:idea` · status Triage
- **Bug**: `docs/templates/bug.md` · default label `stream:bug` · status Triage
- **Feature**: a short body linking to the spec · default label `stream:feature` · status Backlog

Agents fill these themselves via `/idea` and `/bug`; the templates are for humans creating issues in the Linear app.

## 6. GitHub integration
Settings → **Integrations → GitHub** → connect the organisation/repo.

Then in team settings → **Workflow → Pull request automations** (wording may vary slightly):

| GitHub event | Move issue to |
|---|---|
| Branch created / draft PR opened | In Progress |
| PR opened | In Review |
| PR ready for merge | *(no change, agents move it to UAT)* |
| PR merged | Deploying |

**Branch name format:** `{issue-identifier}-{issue-title}` (lower-case), e.g. `app-123-bulk-invite-users`. Remove the username prefix so branches are the same whoever creates them.

Turn on **"link PRs by issue ID in title"** so `APP-123: ...` PR titles link automatically.

## 7. Views (saved filters)
Create these team views so humans see what needs them:

| View | Filter |
|---|---|
| **Triage** | Linear's built-in Triage inbox (the product owner's daily inbox; see `docs/process/PRODUCT-MANAGER.md` §7) |
| **Waiting on me** | Status in (Decision, UAT), plus Backlog issues with a `📝 Spec ready for review` comment |
| **Agent queue** | Status = Ready, label `agent-ready` or `stream:bug`, unassigned |
| **Ideas inbox** | Status in (Triage, Discovery), label `stream:idea` |
| **Bugs** | Label `stream:bug`, not Done/Canceled, sorted by priority |
| **Overrides to close** | Label `override-followup`, not Done |

## 8. Notifications
Each human: Settings → Notifications → make sure you're notified on **mentions** and **issues assigned to you**. `/uat` mentions the product owner when something is ready to test.

## 9. Connect each person's agent tool to Linear
Each person signs in once from their own tool (Claude Code, Cursor, Codex, Grok, Gemini, Copilot). Steps per tool: `docs/setup/AGENTS-SETUP.md`.
Test: ask the agent *"list my open Linear issues in team APP"*.

If you also use a chat app (Claude, ChatGPT…) with a Linear connector, connect it too so you can capture ideas from your phone.
