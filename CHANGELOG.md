# Changelog

All notable changes to the HAAM kit. The format follows [Keep a Changelog](https://keepachangelog.com) and the project uses [semantic versioning](https://semver.org).

Each release lists **Migration** steps when a project needs to do more than run `haam.py update`.

## [Unreleased]

## [1.5.0] - 2026-10-17

Fixes from running HAAM on a real project with several agent chats in parallel.

### Safety
- The Claude Code secret hook scans the folder the commit happens in (the agent's worktree, or the folder named by `git -C` / `cd … &&`), not always the main folder. It used to block commits over unrelated files and miss what a worktree was committing.
- New rulesets let admins bypass only when merging a pull request, never by pushing straight to `main` (agents work under a human's login, often an admin's). `github` warns if an existing ruleset still allows "always".
- `github --apply` no longer overwrites an existing ruleset: it adds only what HAAM needs (missing rules and required checks), keeps the project's own settings and shows what it will change. `--reset` restores HAAM's defaults.
- `issue status` refuses to move an issue that's In Progress for another chat, unless this chat is on the issue's branch (or the batch branch named in the claim), or the human asked (`--force`, or `--human` inside a human-only skill).
- Because the spec now ships in the code's PR, the "spec approved" comment records the approved commit, and the reviewer agent blocks any later change to the spec.
- `ship` refuses to run inside an agent's worktree: only the owner's own chat ships. `AGENTS.md` and `/work` say so.
- `/test` and `checkout-pr` no longer suggest `git stash` (all worktrees share one stash list).

### CI cost
- `ci.yml`: docs-only PRs pass in seconds; `make check` gets the changed files in `$CI_CHANGED_FILES` so a project can run only the parts a PR touches; no run after every merge to `main`, a nightly full run instead.
- `security.yml`: the dependency audit skips docs-only PRs and runs nightly on `main`.
- `review.yml` no longer starts a runner for every label added; `gates.yml` only for code pushes, the two gate labels and override comments.
- `tracker-sync.yml` no longer runs for every new issue: the board's free "Auto-add to project" workflow does that (setup step), and `issue create` adds its own.
- New rulesets don't require branches to be up to date before merging (which re-ran CI on every open PR after each merge).
- Assessments and specs are committed on the issue's own branch, without a PR, and ship with the code in one PR. Epic briefs and split specs still get a (now cheap) docs PR.
- Dependabot: monthly, grouped, at most 2 open PRs per ecosystem.
- `haam.py capacity` and new config `max_open_prs` (default 5) and `max_in_uat` (3): `/next` holds new work when either is reached. Bots' PRs (Dependabot) don't count.

### Changed
- `"deploy": "manual"` in `haam.config.json` (`config --deploy manual`): `ship` merges, then exits 3 (waiting for the human) until the owner deploys and says `live` (`ship --live`), which closes the issue.
- Batch an epic's bugs: `/next` offers them as one item, `/work epic <ID>` takes them; one branch, one PR titled `#12 #13 #14: …`, and `ship` closes them all.
- `doctor` and `github` accept `CLAUDE_CODE_OAUTH_TOKEN` for the AI review (`review.yml` passes it); the security review still needs `ANTHROPIC_API_KEY`.
- On plans that don't allow required reviewers on private repos, `github` creates the production environment without them and explains why, instead of failing with HTTP 422.
- Workflows run on `ubuntu-24.04` (not `ubuntu-latest`), and every job has a time limit.
- `/build` runs `worktree prep` first in a worktree (local files like `.env`), and `worktree prep` reports whether the git secret hook is on.

### Updater
- `install` and `update` only make the kit's own scripts executable, never the project's.
- Kit files hidden by the project's `.gitignore` (e.g. `**/build/` hiding `.agents/skills/build/`) are re-included by a small block kept at the very end of `.gitignore` (so it wins over later rules), restored if missing, and reported; `doctor` checks for them.
- `github` leaves an existing ruleset alone if it can't read it (instead of replacing it).

### Migration
- `haam.py update`. Then run `haam.py github` (plan): it shows what it would add, and warns if your ruleset lets admins bypass "always" or requires up-to-date branches. Change those in the ruleset (or `github --apply --reset`).
- GitHub Projects: turn on the board's **Auto-add to project** workflow (board → Workflows).
- If you deploy by hand: `haam.py config --deploy manual`.
- If `make check` can run parts of the project separately, have it read `$CI_CHANGED_FILES`.

## [1.4.0] - 2026-10-17

### Added
- **`/test`** (human-invoked): the product owner's one command for testing and shipping. It picks the oldest change waiting in UAT, puts it on this machine and starts the app, shows a short checklist, then:
  - **`pass`** → asks *"Ship it?"*; on **`ship`** it merges, approves the production deploy on the human's behalf, waits for it, runs the smoke check and closes the issue.
  - **what went wrong** → records it on the issue, labels it `uat-failed`, sends it back to Ready, and (in Claude Code) starts a worker on the fix straight away. Agents take `uat-failed` items first; the fix comes back to `/test`.
- `haam.py checkout-pr ISSUE` / `--back`: put an issue's PR on this machine to test (detached, so agents' worktrees aren't disturbed; refuses over unsaved work).
- `haam.py ship ISSUE --human`: merge exactly the commit the human tested once every check (including `release-gate`) is green, approve the waiting `production` deploy, wait, close the issue, and say when it was the last issue in its epic. Exit code 2 means "not finished, run again"; it stops (exit 1) on failing checks, merge conflicts, a changed PR or a failed deploy. `--merged-only` (used by `/release`) never merges. Docs-only changes skip the deploy wait.
- `docs/changes/<FILE-ID>.md`: one release note per change, added by `/uat`, so parallel PRs never conflict.
- New issue label `uat-failed` (GitHub and Linear).

### Changed
- `/uat` adds the release note on the PR branch, so it ships with the change; `/release` now only finishes changes merged some other way (`ship --merged-only`).
- Test results are recorded as comments on the issue and the PR, not commits, so recording a result never changes what was tested. The UAT plan's Results table is gone.
- `/uat-result fail` sends the issue back to Ready with `uat-failed` (it used to go to In Progress, assigned); `/next` takes `uat-failed` items first; `/build` reworks them on the same branch and PR and runs `/uat` again.
- `AGENTS.md`: agents may merge and approve the deploy only through `ship --human`, inside `/test`, after the human said `pass` and `ship` (`/release` uses `--merged-only`, which never merges).
- The product manager guide has a new §2a, "Testing a change: the whole loop".

### Migration
- `haam.py update`, then add the `uat-failed` label: GitHub Projects `haam.py github-project --apply`; Linear `haam.py linear --apply` (in your terminal). From now on, test with `/test`.

## [1.3.0] - 2026-10-16

### Added
- **Product manager guide** (`docs/process/PRODUCT-MANAGER.md`), for humans: what only the product owner does, a daily, weekly and monthly rhythm, how to triage (four questions and the possible outcomes), priority levels with tests, a bug impact × reach matrix, value/confidence/size for ideas, healthy queue sizes, and how to do each step with an agent, directly in GitHub Projects or directly in Linear. With checklists.
- **`/triage [inbox|backlog|stale]` skill** (human-invoked): the agent reads the inbox, the backlog or stuck work, proposes stream, priority and next step for each item in one table, and applies only what the product owner confirms, with a comment on each item.
- GitHub Projects setup lists a **Triage** saved view; Linear setup points to Linear's Triage inbox.
- **Epics**: a parent issue labelled `epic` groups the issues of one feature (GitHub sub-issues; Linear sub-issues), with a brief in `docs/epics/` from the new `docs/templates/epic.md`. Epics are decided once at G1 (`/decide` applies to their idea sub-issues), never built themselves, and closed when their last sub-issue is released.
- **`/triage group`**: clusters loose issues into proposed epics (title, outcome, members, why) for the product owner to confirm.
- **`/epic <ID>` or `/epic "<theme>"`** (human-invoked): reads an epic's issues and the code, drafts the brief, interviews the product owner (at most five questions per round), then proposes and applies a clean-up: duplicates, gaps, rewrites, splits, order.
- `haam.py issue create --epic`, `--parent N`, `issue link N --parent E`, `issue unlink N`, `issue edit N --title/--body-file`, `issue children E` (with progress, including sub-issues not on the board), `issue list --parent E` / `--no-parent`; `claim` refuses epics; new label `epic` on GitHub and Linear; Epics saved view.

### Changed
- On GitHub Projects, moving an issue to Canceled also closes it as not planned.
- `/next` picks ideas triaged for assessment (Discovery, unassigned) before untriaged ones.
- `/assess` and `/spec` branch from `origin/main` (works in worktrees); the claim message suggests the same.
- Lifecycle, onboarding and adoption docs point to the guide and `/triage`.

### Migration
- `haam.py update`, then re-run the tracker setup to add the `epic` label: GitHub Projects `haam.py github-project --apply`; Linear `haam.py linear --apply` (in your terminal). On GitHub Projects, add the **Triage** (`status:Triage`) and **Epics** (`label:epic`) views to the board.

## [1.2.0] - 2026-10-16

### Added
- **`/work` skill**: the one command to type in a new agent chat window. It gives the chat its own git worktree, copies local files like `.env`, then runs `/next` in just-pick mode and works the item through to the hand-over. `/work bugs`, `/work features` and `/work ideas` restrict it to one stream.
- **`haam.py worktree status|new|prep|list|clean`**: one worktree per agent chat under `.claude/worktrees/` (the same place Claude Code uses). `new` and `prep` copy the git-ignored files listed in `.worktreeinclude`, never tracked files, never overwriting. `clean` removes only worktrees whose PR is merged or closed (or that were never used) and that have nothing unsaved; it shows the plan first.
- `.worktreeinclude` (lists `.env` and `.env.local` to start with).
- `/haam-setup` Phase 8, "Prepare for parallel chats": list the local files, keep test runners out of `.claude/worktrees/`, try a fresh worktree.
- `doctor` has a "Parallel chats" section; the Claude Code session hook says whether the chat is in its own worktree.

### Changed
- `AGENTS.md` §7: one chat, one folder. Agent chats that change files work in their own worktree whenever other chats may be open; the main folder is the human's.
- `/build` branches from `origin/main` (works inside a worktree); `/next` checks the workspace first.
- UAT plans check the branch out detached (`git switch --detach origin/<branch>`), so the human can test while the agent's worktree still has it.
- Onboarding, agent setup, lifecycle and adoption docs explain how to open agent chats in each tool.

### Migration
- `haam.py update` brings everything in. Then, once: check `.worktreeinclude` lists the local files your app needs, and exclude `.claude/worktrees/` from any tool that scans the whole project folder (test runner, linter, file watcher). `/haam-setup` Phase 8 walks you through it.

## [1.1.0] - 2026-10-16

### Added
- **GitHub Projects as a tracker**, alongside Linear. Choose per project with `haam.py config --tracker github|linear`.
  - `haam.py github-project [--apply]`: creates the board, links the repository, sets the 12 HAAM statuses and a Priority field, creates the issue labels, and lists the browser-only steps (saved views).
  - `haam.py issue list|create|view|add|claim|status|priority|label|comment|close`: one command set any agent can use to work the board. `claim` refuses already-claimed or non-Ready issues; human-only moves (Done, Parked, Canceled, Decision→Backlog, `agent-ready`) require `--human`.
  - `tracker-sync.yml` workflow: moves linked issues to In Review when a PR opens and to Deploying when it merges, and puts new issues on the board. Needs the `HAAM_PROJECT_TOKEN` secret; does nothing on Linear projects.
  - GitHub issue forms for ideas and bugs.
  - `invite` shares the board; `dev` and `doctor` check the board and the `project` scope.
- `docs/process/TRACKER.md`: how every tracker operation works on GitHub Projects and on Linear.
- Claim comments can name the machine (`--machine`), for one person working from several computers.

### Changed
- Rules, skills, process docs, templates, the PR template and the reviewer instructions are tracker-neutral. Skills write `<ID>` (`#123` on GitHub Projects, `APP-123` on Linear).
- On GitHub Projects, PRs link issues with `Refs #123` (not `Closes`), so the issue stays open until `/release`.
- The session hook recognises both branch styles (`123-title` and `app-123-title`).

### Migration
- **Existing projects keep Linear**: `"tracker"` defaults to `linear`, so `haam.py update` is all you need.
- **To move to GitHub Projects**: `gh auth refresh -s project`, then `haam.py config --tracker github`, `haam.py github-project --apply`, add the `HAAM_PROJECT_TOKEN` secret, create the board views, and ask your agent to copy open issues across.

## [1.0.0] - 2026-10-16

First public release.

### Added
- Human-Agent Agile Methodology: lifecycle with three work streams (ideas, features, bugs) and five gates (decide, ready, verified, accepted, released), with recorded overrides.
- Shared rules (`AGENTS.md`) and 14 skills in the Agent Skills format: `idea`, `bug`, `assess`, `decide`, `spec`, `next`, `build`, `uat`, `uat-result`, `override`, `release`, `haam-setup`, `haam-onboard`, `haam-update`.
- Support for Claude Code, Cursor, Codex, Grok Build, Gemini CLI and GitHub Copilot.
- Code review layers: commit secret hook (gitleaks), CI secret scan and dependency audit, independent AI spec/quality review and Claude security review, human review for protected areas, human UAT.
- GitHub workflows: `ci`, `security`, `review`, `gates` (UAT label gate), `deploy` (approval-gated).
- Setup tool `haam.py`: `install`, `update`, `config`, `agents`, `github`, `linear`, `invite`, `dev`, `doctor`, `version`, with version tracking in `haam.lock.json`.
- Docs: methodology, gates, adoption guide, per-agent setup, GitHub and Linear setup, developer onboarding, templates (idea, bug, assessment, spec, UAT plan, ADR).

[Unreleased]: https://github.com/jorgedpl/haam-kit/compare/v1.5.0...HEAD
[1.5.0]: https://github.com/jorgedpl/haam-kit/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/jorgedpl/haam-kit/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/jorgedpl/haam-kit/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/jorgedpl/haam-kit/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/jorgedpl/haam-kit/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/jorgedpl/haam-kit/releases/tag/v1.0.0
