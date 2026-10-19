# Changelog

All notable changes to the HAAM kit. The format follows [Keep a Changelog](https://keepachangelog.com) and the project uses [semantic versioning](https://semver.org).

Each release lists **Migration** steps when a project needs to do more than run `haam.py update`.

## [Unreleased]

## [1.9.0] - 2026-10-19

The product owner decides how HAAM runs.

### Added
- **`/haam-settings`** (human-only). It walks the owner through every setting: what it does, each option's trade-off, a recommendation based on the project's own numbers (Actions minutes, the UAT queue), and combinations that undo each other's safety. It applies what they choose and syncs GitHub.
- **`haam.py settings`**: `[--explain]` shows the settings, `--set key=value` changes one (validated, saved in `haam.config.json`), and `--apply` syncs GitHub: repository variables, required checks, production approval.
  - Changing settings needs `--human` and refuses in an agent's worktree, as `ship` does: they're the owner's choice. `AGENTS.md` says so.
  - `ci-settings` still works and maps onto it. An existing own runner (set up before 1.9.0) is adopted, label included.
- New settings, defaults first:
  - **`ci`**:
    - `every-pr`;
    - `local`: `make check` (and `make audit`) on the owner's computer on a clean copy of the PR's commit, posted as `ci-local`, which becomes the required check. `ship` runs it automatically. New `haam.py local-ci`.
    - `off`: the secret scan still runs on every PR.
  - **`nightly`**: `on` | `off` (the full check and dependency audit on main).
  - **`review`**: `github` | `local` | `protected-only` (only PRs changing protected areas get the AI reviews, decided from the files and the base branch's `protected_paths`) | `off`.
  - **`uat`**: `owner-decides` (the `uat:skip` lane) | `always` (no lane) | `bugs-skip` (`/triage` marks bugs `uat:skip` by default; the gate still only trusts the owner's mark, and protected areas never take the lane).
  - **`grouping`**:
    - `per-issue`;
    - `per-epic`: agents always batch an epic's items;
    - `release`: no PR per change. `publish` records the owner's pass. `ship --all` (or `ship <IDs>`) merges every passed change into one fresh branch from main and opens one release PR. Each change's tested commit is listed in the release PR; changes that conflict or moved after their test are left out with a reason. The checks and AI reviews run once, then it merges, deploys once, closes every issue and deletes the merged branches.
  - **`deploy_approval`**: `each` | `automatic` (deploys start on merge: the production environment has no required reviewer).
  - **`runner`**: `github` | `self-hosted` (now stored in the config too).
  - **`worktree_cleanup`**: `after-ship` (each ship tidies agents' worktrees that are merged or abandoned with nothing unsaved) | `manual`.
  - Limits: **`max_review_rounds`** (2) and **`max_pr_lines`** (400) join `max_open_prs` and `max_in_uat`. Agents follow them (`AGENTS.md`, `/build`).
- The no-UAT lane auto-merges only when CI and both AI reviews run on GitHub (`ci: every-pr`, `review: github`). With anything less, the owner ships those PRs.
- With `grouping: release`, running `ship` again carries on with the same release PR (after exit 2 or 3, `--live` included) rather than building a second one. `ship --all` then also ships the other ready PRs (no-UAT, overrides). A merged change's branch is deleted only if nobody pushed to it since. `release` can't be combined with `flow: checks-first`.
- `local-ci` runs `make setup` first, with the local files from `.worktreeinclude`.
- A release that failed its checks, was closed, or whose branch changed no longer blocks the next one. `ship --abandon-release` closes it (or `ship` does it by itself when the PR was closed or moved), keeps every other pass and builds a fresh release next time. `test-failed` takes a change out of the next release. Passing a change again while it's in an open release is kept for the next release, not lost.
- `config` refuses to change `--flow`, `--deploy`, `--protected`, `--unprotected` or the limits on an existing project without `--human`, or from an agent's worktree. `github --apply` takes `ci` and `deploy_approval` from `main`'s `haam.config.json`, not the working copy, and says when they differ.
- `settings --apply` reports what it couldn't change (`failed` in `--json`) instead of counting it as applied, so running it again retries.

### Migration
- `haam.py update`, then merge the updated workflows (`ci.yml`, `security.yml`, `review.yml`, `gates.yml`).
- Nothing changes until you choose: the defaults are today's behaviour, except `worktree_cleanup`, which is now `after-ship`. Type `/haam-settings` to go through them.

## [1.8.1] - 2026-10-19

Two fixes found while updating a real project to 1.8.0.

### Fixed
- **The no-UAT lane no longer trusts a label to keep protected areas out.**
  - The gate now checks the files a PR changes against `protected_paths` in `haam.config.json`, read from `main`, not from the PR.
  - When any of them is touched, it adds `human-review`, explains why on the PR, and keeps the lane closed, whatever the labels say.
  - The defaults cover agent and CI configuration. Add the project's own areas with `haam.py config --protected "src/auth/**,db/migrations/**"`; `/haam-setup` asks for them.
  - A file moved out of a protected folder counts by its old path too. A PR with more than 3,000 files (GitHub lists no more) counts as protected.
  - Patterns: `**` any folders, `*` within one folder; a plain name (`src/auth`) or a trailing `/` means the whole folder, and a leading `./` is ignored. `config --protected` warns about a pattern that matches no file.
  - New `haam.py protected` lists the protected files a branch changes, so agents know before opening the PR. It fails rather than reporting "clean" when it can't compare with the base.
  - This means a kit update never takes the lane: it changes agent configuration, so you review and ship it yourself.
- **The first PR after a kit update no longer fails its reviews.** The reviews read their instructions from `main`, which still had the old wording ("post your comment yourself"), and that's now refused. The workflow now tells the reviewers how to report: write the files, never post. That works with any version of the instructions.

### Migration
- `haam.py update`, then merge the updated `gates.yml` and `review.yml`.
- Add your protected areas: `haam.py config --protected "<patterns>"`, then commit `haam.config.json`. Until then the gate uses the defaults.

## [1.8.0] - 2026-10-19

Fewer merges and deploys for the product owner.

### Added
- **No-UAT lane** for changes the owner can't meaningfully test, such as a kit or config update, a dependency bump, an invisible refactor or CI. The owner marks the issue `uat:skip`, once, in `/triage` (new *UAT* column) or by saying "spec approved, no UAT".
  - The agent skips `/uat` and opens the PR straight away, labelled `uat:skip`.
  - `release-gate` passes once every issue the PR is for (title and branch, never the description) is an open issue, not a PR, carrying the owner's label.
  - On GitHub Projects the gate turns on auto-merge, so the PR merges by itself when CI and both AI reviews pass. This uses `HAAM_PROJECT_TOKEN` (now with the `repo` scope), because a merge by the workflow's own token wouldn't start the deploy.
  - The gate re-checks when the owner adds or removes `uat:skip` on an issue, or the PR's title changes, and turns auto-merge off again when the lane no longer applies.
  - On Linear the gate can't read the issue: it trusts the PR label but never auto-merges, so the owner ships it. No auto-merge either when the AI reviews run on the owner's computer (`HAAM_REVIEW=local`), since those results aren't tamper-proof.
  - Never for PRs labelled `human-review`.
  - Agents can't add `uat:skip` to an issue: `issue label` and `issue create --label` refuse it without `--human` (and now refuse `agent-ready` in `create` too, which they didn't before).
- **`/test all`**: tests everything waiting in UAT in one sitting, then asks once to ship what passed.
- **`ship --all --human`** (or `ship 12 13 14 --human`): one production deploy for many changes.
  - It merges every PR that passed UAT or is in the lane, and includes merged ones still waiting to deploy.
  - It waits for the deploy run of the newest merge, cancels the older waiting runs, approves that one deploy, then closes every issue.
  - If any PR's checks are still running, it deploys nothing yet (exit 2) so it stays one deploy.
  - `--all` needs GitHub Projects; on Linear, list the issues.
- **Every `ship` deploys what's waiting.** A merged change whose deploy run is waiting for approval (a lane merge, or one approved nowhere) no longer blocks the next deploy: `ship` cancels that older waiting run, approves the newest (it contains both), and closes every issue in Deploying that went out with it. If any deploy that includes the change succeeded, it's live, even if a later one failed. A deploy run someone cancelled stops `ship` with a clear message instead of waiting. Only deploy runs on the default branch count.
- `github --apply` allows auto-merge on the repository.

### Fixed
- `issue create` (and any first status or priority change) no longer fails with "Content already exists in this project" when the board's own Auto-add workflow puts the issue on the board first. It uses that card and sets the fields.

### Migration
- `haam.py update`, then:
  - `haam.py github --apply` (allows auto-merge and adds the `uat:skip` label);
  - `haam.py github-project --apply` (GitHub Projects) or `haam.py linear --apply` (Linear) for the issue label.
- Merge the updated `gates.yml`.
- For auto-merge, the repository needs the `HAAM_PROJECT_TOKEN` secret (`docs/process/TRACKER.md`; Linear projects too). Without it, lane PRs wait for your `ship --all`.

## [1.7.2] - 2026-10-19

Fixes found while updating a real project from 1.2.0 to 1.7.x.

### Fixed
- **`/override` now satisfies the gate.** The skill posted `OVERRIDE (Level 1, skip UAT) by …: <reason>`, which `gates.yml` didn't accept (it wants a comment starting `OVERRIDE:`) and which didn't even start a gate run, so the gate stayed red. The skill now posts `OVERRIDE: <reason> (Level 1, skip UAT, by @user)` before adding the label; the gate also accepts the older wording (`OVERRIDE (…) by @user: <reason>`, capitals only, so an ordinary comment that starts "Override …" doesn't count). A test checks the skill's comment against the gate's own pattern.
- **`/override` works on a PR with no issue** (a kit update, a config change): `/override PR <number> "<reason>"` skips the issue comment and the follow-up issue.
- **The AI review always leaves its comment.** The reviewer used to post the comment itself, and that could be refused (long comments), leaving "Changes requested: see PR comment" with nothing to read. The reviewer now writes `review-comment.md` and the workflow posts it with the verdict (approvals too). Changes requested with no comment is reported as an `error` (re-run), not a `failure`. The security review on the Claude plan token works the same way (`security-comment.md`). Neither session can post comments any more.
- **`dev --apply` no longer switches off a repository's own git hooks.** `core.hooksPath` (shared by every worktree) made git ignore `.git/hooks`. If a clone has hooks of its own, the secret scan is now chained from `.git/hooks/pre-commit` instead, and a clone already switched the old way is moved over (your `.git/hooks/pre-push` and others run again). A `pre-commit` of your own is never edited: the tool prints the one line to add (it does nothing on branches without the kit), and leaves `core.hooksPath` alone until you have, so a scan that's on stays on. `make hooks` also restores the scripts' executable bits, as before. New `haam.py hooks [--apply]`; `make hooks` uses it; `doctor` warns when the old setting is hiding hooks.
- **`.mcp.json` removed by the project stays off:** the settings merge no longer switches its servers back on in `.claude/settings.json` (GitHub-tracker projects were fixed in 1.7.1).
- **`tracker-sync` no longer starts a runner for a PR closed without merging.**

### Changed
- `max_open_prs` and `max_in_uat` default to 10 (were 5 and 3). `capacity` lists the PRs and UAT issues it counted (`--list`, and always when it holds work) and says how to make room.

### Migration
- `haam.py update`, then `make hooks` (or `haam.py dev --apply`) once per clone.
- Your `haam.config.json` keeps the limits it already has: raise them with `haam.py config --max-open-prs 10 --max-in-uat 10`.
- **Moving from checks-first to test-first (1.7.0):** PRs opened under checks-first (drafts, red, blocked, or waiting for UAT) still count towards `max_open_prs`. Close the ones that are stale, red or untested: in test-first, `/test` and `publish` work from the branch, so closing a PR loses nothing, and the PR opens again after your pass. `haam.py capacity --list` shows what's counted.

## [1.7.1] - 2026-10-18

Two fixes reported from a project running v1.7.0.

### Fixed
- **No Linear connection on GitHub-tracker projects.** The settings merge kept re-adding `linear` to `enabledMcpjsonServers` in `.claude/settings.json` (and the Linear server to `.mcp.json` / `.cursor/mcp.json`) on every update, even after the project removed it. Now, when `"tracker"` is `github`, the kit's Linear entries are never installed or merged. `config --tracker github`, `agents` and `update` also take out what an earlier version added; a file that held only the Linear server is removed (and comes back if the project later switches to Linear), and the project's own servers, including one it calls `linear`, are kept and stay switched on. `agents` no longer asks GitHub-tracker projects to sign in to Linear.
- **The security review runs on the Claude plan token.** With only `CLAUDE_CODE_OAUTH_TOKEN` (no `ANTHROPIC_API_KEY`), `security-review` used to stay red. Now a Claude session follows the new `.github/review/SECURITY-REVIEWER.md` and reports the number of findings. With an API key, Anthropic's security review action runs as before. One secret, either one, runs both reviews; `github` and the setup docs say so.

### Changed
- Both AI reviews read their instructions (`REVIEWER.md`, `SECURITY-REVIEWER.md`) from the base branch, not from the PR, so a PR can't rewrite its own review rules (the first PR, before the kit is on `main`, uses its own copy). A `review-verdict.txt` or `security-findings.txt` committed in the PR is deleted before the review, so it can't stand in for one.
- README, `SECURITY.md` and the lifecycle say either secret works.

### Migration
- `haam.py update`. On GitHub-tracker projects it removes the Linear connection the earlier versions added. Merge the updated `review.yml` and the new `SECURITY-REVIEWER.md`.

## [1.7.0] - 2026-10-18

### Added
- **Test-first flow** (the new default, `"flow": "test-first"`): the owner tests a change before any pull request exists, so only tested work reaches GitHub's checks.
  1. The agent builds, runs `make check`, writes the UAT plan and release note, and pushes its branch (free: branch pushes start no workflows). It opens no PR.
  2. The owner's `/test` checks out the agent's branch (`checkout-pr` now falls back to the branch when there's no PR, local or pushed).
  3. On `pass`, **`haam.py publish <ID> --human`** pushes exactly the tested commit and opens the PR labelled `uat-passed` (`--also` for a batch); the checks and reviews run once, on that commit. On `ship`, `ship` merges it as before.
  4. A failed test costs no Actions minutes. A failed check sends the issue back to the agents (`uat-failed`), and changed code is always tested again (`publish` and `ship` refuse anything else).
- `config --flow test-first|checks-first`. Checks-first keeps v1.6.0's order (draft PR, checks, then the owner's test).
- **A pass belongs to the tested commit.** `publish` records it on that commit as a `uat` status; `gates.yml` now also watches pushes to drafts that carry `uat-passed`, and removes the label when a push brings code that wasn't tested (in both flows); one gate run per PR at a time. So a later agent push can't be merged by hand in GitHub on the strength of an old pass. `publish` also checks the PR it opened points at the tested commit, and `ship` puts back a label the gate removed in a race when the head is still the tested commit.
- **`haam.py test-failed <ID> --human`** (`/test` and `/uat-result` on a fail): marks the tested commit's `uat` status as failed and removes `uat-passed` from an open PR, so an earlier pass of that commit can't be reused.
- `checkout-pr --branch <name>`; `publish --label <name>` (Linear: `human-review`); `capacity --in-uat N` (Linear: the agent counts the UAT items).

### Changed
- `/build`, `/uat`, `/test`, `AGENTS.md`, the lifecycle, the gates and the product manager guide describe both orders; in test-first G4 comes before G3.
- During rework on an open PR, agents turn it back into a draft before pushing, so their fixes don't start the checks until the owner has tested them.
- Finding the branch to test: GitHub's branches win over ones only on this computer (the push is the hand-over; leftovers and differences are reported), deleted remote branches are pruned, spike branches never count, Linear's `user/app-12-…` names are recognised, and a batch's branch is found from any of its issues through the ``branch `…` `` in the claim or UAT comment. `publish` covers the whole batch (the issue the branch is named after comes first), reads `--also` before pushing anything, and on Linear prints the tracker steps to do.
- `ship` waits for the checks of a just-opened PR to start, and for the gate to re-run after a label change, for up to 5 minutes after the PR's last update (so re-running `ship` doesn't restart the clock), instead of stopping.
- On a PR that already exists, `publish` adds the labels before marking it ready, and turns it back into a draft if its head turns out not to be the tested commit.
- `/uat-result pass` in test-first opens the PR through `publish`; the claim and UAT comments write the branch in backticks.

### Migration
- `haam.py update`. Projects get test-first by default; to keep the previous order, `haam.py config --flow checks-first`.
- Merge the updated `gates.yml` (it needs `pull-requests: write` to remove a stale label).

## [1.6.0] - 2026-10-18

Spending far fewer GitHub Actions minutes per pull request.

### Added
- **Draft first, check once.** Agents open PRs as drafts and push freely; CI, the secret scan, the dependency audit, both AI reviews, the UAT gate and the board sync skip drafts. When the change is complete (code, tests, UAT plan, release note, rebased), the agent marks it ready (`gh pr ready`) and everything runs once. Each round of review fixes goes in one push.
- **`haam.py ci-usage [--days 7]`**: where the minutes went, by workflow, job, trigger and day (every attempt, rounded up per job; macOS counted 10x, Windows 2x; own runners shown separately).
- **`haam.py ci-settings`**, two switches stored as repository variables the workflows read:
  - `--review local`: the AI reviews run on the owner's computer instead of in Actions. `haam.py review <ID>` checks out the PR's commit cleanly, gathers the diff, the PR description and the spec-approval check itself, and starts two fresh agent sessions that can only read files (`claude -p` with Bash and edits disallowed, or `"review_command"` from `main`'s `haam.config.json`), using the review instructions from `main`, not the PR's branch. The tool posts their comments and the `ai-review` and `security-review` statuses on that exact commit (and refuses if the PR moved meanwhile). On GitHub the review job just shows *Waiting for the local review*; PRs labelled `human-review` are always reviewed on GitHub. Trade-off: the result is no longer tamper-proof, since the building agent starts the review and anything using the owner's login could post a pass.
  - `--runner self-hosted` (private repos only; refused if the repository can't be confirmed private): every job except the deploy runs on your own machine (`runs-on: ${{ vars.HAAM_RUNNER || 'ubuntu-24.04' }}`).
- Batches cover an epic's small features with approved specs as well as its bugs: one branch, one PR, one CI run, tested together.

### Changed
- `/build` writes the UAT plan and release note before marking the PR ready, so `/uat` no longer pushes (which re-ran everything).
- The secret-scan job reuses gitleaks if the runner already has it.
- The board and Linear move an issue to In Review when its PR is marked ready, not when the draft opens.
- Setup (`/haam-setup` Phase 6), `GITHUB-SETUP.md` §8 and the product manager guide §10 explain the cost switches.

### Migration
- `haam.py update`. Nothing else is required: drafts and the new triggers work straight away.
- Optional: `haam.py ci-usage` to see your spend; `haam.py ci-settings --review local --apply` and/or `--runner self-hosted --apply`.

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

[Unreleased]: https://github.com/jorgedpl/haam-kit/compare/v1.9.0...HEAD
[1.9.0]: https://github.com/jorgedpl/haam-kit/compare/v1.8.1...v1.9.0
[1.8.1]: https://github.com/jorgedpl/haam-kit/compare/v1.8.0...v1.8.1
[1.8.0]: https://github.com/jorgedpl/haam-kit/compare/v1.7.2...v1.8.0
[1.7.2]: https://github.com/jorgedpl/haam-kit/compare/v1.7.1...v1.7.2
[1.7.1]: https://github.com/jorgedpl/haam-kit/compare/v1.7.0...v1.7.1
[1.7.0]: https://github.com/jorgedpl/haam-kit/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/jorgedpl/haam-kit/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/jorgedpl/haam-kit/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/jorgedpl/haam-kit/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/jorgedpl/haam-kit/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/jorgedpl/haam-kit/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/jorgedpl/haam-kit/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/jorgedpl/haam-kit/releases/tag/v1.0.0
