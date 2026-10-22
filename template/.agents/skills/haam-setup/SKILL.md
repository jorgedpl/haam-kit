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

**How to ask.** Every choice is in `docs/setup/DECISIONS.md` (in the kit's `template/` folder until it's installed). For each one, give a one-line recommendation for *their* situation and the reason, then ask. Use your tool's multiple-choice question feature if it has one, at most 4 questions at a time. Accept "you choose", and take the recommendation then.

## Phase 0: Check the starting point
1. Confirm you're at the root of the project's git repository (`git rev-parse --show-toplevel`).
2. **Accounts.** Ask whether everyone who will work on it has a GitHub account, and whether the repository belongs to an organization or to one person.
   - Someone has no account, or there's no organization yet: walk them through `DECISIONS.md` §1, *Accounts*. Each person signs up themselves; you never create accounts or handle passwords. Recommend an organization with two owners.
   - Check the GitHub CLI: `gh auth status`. If it isn't installed or signed in, they install it and run `gh auth login` themselves.
3. Ask the human to confirm they are an **admin** of the GitHub repository (and of the Linear workspace, if they choose Linear). Explain in 3 lines what will happen: install files on a branch, make the decisions together, open a PR, set up GitHub and the tracker, then a trial run.
4. **Plan.** Run `gh api repos/<owner>/<name> --jq '{private, owner: .owner.type}'`. Then find the plan: for an organization `gh api orgs/<org> --jq .plan.name` (it prints `null` unless they own the organization); for a personal account `gh api user --jq .plan.name`. If you can't tell, ask them. Then tell them in two or three lines what their plan means, from the table in `DECISIONS.md` §1:
   - public repository: everything works;
   - private on Free: no branch rules, so recommend Team (organization) or Pro (personal);
   - private below Enterprise Cloud: no approver on production deploys, so their `ship` is the release decision (`deploy_approval: automatic`).

   Let them decide whether to upgrade. Carry on either way.
5. If `AGENTS.md` and `tools/haam/haam.py` already exist, HAAM is installed: skip to Phase 2.

