---
name: haam-setup
description: First-time adoption of the Human-Agent Agile Methodology (HAAM) in a repository, run with the project admin. Installs the kit, configures the project, agents, GitHub and the tracker (GitHub Projects or Linear), and fills in project knowledge. Use when the admin asks to set up, install or adopt HAAM.
argument-hint: "[path to the unzipped HAAM kit, if HAAM isn't installed yet]"
disable-model-invocation: true
---

# /haam-setup: adopt HAAM in this repository (project admin)

Kit path (if given): $ARGUMENTS. This is the kit's `template/` folder, e.g. from `git clone --depth 1 --branch vX.Y.Z https://github.com/jorgedpl/haam-kit.git`, or an unzipped release.

You are guiding the **project admin** through adopting HAAM. The tool `tools/haam/haam.py` does the mechanical work; you do the judgement work (merging files, reading the codebase, asking the human) and keep the human in control of every change to GitHub and Linear.

**Rules for this skill**
- Show plans before applying. GitHub and tracker changes run with `--apply` **only after the human says yes** to the plan you showed.
- **Never ask the human to paste a secret into the chat**, and never read `.env*`. Steps marked `[YOU, in your terminal]` are done by the human in their own terminal; give them the exact command and wait.
- Work on a branch. Never push to `main`.
- After each phase, give a two-line status: done / waiting on the human.
- If you can't run commands (some tools can't), show each command for the human to run and continue from their output.

## Phase 0: Check the starting point
1. Confirm you're at the root of the project's git repository (`git rev-parse --show-toplevel`).
2. Ask the human to confirm they are an **admin** of the GitHub repository (and of the Linear workspace, if they choose Linear). Explain in 3 lines what will happen: install files on a branch, configure, open a PR, set up GitHub and Linear, then a trial run.
3. If `AGENTS.md` and `tools/haam/haam.py` already exist, HAAM is installed: skip to Phase 2.

