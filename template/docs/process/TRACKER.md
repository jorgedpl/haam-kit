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
| Streams, `agent-ready`, `human-only`, `override-followup`, `epic`, `uat-failed` | Issue labels | Issue labels |
| Epic (groups the issues of one feature) | Issue labelled `epic`; its issues are GitHub **sub-issues** | Issue labelled `epic`; its issues are **sub-issues** (parent set) |
| Who is working on it | Issue assignee | Issue assignee |
| Status moves on PR open/merge | `tracker-sync.yml` workflow | Linear's GitHub integration |

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
| **Take an issue out of an epic** | `haam.py issue unlink 14` | Clear the issue's parent |
| **Rewrite an issue** (title, description) | `haam.py issue edit 14 --title "…" --body-file new.md` | Update issue |
| **An epic's issues** | `haam.py issue children 9` (with progress) | List the epic's sub-issues |
| **Issues not in any epic** | `haam.py issue list --open-only --no-parent --no-label epic` | List issues without a parent |
| **Claim** (before any code) | `haam.py issue claim 123 --tool "Claude Code" --machine laptop` (refuses if already claimed or not Ready; `--force` for bugs being fixed straight from Triage only when the human said so) | Re-fetch; if In Progress or assigned to someone else, stop; else assign to you, set In Progress, comment |
| **Change status** | `haam.py issue status 123 "UAT"` | Update issue status |
| **Human-only status** (Done, Parked, Canceled, Decision→Backlog) | Same, plus `--human`, **only** inside `/triage`, `/epic`, `/decide`, `/test`, `/release` or `/override` typed by a human | Same rule |
| **Priority** | `haam.py issue priority 123 High` | Update priority |
| **Labels** | `haam.py issue label 123 --add stream:feature --remove stream:idea` (`agent-ready` also needs `--human`, after the human approved the spec) | Update labels |
| **Comment** | `haam.py issue comment 123 --body "…"` or `--body-file` | Create comment |
| **Reject or duplicate** (in `/triage`, `/epic` or `/decide`) | `haam.py issue status 123 Canceled --human` (also closes the issue as not planned); comment the reason or the original's ID | Status Canceled, comment |
| **Test a change** (human, in `/test`) | `haam.py checkout-pr 123`, then `haam.py checkout-pr --back` | Same (the code is in GitHub either way) |
| **Ship after a pass** (human said `ship`) | `haam.py ship 123 --human`: merge, approve deploy, wait, close | `haam.py ship APP-123 --human`, then set Done in Linear |
| **Close after release** | `haam.py issue close 123 --human` (sets Done and closes; `/release` only) | Status Done |

## Rules that apply to both

- Every piece of work has an issue in the tracker; nothing is tracked anywhere else.
- If the tracker can't be reached, stop and tell the human.
- The claim protocol is what stops two agents (or two machines) building the same thing. Never skip it.
- Human-only moves happen only inside the human-only skills, and the tool asks for `--human` on GitHub as a reminder.

## GitHub Projects setup (admin, once)

1. `gh auth refresh -s project` (lets your GitHub login use Projects).
2. `python3 tools/haam/haam.py config --tracker github`
3. `python3 tools/haam/haam.py github-project` (plan), then `--apply`: creates the board named after the product, links the repo, sets the 12 statuses and the Priority field, creates the labels.
4. **Automation token** (for `tracker-sync.yml`): create a classic token at github.com/settings/tokens with the `project` scope (plus `repo` if the repository is private), then `gh secret set HAAM_PROJECT_TOKEN -R owner/repo`. Without it everything works, but cards don't move by themselves when PRs open or merge.
5. **In the browser**, on the board: create the saved views the setup lists (Board grouped by Status, Agent queue, Waiting on me, Ideas inbox, Bugs).
6. Each developer runs `gh auth refresh -s project` once; `/haam-onboard` checks it.

## Switching tracker later

Set `"tracker"` with `haam.py config --tracker …`, run the new tracker's setup, then ask your agent to copy open issues across (it can read one tracker and write the other). Keep the old tracker read-only for history.