## Phase 1: Install the kit
1. `git switch -c chore/adopt-haam` (from an up-to-date default branch).
2. **Language:** the kit's docs come in English (`en`), Spanish (`es`), French (`fr`), German (`de`), Italian (`it`), Dutch (`nl`) and Portuguese (`pt`). If the human writes to you in one of these other than English, propose it; otherwise use `en`. Agents then write specs, issues, UAT plans and messages in that language; commands, labels and code stay in English.
3. `python3 <kit-path>/tools/haam/haam.py install --target . --language <code> --dry-run`, then show the summary, then run it without `--dry-run`. This records the kit version in `haam.lock.json` (commit it: it's how future upgrades know what was installed).
4. For each conflict reported, merge the kit version from `.haam/incoming/` into the existing file, following the table in `docs/setup/HAAM-ADOPTION-GUIDE.md` (Phase 1). Key cases:
   - **Existing `CLAUDE.md` / `AGENTS.md` / `.cursorrules` / `.cursor/rules`**: move project-specific knowledge (conventions, commands, gotchas) into `docs/product/ARCHITECTURE.md` or a "Project specifics" section at the end of `AGENTS.md`; then replace the file with the kit version. Show the human what you moved.
   - **Existing CI**: keep it, make sure a job called `ci` runs the full test suite on PRs; add the kit's other workflows.
   - **Existing `Makefile`**: add the kit's targets.
5. Delete `.haam/incoming/` when everything is merged.

## Phase 2: The decisions, in four short rounds
Each round is one message, with a recommendation per question (`DECISIONS.md` has them). Wait for the answers before the next round.

**Round 1: who and where** (`DECISIONS.md` §2–3)
- Product name, and a short product key (2–5 capital letters, e.g. `ACM`; with Linear, the team key).
- The GitHub repository (`owner/name`): propose the one from `git remote get-url origin`.
- The product owner's GitHub username (they decide, test and ship), and one or two backup approvers.
- **Tracker:** GitHub Projects or Linear. Recommend GitHub Projects unless they already work in Linear every day. Mention Linear's free cap and what's automatic only on GitHub Projects (§2's table).
- Which agent tools the team uses (Claude Code, Cursor, Codex, Grok, Gemini, Copilot).
- The production URL, or none yet.
- Confirm the language chosen in Phase 1. To change it: `python3 tools/haam/haam.py config --language <code>`, then `python3 <kit-path>/tools/haam/haam.py update --target . --apply` switches the kit's docs.

**Round 2: how work flows** (`DECISIONS.md` §4)
- **Testing order** (`flow`): `test-first` (recommended: they test the agent's branch, then the PR and checks run once) or `checks-first`.
- **What they test** (`uat`): `owner-decides` (recommended), `always` (regulated or safety-critical products) or `bugs-skip`.
- **Deploys** (`deploy`): by `deploy.yml` when a PR merges (`github`), or another way (`manual`).
- **Deploy approval** (`deploy_approval`): `each` (recommended) or `automatic`. Recommend `automatic` when the plan check in Phase 0 showed they can't have an approver (a private repository below Enterprise Cloud), and say why. If that leaves deploys automatic, advise against `uat: bugs-skip`: a bug fix could then reach production with nobody looking at it.

The other settings (grouping, where CI and the reviews run, nightly, runner) start at their recommended values. Mention that `/haam-settings` changes them any time and that the first week's `ci-usage` will show whether they need to.

**Round 3: limits** (`DECISIONS.md` §5)
Ask four numbers:
- how many people will run agent chats;
- how many chats each runs at once;
- how many hours a week the owner can test;
- in how many sittings.

Then run `python3 tools/haam/haam.py settings --recommend --builders N --chats N --testing-hours N --sittings N --flow <their choice>` and show its suggestion and notes (if they know how long one of their tests takes, or how many changes a chat finishes a day, add `--minutes-per-test` and `--changes-per-chat`), especially when the agents will out-produce the testing. They accept the numbers or change them.

**Round 4: what to protect** (`DECISIONS.md` §6) waits for Phase 3, when you've read the code and can propose real paths.

Then apply rounds 1–3:
1. `python3 tools/haam/haam.py config --product "…" --tracker github|linear --team-key … [--linear-team "…"] --github-repo … --owner … [--backup-approvers a,b] [--production-url …] --agents claude,cursor,… --deploy github|manual --flow test-first|checks-first --max-open-prs N --max-in-uat N --human` (`--human`: the owner chose these values with you now; re-running `config` later to change `--flow`, `--deploy`, `--protected` or the limits needs it too).
2. If they chose anything but the defaults for `uat` or `deploy_approval`: `python3 tools/haam/haam.py settings --set uat=… --set deploy_approval=… --human`. `github --apply` in Phase 6 sets up the deploy approval; `uat` takes effect for the release gate once the adoption PR is merged.
3. `python3 tools/haam/haam.py agents --apply` and report per tool.

## Phase 3: Teach HAAM about the project (your judgement work)
1. **Command contract:** inspect the project (package.json, pyproject.toml, composer.json, go.mod, existing CI, README) and fill every `TODO(setup)` in `Makefile` (`setup`, `dev`, `test`, `lint`, `typecheck`, `build`, `audit`, `deploy` if they deploy from CI), and the runtime setup steps in `.github/workflows/ci.yml`, `security.yml`, `deploy.yml`. CI passes `make check` the list of changed files in `$CI_CHANGED_FILES`; if the project has clearly separate parts (e.g. a backend and a mobile app), offer to make `make check` run only the parts a PR touches, which saves a lot of CI minutes (the nightly run still checks everything). Run `make check`. If it fails on the current code, show the human why and agree whether to fix first or mark known failures.
2. **Architecture map:** fill `docs/product/ARCHITECTURE.md` from the codebase (under 150 lines).
3. **Protected areas (round 4):** go through the checklist in `DECISIONS.md` §6. For each area that applies to this codebase, propose the real paths you found (e.g. `src/auth/**` for sign-in, `db/migrations/**`), with one line on why. Say which areas don't apply. Remind them that every protected change needs their code review and their test, so the list should cover what matters, not everything. On their OK:
   - `python3 tools/haam/haam.py config --protected "<patterns>" --human` (it warns about a pattern that matches no file);
   - replace the examples in `AGENTS.md` §4 with the same areas in words.

   **Production code** (`DECISIONS.md` §8): by default everything except prototypes, tests and docs counts as production code, which always meets every gate. If the product's code clearly lives in a few folders (e.g. `src/`, `api/`, `mobile/`), propose `config --production "src/**,api/**" --human` and, for folders that never run for users (fixtures, sample data, internal tools), `config --not-production "…" --human`. Tell them in one line that `/spike` and epic build mode exist for when they want agents to build freely.

   If the tests use something the whole machine shares (a local database they clone, a simulator, a device), also propose `config --heavy-run "<pattern>"` (`DECISIONS.md` §7).
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
