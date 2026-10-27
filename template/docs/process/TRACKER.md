# The tracker: Linear or GitHub Projects

HAAM works the same with either tracker. `haam.config.json` → `"tracker"` says which one this project uses:

- **`github`**: issues in this GitHub repository, on a GitHub Projects board. Free on every GitHub plan. Agents use `python3 tools/haam/haam.py issue …` (below), which works from any agent tool.
- **`linear`**: issues in a Linear team. Agents use the Linear connection (MCP).

Skills say "in the tracker"; this page says how to do each operation in each tracker. **Agents: check `tracker` in `haam.config.json` once per session, then use the matching column.**

## Concepts

| Concept | GitHub Projects | Linear |
|---|---|---|
| Issue ID (write it like this) | `#123` | `APP-123` |
| Branch name | `123-short-title` | `app-123-short-title` (Linear's branch name) |
| Commit message | `#123: Add bulk invite` | `APP-123: Add bulk invite` |
| PR title | `#123: Add bulk invite` | `APP-123: Add bulk invite` |
| Link PR → issue | **`Refs #123`** in the PR description (not `Closes`: the issue closes at `/release`, after deploy) | Issue ID in the PR title |
| Files for the issue | `docs/specs/GH-123-slug.md` (same for assessments, UAT) | `docs/specs/APP-123-slug.md` |
| 12 statuses | Board's **Status** field | Team workflow statuses |
| Priority | Board's **Priority** field (Urgent/High/Medium/Low) | Built-in priority |
| Streams, `agent-ready`, `human-only`, `override-followup`, `epic`, `uat-failed`, `claimed`, `mode:prototype`, `mode:epic-build`, `spike-ready` | Issue labels | Issue labels |
| Epic (groups the issues of one feature) | Issue labelled `epic`; its issues are GitHub **sub-issues** | Issue labelled `epic`; its issues are **sub-issues** (parent set) |
| Who is working on it | Status In Progress (building) or label `claimed` (assessing, writing a spec, building a prototype), plus the claim comment. The assignee alone can't tell two chats of the same person apart | Same |
| Status moves on PR open/merge | `tracker-sync.yml` workflow: issues being delivered only (not epics, not docs-only PRs or spikes) | Linear's GitHub integration |

## Operations

Commands in the GitHub column run from the repository root. Add `--json` for machine-readable output.

| Operation | GitHub Projects | Linear (via MCP) |
|---|---|---|
| **Find work** (queues for `/next`) | `haam.py issue list --status Ready --unassigned --open-only` (add `--label agent-ready` for features, `--label stream:bug` for bugs) | List team issues by status, label, assignee |
| **Read an issue** | `haam.py issue view 123` | Get issue |
| **Create an idea** | `haam.py issue create --stream idea --title "…" --body-file idea.md` (lands in Triage) | Create issue, status Triage, label `stream:idea` |
| **Report a bug** | `haam.py issue create --stream bug --title "…" --body-file bug.md --priority High` | Create issue, status Triage, label `stream:bug` |
| **Create an epic** | `haam.py issue create --epic --stream idea --title "…"` | Create issue with label `epic` |
| **Put an issue in an epic** | `haam.py issue link 14 --parent 9` | Set the issue's parent to the epic |
| **Create an issue inside an epic** (e.g. spec slices, gaps) | `haam.py issue create --stream feature --parent 9 --title "…"` | Create sub-issue of the epic |
| **The board's own fields** (Area, Team, Estimate, Sprint…) | `haam.py issue fields` lists them and their options. Set them with `--field NAME=VALUE` on `issue create` or `issue edit` (repeatable; an empty value clears one; `Sprint=@current` is the iteration running today), and filter with `issue list --field Area=Billing`. A wrong name or value is refused before anything changes | The team's own fields, with the Linear connection |
| **Take an issue out of an epic** | `haam.py issue unlink 14` | Clear the issue's parent |
| **Rewrite an issue** (title, description) | `haam.py issue edit 14 --title "…" --body-file new.md` | Update issue |
| **An epic's issues** | `haam.py issue children 9` (with progress) | List the epic's sub-issues |
| **Issues not in any epic** | `haam.py issue list --open-only --no-parent --no-label epic` | List issues without a parent |
| **Claim** (before building, assessing or writing a spec) | `haam.py issue claim 123 --tool "Claude Code" --machine laptop` (build: refuses if already claimed or not Ready; `--force` for bugs being fixed straight from Triage only when the human said so). Assessing: add `--for assess`; writing a spec: `--for spec`. It prints a claim id: keep it | Re-fetch; if In Progress, labelled `claimed` or assigned to someone else, stop; else assign to you, set In Progress (build) or add label `claimed` (assess, spec), comment with a claim id, re-read the comments (AGENTS.md §6) |
| **Build a prototype** (`/spike`) | `haam.py issue claim 123 --for spike` (ideas in Triage to Decision, Backlog features), then when pushed: `issue label 123 --add spike-ready` and `issue release 123 --claim <id> --status Decision` (a Backlog feature: no `--status`) | Claim as above (label `claimed`, a claim comment saying "to build a prototype"), label `spike-ready`, release |
| **Production code in a change** | `haam.py production` (the files a branch changes that run for users) | Same |
| **Release a claim** (assessment or spec pushed; or the chat stops) | `haam.py issue release 123 --claim <id> [--status Decision]` (`--human` instead of the id only in `/triage stale` or `/test`) | Unassign, remove `claimed`, set the status, comment `🔓 Claim released` |
| **Change status** | `haam.py issue status 123 "UAT"` | Update issue status |
| **Human-only status** (Done, Parked, Canceled, Decision→Backlog) | Same, plus `--human`, **only** inside `/triage`, `/epic`, `/decide`, `/test`, `/release` or `/override` typed by a human | Same rule |
| **Priority** | `haam.py issue priority 123 High` | Update priority |
| **Labels** | `haam.py issue label 123 --add stream:feature --remove stream:idea` (`agent-ready` also needs `--human`, after the human approved the spec) | Update labels |
| **Comment** | `haam.py issue comment 123 --body "…"` or `--body-file` | Create comment |
| **Reject or duplicate** (in `/triage`, `/epic` or `/decide`) | `haam.py issue status 123 Canceled --human` (also closes the issue as not planned); comment the reason or the original's ID | Status Canceled, comment |
| **Test a change** (human, in `/test`) | `haam.py checkout-pr 123`, then `haam.py checkout-pr --back` | Same (the code is in GitHub either way) |
| **Open the PR after a pass** (test-first, human said `pass`) | `haam.py publish 123 --human`: pushes the tested commit, opens the PR labelled `uat-passed`, moves the issue to In Review | `haam.py publish APP-123 --human` (`--label human-review` if the issue has it), then move the issue to In Review and comment, as it prints |
| **Record a failed test** (human said it failed) | `haam.py test-failed 123 --human`, then label `uat-failed`, status Ready, no assignee | `haam.py test-failed APP-123 --human`, then the same in Linear |
| **Ship after a pass** (human said `ship`) | `haam.py ship 123 --human`: merge, approve deploy, wait, close | `haam.py ship APP-123 --human`, then set Done in Linear |
| **Ship everything ready, one deploy** | `haam.py ship --all --human` (or `ship 12 13 14 --human`): merges each, approves the newest deploy only, closes all | `haam.py ship APP-12 APP-13 --human` (list them: `--all` can't read Linear) |
| **See or change how HAAM runs** (owner) | `/haam-settings`; `haam.py settings [--explain]`, `settings --set key=value --human`, `settings --apply --human` (the owner's choice only) | Same |
| **Run CI here** (setting `ci: local`) | `haam.py local-ci 123` (ship runs it for you) | Same |
| **No UAT for this issue** (owner's decision) | `haam.py issue label 123 --add uat:skip --human` | Label `uat:skip` |
| **Room for new work?** (`/next` checks first) | `haam.py capacity` (the UAT queue and ready PRs vs `max_in_uat`, `max_open_prs`, or a batch window's raise; drafts and docs-only PRs don't count) | Same command, with `--in-uat <count>` |
| **Will new work collide with what's waiting?** | `haam.py overlap --files src/auth/,src/api/users.py` (branches in UAT that change the same files) | Same, with `--branch <name>` for each branch in UAT |
| **Batch PR** (an epic's bugs) | Title `#12 #13 #14: …`, a `Refs #n` line per issue; `ship` closes them all | Title `APP-12 APP-13: …` |
| **Close after release** | `haam.py issue close 123 --human` (sets Done and closes; `/release` only) | Status Done |

## Rules that apply to both

- Every piece of work has an issue in the tracker; nothing is tracked anywhere else.
- If the tracker can't be reached, stop and tell the human.
- The claim protocol is what stops two agent chats (or two machines) building, assessing or specifying the same thing. Never skip it.
- Human-only moves happen only inside the human-only skills, and the tool asks for `--human` on GitHub as a reminder. Agents act under the owner's own login, so GitHub can't tell who set an owner's label (`uat:skip`, `mode:prototype`, `mode:epic-build`): that's a rule, checked by the tool on GitHub Projects and by nothing on Linear. An agent that broke it with plain `gh` could, with `uat:skip`, let a change outside the protected areas skip your test; CI and both AI reviews still run, and deploys still wait for you where your plan allows.

## GitHub Projects setup (admin, once)

1. `gh auth refresh -s project` (lets your GitHub login use Projects).
2. `python3 tools/haam/haam.py config --tracker github`
3. `python3 tools/haam/haam.py github-project` (plan), then `--apply`: creates the board named after the product, links the repo, sets the 12 statuses and the Priority field, creates the labels.
4. **Automation token** (for `tracker-sync.yml`, and auto-merge in the no-UAT lane): create a classic token at github.com/settings/tokens with the `project` and `repo` scopes (`public_repo` is enough for a public repository), then `gh secret set HAAM_PROJECT_TOKEN -R owner/repo`. Without it everything works, but cards don't move by themselves when PRs open or merge, and the no-UAT lane can't turn on auto-merge (the gate uses this token, because a merge by the workflow's own token wouldn't start the deploy). On Linear projects the lane never auto-merges, so the token isn't needed for it.
5. **In the browser**, on the board: create the saved views the setup lists (Board grouped by Status, Triage, Agent queue, Waiting on me, Ideas inbox, Bugs, Epics), and turn on the board's built-in **Auto-add to project** workflow for this repository (board → Workflows). It puts issues created on GitHub's website on the board for free; `haam.py issue create` adds its own. **Turn off** the built-in **Item closed → Status: Done** workflow: it overwrites `Canceled` after `issue status … Canceled` closes the issue, and `ship` already sets Done itself.
6. Each developer runs `gh auth refresh -s project` once; `/haam-onboard` checks it.

## Switching tracker later

Set `"tracker"` with `haam.py config --tracker …`, run the new tracker's setup, then ask your agent to copy open issues across (it can read one tracker and write the other). Keep the old tracker read-only for history.
