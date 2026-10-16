---
name: haam-onboard
description: Onboard a developer who is joining a project that uses the Human-Agent Agile Methodology (HAAM). Checks their machine, access, agent tool and tracker connection, sets up local hooks and environment, explains the way of working and suggests a first issue. Use when someone new asks to get set up, get started or onboard.
disable-model-invocation: true
---

# /haam-onboard: get a developer ready to work

You're helping a developer (human) get ready to work on this project with their own agent tool and accounts. Be friendly and efficient. Aim for under an hour in total.

**Rules for this skill**
- **Never ask for secrets in chat** and never read or write `.env*` contents yourself. The developer fills credentials in their own editor.
- Show what a command will change before running it with `--apply`.
- If you can't run commands, show them and continue from the developer's output.

## 1. Where are we?
1. Confirm you're at the repo root and on the default branch, up to date: `git status`, `git pull`.
2. Read `haam.config.json` (product, team key, repo) and greet the developer with one line about the product from `docs/product/PRODUCT.md`.

## 2. Machine check
1. `python3 tools/haam/haam.py dev` (plan). Explain anything missing in plain words.
2. Missing tools are `[YOU, in your terminal]` installs (git, gh, make, gitleaks). Give the command for their OS, wait, re-run.
3. On their OK: `python3 tools/haam/haam.py dev --apply` (turns on the commit secret hook, creates `.env` from `.env.example` if missing).

## 3. Access
1. GitHub: `gh api repos/<github_repo> --jq .permissions`. If no access, or no `push` permission: tell them to ask the project admin to run
   `python3 tools/haam/haam.py invite --github <their-username> --linear-email <their-email> --apply`, then accept the emails. Pause until done.
2. Tracker (`"tracker"` in `haam.config.json`): **GitHub Projects**: the invite also shares the board; they run `gh auth refresh -s project` in their terminal. **Linear**: they need membership of team `<team_key>`; the same invite command covers it.
3. Test credentials: they come from the product owner via a password manager or one-time link. The developer pastes them into `.env` themselves.

## 4. Connect to the tracker
- **GitHub Projects:** nothing to install. Verify: `python3 tools/haam/haam.py issue list --status Ready`. If it says the login can't use Projects: `gh auth refresh -s project`.
- **Linear:** connect their agent tool using `docs/setup/AGENTS-SETUP.md` (Claude Code, Cursor, Codex, Grok, Gemini, Copilot), then list the issues in status **Ready** for team `<team_key>`.

## 5. Run the project
1. `python3 tools/haam/haam.py dev --run-checks` (runs `make setup` and `make check`).
2. If anything fails, explain why and fix only setup problems on their machine. Don't change project code during onboarding.
3. `make dev` and give them the local URL from `docs/product/ARCHITECTURE.md`.

## 6. How we work (5 minutes)
Explain briefly, in your own words, from `AGENTS.md`, `docs/process/LIFECYCLE.md` and `docs/process/GATES.md`:
- The lifecycle: idea → assess → decide → spec → build → checks & AI review → UAT → deploy, and which steps are human-only.
- The commands for **their** tool (`/build` vs `$build`), the hard rules (no push to `main`, no secrets, claim before building, small PRs).
- How review works: reviewer agents block, humans overrule; two failed rounds → hand over.
- Where things live: the tracker for work (`docs/process/TRACKER.md`), Git for knowledge (`docs/`).

## 7. First task
1. Show the top 3 items from the **Agent queue** (status Ready, `agent-ready` or `stream:bug`, unassigned). Prefer something small.
2. Offer to start it together with the build skill, explaining each step as it happens the first time.
3. Explain how to run agents in parallel from now on: one new chat window per agent, each started with `/work` (Codex: `$work`), which gives it its own worktree. The chat in the main folder is theirs, for ideas, testing and reviews. On a second computer, the same: clone, `/haam-onboard` once, then `/work`.

## 8. Wrap up
Run `python3 tools/haam/haam.py doctor` and finish with a checklist: ready ✔ / still to do ☐ (with who and how).