## Phase 1: Install the kit
1. `git switch -c chore/adopt-haam` (from an up-to-date default branch).
2. `python3 <kit-path>/tools/haam/haam.py install --target . --dry-run`, then show the summary, then run it without `--dry-run`. This records the kit version in `haam.lock.json` (commit it: it's how future upgrades know what was installed).
3. For each conflict reported, merge the kit version from `.haam/incoming/` into the existing file, following the table in `docs/setup/HAAM-ADOPTION-GUIDE.md` (Phase 1). Key cases:
   - **Existing `CLAUDE.md` / `AGENTS.md` / `.cursorrules` / `.cursor/rules`**: move project-specific knowledge (conventions, commands, gotchas) into `docs/product/ARCHITECTURE.md` or a "Project specifics" section at the end of `AGENTS.md`; then replace the file with the kit version. Show the human what you moved.
   - **Existing CI**: keep it, make sure a job called `ci` runs the full test suite on PRs; add the kit's other workflows.
   - **Existing `Makefile`**: add the kit's targets.
4. Delete `.haam/incoming/` when everything is merged.

## Phase 2: Project configuration
1. Ask the human, in **one** message:
   - Product name
   - **Tracker:** GitHub Projects (free, everything in GitHub; recommended for small teams) or Linear (nicer UX, free plan limited to a few hundred issues). See `docs/process/TRACKER.md`.
   - A short product key (2–5 capital letters, e.g. `ACM`): the Linear team key if they use Linear
   - GitHub repo (`owner/name`): propose the one from `git remote get-url origin`
   - Product owner's GitHub username (approves production deploys) and any backup approvers
   - Production URL (or none yet)
   - Which agent tools the team uses (Claude Code, Cursor, Codex, Grok, Gemini, Copilot)
   - How production is deployed: by `deploy.yml` when a PR merges (`github`), or by hand / another platform (`manual`)
   - Limits for parallel work (defaults are fine to start): at most 10 open PRs and 10 changes waiting for their test
   - The protected areas as folder or file patterns (AGENTS.md §4: authentication, payments, personal data, migrations…), e.g. `src/auth/**,db/migrations/**`. Agent and CI configuration are protected already. Changes there always get a human code review and never take the no-UAT lane: the gate checks the changed files.
   - The order of testing: **test-first** (default: they test the agent's branch locally, and the PR and checks come only after their pass, which saves the most CI minutes) or **checks-first** (PR and checks, then their test)
2. `python3 tools/haam/haam.py config --product "…" --tracker github|linear --team-key … [--linear-team "…"] --github-repo … --owner … [--backup-approvers a,b] [--production-url …] --agents claude,cursor,… --deploy github|manual [--max-open-prs 10] [--max-in-uat 10] [--flow test-first|checks-first] [--protected "src/auth/**,db/migrations/**"]`
3. `python3 tools/haam/haam.py agents --apply` and report per tool.
   Then offer `/haam-settings`, which the human types themselves, to choose how CI, the AI reviews, testing, grouping and shipping work here. The defaults are a safe start.

## Phase 3: Teach HAAM about the project (your judgement work)
1. **Command contract:** inspect the project (package.json, pyproject.toml, composer.json, go.mod, existing CI, README) and fill every `TODO(setup)` in `Makefile` (`setup`, `dev`, `test`, `lint`, `typecheck`, `build`, `audit`, `deploy` if they deploy from CI), and the runtime setup steps in `.github/workflows/ci.yml`, `security.yml`, `deploy.yml`. CI passes `make check` the list of changed files in `$CI_CHANGED_FILES`; if the project has clearly separate parts (e.g. a backend and a mobile app), offer to make `make check` run only the parts a PR touches, which saves a lot of CI minutes (the nightly run still checks everything). Run `make check`. If it fails on the current code, show the human why and agree whether to fix first or mark known failures.
2. **Architecture map:** fill `docs/product/ARCHITECTURE.md` from the codebase (under 150 lines).
3. **Protected areas:** propose real paths for `AGENTS.md` §4; confirm with the human.
4. **Product context:** draft `docs/product/PRODUCT.md` from the README and code, then ask the human to correct it, especially *Current priorities* and *Non-negotiables*. Don't invent business facts.
5. **Onboarding doc:** fill the `TODO(setup)` items in `docs/ONBOARDING.md` (clone URL, runtime, local URL).
6. `python3 tools/haam/haam.py doctor` until no `TODO(setup)` remains that you can fill.

## Phase 4: Secrets hygiene
1. `make hooks` (turns on the commit secret scan on this machine).
2. One-time history scan: `gitleaks git --redact --no-banner .` Report **how many** findings and **which files/commits**, never the values. For each real one, tell the human it must be **revoked and rotated** with the provider (it's already exposed to anyone with repo access). False positives: the human approves adding fingerprints to `.gitleaksignore`.

## Phase 5: Open the adoption PR
Commit (`Adopt the Human-Agent Agile Methodology (HAAM)`), ask before pushing, push the branch, open a PR. This makes the checks exist in GitHub so they can be required.

## Phase 6: GitHub
1. `python3 tools/haam/haam.py github` → show the plan in plain words → on the human's yes: `… github --apply`.
2. Human-only steps the tool lists, e.g. `[YOU, in your terminal] gh secret set CLAUDE_CODE_OAUTH_TOKEN -R owner/name` (or `ANTHROPIC_API_KEY`; either runs both reviews) and the fork-PR setting in the browser. Wait for confirmation, then re-run `github` to verify.
3. If something needs a paid GitHub plan, explain the trade-off briefly and continue.
4. **Actions minutes** (private repositories have a monthly allowance). Explain the choices in a few lines and ask:
   - AI reviews on GitHub (default: tamper-proof, but each review keeps a runner busy while Claude reads) or **on the owner's computer** (`haam.py review`, uses their Claude plan; protected-area PRs still reviewed on GitHub): `python3 tools/haam/haam.py settings --set review=local --apply --human`.
   - Their **own runner** (a computer or small server that stays on) instead of GitHub's machines, for private repos only: register it (Settings → Actions → Runners), then `settings --set runner=self-hosted --apply --human`.
   - After the first busy week, `python3 tools/haam/haam.py ci-usage` shows where the minutes went.

## Phase 7: The tracker

**If GitHub Projects** (`"tracker": "github"`):
1. `[YOU, in your terminal]` `gh auth refresh -s project` (lets the human's GitHub login use Projects).
2. `python3 tools/haam/haam.py github-project` → show the plan → on the human's yes: `… github-project --apply`. It creates the board, links the repo, sets the 12 statuses and Priority, creates the labels, and saves the board number in `haam.config.json`.
3. `[YOU, in your terminal]` the automation token, exactly as the tool prints it (`gh secret set HAAM_PROJECT_TOKEN …`).
4. `[YOU, in the browser]` create the saved views the tool lists on the board, and turn on the board's **Auto-add to project** workflow for this repository (board → Workflows), so issues created on GitHub's website land on the board without using Actions minutes.
5. Verify: `python3 tools/haam/haam.py issue list`.

**If Linear** (`"tracker": "linear"`):
1. The Linear step needs the human's personal API key, so the **human runs it** in their terminal:
   `python3 tools/haam/haam.py linear` (plan), then `python3 tools/haam/haam.py linear --apply`.
   Ask them to paste you the **output** (it contains no secrets).
2. Walk them through the browser-only steps the tool lists (GitHub integration, PR automations, branch name format, saved views), using `docs/setup/LINEAR-SETUP.md`.
3. Connect your own tool to Linear (see `docs/setup/AGENTS-SETUP.md`) and verify: list the team's statuses and labels.

**Existing backlog** (GitHub issues, Jira, a spreadsheet…): offer to bring it into the tracker, everything into Triage first.

## Phase 8: Prepare for parallel chats
So the human can open several agent chats (on one or more computers) and type `/work` in each:
1. **Local files:** check which git-ignored files the app needs to run or test locally (`.env`, `.env.local`, local certificates, a local config file, `local.properties` with the Android SDK path) and make sure `.worktreeinclude` lists them. List paths only; never open or read them.
2. **Test discovery:** worktrees live inside the project, under `.claude/worktrees/`. If the project's test runner, linter, type checker, file watcher or bundler scans the whole folder, exclude `.claude/worktrees/` in its config so the main folder doesn't pick up the worktrees' copies.
3. **Dry run:** `python3 tools/haam/haam.py worktree new setup-check`, then in that folder `make setup && make check`. Fix anything that only worked because of files in the main folder. Then remove it: `git worktree remove .claude/worktrees/setup-check`.
4. Tell the human how to start an agent from now on: open a new chat window in their tool (Claude Code in VS Code: Cmd/Ctrl+Shift+Esc) and type `/work bugs` (or `features`, `ideas`, or nothing); Codex: `$work`. Their own chat in the main folder is for ideas, decisions, UAT and releases.

## Phase 9: Verify and hand over
1. `python3 tools/haam/haam.py doctor --role admin`. Fix what you can; list the rest.
2. Remind the human to merge the adoption PR (once checks are green they add `uat-passed` themselves; they can use `ai-review-overruled` if the reviewers nitpick the kit itself).
3. Propose the trial loop (Phase 5 of the adoption guide) with a small real ticket.
4. To add people later: `python3 tools/haam/haam.py invite --github USER --linear-email EMAIL` (plan), then `--apply` on the admin's OK. New developers then run `/haam-onboard`.
5. End with a checklist: done ✔ / waiting on the human ☐ (with exact commands or links).
