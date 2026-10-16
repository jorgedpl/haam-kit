# Changelog

All notable changes to the HAAM kit. The format follows [Keep a Changelog](https://keepachangelog.com) and the project uses [semantic versioning](https://semver.org).

Each release lists **Migration** steps when a project needs to do more than run `haam.py update`.

## [Unreleased]

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

[Unreleased]: https://github.com/jorgedpl/haam-kit/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/jorgedpl/haam-kit/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/jorgedpl/haam-kit/releases/tag/v1.0.0
