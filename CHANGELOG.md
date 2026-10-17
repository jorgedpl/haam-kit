# Changelog

All notable changes to the HAAM kit. The format follows [Keep a Changelog](https://keepachangelog.com) and the project uses [semantic versioning](https://semver.org).

Each release lists **Migration** steps when a project needs to do more than run `haam.py update`.

## [Unreleased]

## [1.3.0] - 2026-10-16

### Added
- **Product manager guide** (`docs/process/PRODUCT-MANAGER.md`), for humans: what only the product owner does, a daily, weekly and monthly rhythm, how to triage (four questions and the possible outcomes), priority levels with tests, a bug impact × reach matrix, value/confidence/size for ideas, healthy queue sizes, and how to do each step with an agent, directly in GitHub Projects or directly in Linear. With checklists.
- **`/triage [inbox|backlog|stale]` skill** (human-invoked): the agent reads the inbox, the backlog or stuck work, proposes stream, priority and next step for each item in one table, and applies only what the product owner confirms, with a comment on each item.
- GitHub Projects setup lists a **Triage** saved view; Linear setup points to Linear's Triage inbox.
- **Epics**: a parent issue labelled `epic` groups the issues of one feature (GitHub sub-issues; Linear sub-issues), with a brief in `docs/epics/` from the new `docs/templates/epic.md`. Epics are decided once at G1 (`/decide` applies to their idea sub-issues), never built themselves, and closed when their last sub-issue is released.
- **`/triage group`**: clusters loose issues into proposed epics (title, outcome, members, why) for the product owner to confirm.
- **`/epic <ID>` or `/epic "<theme>"`** (human-invoked): reads an epic's issues and the code, drafts the brief, interviews the product owner (at most five questions per round), then proposes and applies a clean-up: duplicates, gaps, rewrites, splits, order.
- `haam.py issue create --epic`, `--parent N`, `issue link N --parent E`, `issue children E` (with progress), `issue list --parent E` / `--no-parent`; `claim` refuses epics; new label `epic` on GitHub and Linear; Epics saved view.

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

[Unreleased]: https://github.com/jorgedpl/haam-kit/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/jorgedpl/haam-kit/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/jorgedpl/haam-kit/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/jorgedpl/haam-kit/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/jorgedpl/haam-kit/releases/tag/v1.0.0
