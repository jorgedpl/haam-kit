# Human-Agent Agile Methodology (HAAM)
## Adoption guide for the project admin

HAAM is a way of building software where **humans decide and agents execute**. Every piece of work goes from idea to production through the same stages, with human gates at the points that matter. Everything lives in **Git** (knowledge and code) and the **tracker** (work and status): a **GitHub Projects** board (free) or **Linear**. People can use different coding agents (Claude Code, Cursor, Codex, Grok, Gemini, Copilot) with their own accounts and still work in parallel.

This guide applies HAAM to an existing repository in **six phases, about half a day in total**. You can stop after any phase and still have something useful.

---

## Getting the kit

The kit is the `template/` folder of https://github.com/jorgedpl/haam-kit. Always use a released version:
```bash
git clone --depth 1 --branch v1.4.0 https://github.com/jorgedpl/haam-kit.git ~/haam-kit   # kit = ~/haam-kit/template
```
or download the zip from the Releases page. Below, `<path-to-kit>` means that `template/` folder.

## The fast path: let your agent do it

Get the kit somewhere outside your project, open your coding agent **in your project's root folder**, and say:

> Read `<path-to-kit>/.agents/skills/haam-setup/SKILL.md` and follow it to set up HAAM in this repository. The kit is at `<path-to-kit>`.

The agent drives the setup tool (`tools/haam/haam.py`) through every phase below. It asks you a handful of questions, shows each change before making it, and hands you the few steps that need your passwords or keys to run in your own terminal. Use the rest of this guide to understand what it's doing, or to do it by hand.

### Who does what during setup

| Marked as | Means |
|---|---|
| `[agent]` | Your coding agent does it (or you, if doing it by hand) |
| `[YOU, in your terminal]` | You run the command yourself: it involves a secret (API key, login) that must never pass through an agent's chat |
| `[YOU, in the browser]` | A setting that GitHub or Linear only offers in its web app |

---

## What you get

```
START-HERE.md                 Kit entry point (not copied into your repo)
AGENTS.md                     Rules every agent reads, whatever the tool
CLAUDE.md                     Pointer to AGENTS.md for Claude Code
haam.config.json              Project settings for the setup tool (created by `config`; no secrets)
haam.lock.json                Installed kit version and file fingerprints (used by `update`)
CHANGELOG.md                  Release notes, maintained by /release
Makefile                      Command contract: setup, hooks, dev, test, check, audit, secrets, smoke, deploy
tools/haam/haam.py            Setup tool: install, config, agents, github, github-project, linear, issue, worktree, invite, dev, doctor
scripts/scan-secrets.sh       Secret scan (gitleaks) shared by all commit hooks
.githooks/pre-commit          Blocks commits containing secrets (any human, any agent using git)
.agents/skills/               One skill per stage, shared by all agent tools
.worktreeinclude              Local files (like .env) to copy into each agent's worktree
.claude/                      Claude Code: settings (guard-rails), hooks, skills link
.cursor/mcp.json              Cursor: Linear connection (Linear projects)
.grok/skills                  Grok Build: skills link
.gemini/settings.json         Gemini CLI: read AGENTS.md
.mcp.json                     Linear connection (Claude Code, Grok; Linear projects)
.github/
  pull_request_template.md    Includes "Built with" (agent tool and model)
  workflows/ci.yml            Gate G3: tests on every PR
  workflows/security.yml      Gate G3: secret scan of every commit + dependency audit
  workflows/review.yml        Gate G3: independent AI reviewers (spec/quality + security)
  workflows/tracker-sync.yml    Moves GitHub Projects cards when PRs open and merge
  ISSUE_TEMPLATE/              Idea and bug forms (GitHub Projects)
  workflows/gates.yml         Gate G4: blocks merge until UAT passed or overridden
  workflows/deploy.yml        Gate G5: production deploy waits for human approval
  review/REVIEWER.md          Instructions for the reviewer agent
  dependabot.yml              Dependency update PRs
docs/
  process/LIFECYCLE.md        The methodology: streams, stages, statuses, roles
  process/GATES.md            Gate checklists, code review, overrides
  process/TRACKER.md          How each tracker operation works on GitHub Projects and on Linear
  product/PRODUCT.md          Your product context (you confirm it)
  product/ARCHITECTURE.md     Map of your codebase (the agent drafts it)
  setup/HAAM-ADOPTION-GUIDE.md  This guide
  setup/AGENTS-SETUP.md       Per-tool setup: Claude Code, Cursor, Codex, Grok, Gemini, Copilot
  setup/LINEAR-SETUP.md       Linear configuration in detail
  setup/GITHUB-SETUP.md       GitHub configuration in detail
  ONBOARDING.md               Guide for new developers
  templates/                  idea, bug, assessment, feature-spec, uat-plan, adr
  decisions/0001-adopt-haam.md
  assessments/ specs/ uat/    Filled in automatically as work flows
```

### The lifecycle in one picture

```
Idea ─► Assess ─► [G1 Decide] ─► Spec ─► [G2 Ready] ─► Build + unit tests ─► [G3 CI + secret scan + AI review]
     ─► UAT plan ─► [G4 You test locally] ─► Merge ─► [G5 Approve deploy] ─► Production ─► Done
```

### The commands

Written `/name` here (Claude Code, Cursor, Grok). In Codex use `$name`. Any other tool: *"follow `.agents/skills/<name>/SKILL.md`"*.

| Command | Stage | Who |
|---|---|---|
| `/idea <text>` | Capture an idea | Anyone |
| `/bug <text>` | Report a problem | Anyone |
| `/assess APP-12` | Evaluate value, effort, risk, feasibility | Agent |
| `/triage` | Triage the inbox, group issues into epics (`group`), re-rank (`backlog`), chase stuck work (`stale`) | Human only |
| `/epic APP-9` | Shape an epic: brief, questions for you, clean-up of its issues | Human only |
| `/decide APP-12 approve` | Gate G1 | Human only |
| `/spec APP-12` | Write a build-ready spec | Agent |
| `/work bugs` | Start an agent in a new chat window: own worktree, then `/next` | Anyone |
| `/next` | Pick the next item from bugs, features and ideas | Agent |
| `/build APP-12` | Implement with unit tests, open a PR | Agent |
| `/uat APP-12` | Write your local test plan | Agent |
| `/test` | Test a change, then `pass` → `ship`, or say what's wrong (G4 and G5) | Human only |
| `/uat-result APP-12 pass` | Record a test result by itself (G4) | Human only |
| `/override APP-12 "reason"` | Skip UAT in an emergency | Human only |
| `/release APP-12` | Close out after deploy | Human only |
| `/haam-setup` | Adopt HAAM in a repo | Project admin |
| `/haam-onboard` | Get a new developer ready | New developer |
| `/haam-update` | Upgrade to a new kit version | Project admin |

### How code review works

No agent ever reviews its own work, and secrets are caught by a scanner rather than by judgement. Every change passes through six layers:

| Layer | When | What it checks | Who does it |
|---|---|---|---|
| 1. Local secret guard | Before every commit | Keys, tokens, passwords in the changes; the commit is blocked if found | gitleaks via the git hook (everyone), plus agent-tool hooks where supported |
| 2. Self-check | Before opening a PR | Tests pass; security self-review of its own diff | The agent that built it |
| 3. Automated CI | Every PR update | Tests, lint, types (`ci`); secrets in every commit (`secrets`); vulnerable libraries (`dependencies`) | GitHub Actions |
| 4. Independent AI review | Every PR update (not drafts or docs-only) | Meets the spec? Tests honest? Bugs, scope creep, rule breaches (`ai-review`). Security vulnerabilities (`security-review`) | A separate Claude in GitHub Actions that never saw the code being written (cross-model when the code came from another tool) |
| 5. Human code review | PRs touching protected areas | Core logic, auth, payments, personal data, migrations, infrastructure, agent config | Product owner or a designated developer |
| 6. Human acceptance | Every code PR | It actually works (Gate G4 UAT) | Product owner |

- The reviewer posts one comment with **Blocking / Should fix / Nits**. Blocking findings stop the merge.
- The building agent fixes Blocking items and pushes; reviews re-run automatically. If it disagrees, it replies on the PR and asks a human. After **two** failed rounds it stops and hands over.
- AI reviewers can block but never approve or merge. Only a human can overrule them, with the PR label `ai-review-overruled`.
- If a real secret ever reaches GitHub: revoke and rotate it immediately, then have an admin rewrite the branch history. Deleting it in a new commit is not enough.

Full rules: `docs/process/GATES.md`. Reviewer instructions you can tune: `.github/review/REVIEWER.md`.

---

## Before you start

You need:
- [ ] Admin access to the GitHub repository (and a paid plan if the repo is private and you want rulesets and deploy approvals enforced; see Phase 4)
- [ ] A tracker: **GitHub Projects** (nothing extra; free on every plan) or admin access to a **Linear** workspace
- [ ] A coding agent installed and signed in, in your own account
- [ ] Python 3, Git, Make, and the GitHub CLI signed in (`gh auth login`)
- [ ] gitleaks (`brew install gitleaks`, or from its GitHub releases page)
- [ ] An Anthropic API key for the reviewer agents (console.anthropic.com), with a monthly spend limit
- [ ] Your project runs locally today

Decide now:
1. **Tracker:** GitHub Projects (free, everything in GitHub) or Linear (nicer to use, free plan limited). You can switch later.
2. **Product key:** a short code, e.g. `ACM`, `SHOP`, `CRM` (the Linear team key if you use Linear). The kit uses `APP` as a placeholder until `config` replaces it everywhere.
3. **Product owner:** the one person who approves ideas, specs, UAT and deploys (plus an optional backup approver).
4. **Agent tools** your team will use.

Check your machine any time with: `python3 <kit>/tools/haam/haam.py dev`

---

## Phase 1: Install the kit (15 min)

```bash
cd your-project
git switch main && git pull && git switch -c chore/adopt-haam
python3 <path-to-kit>/tools/haam/haam.py install --target . --dry-run   # see what will happen
python3 <path-to-kit>/tools/haam/haam.py install --target .
```

The installer **never overwrites** your files:
- New files are added.
- `.mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json` and `.claude/settings.json` are **merged** automatically.
- `.gitignore` gets a HAAM block appended once.
- Any other file you already have is left alone, and the kit's version is saved to `.haam/incoming/` for you (or the agent) to merge.

How to merge the usual conflicts:

| If your repo already has… | Do this |
|---|---|
| `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.cursor/rules/`, `GEMINI.md` | Move project-specific knowledge (conventions, gotchas, commands) into `docs/product/ARCHITECTURE.md` or a "Project specifics" section at the end of `AGENTS.md`. Then use the kit's `AGENTS.md` and `CLAUDE.md`. Keep Cursor `.mdc` rules only for glob-scoped details |
| `.claude/skills/`, `.claude/commands/` | `haam.py agents --apply` moves your skills into `.agents/skills/` and links the folder. Rename any that clash with HAAM skill names first |
| `Makefile` | Add the kit's targets to yours |
| `.github/workflows/` with CI | Keep your CI, but make sure a job named **`ci`** runs your full test suite on PRs. Add `gates.yml`, `security.yml`, `review.yml`. Compare your deploy with `deploy.yml` (Phase 4) |
| `.github/pull_request_template.md` | Merge in "Built with", "Acceptance criteria → tests" and "Checklist (G3)" |
| `.pre-commit-config.yaml` or Husky | Keep it and call `scripts/scan-secrets.sh` from it instead of using `.githooks/` |
| `CHANGELOG.md`, `.github/dependabot.yml` | Keep yours (add the `github-actions` ecosystem to Dependabot if missing) |

Delete `.haam/incoming/` when done.

---

## Phase 2: Configure and teach it your project (45 min)

1. **Project settings** `[agent]` (answers from you):
   ```bash
   python3 tools/haam/haam.py config --product "Acme" --tracker github --team-key ACM --linear-team "Acme" \
     --github-repo owner/repo --owner your-github-user --production-url https://… \
     --agents claude,cursor,codex,grok
   ```
   This writes `haam.config.json` and replaces the `APP` placeholder and product name in every HAAM file.

2. **Agent tools** `[agent]`: `python3 tools/haam/haam.py agents --apply`. This links the shared skills for Claude Code and Grok, checks Cursor/Codex/Gemini/Copilot files, and lists any per-person steps. Details: `docs/setup/AGENTS-SETUP.md`.

3. **Command contract** `[agent]`: fill every `TODO(setup)` in `Makefile` (setup, dev, test, lint, typecheck, build, audit) and the runtime steps in the workflows, from your project's real commands. Then `make check` must pass on current code. If tests already fail on `main`, fix or mark them first: HAAM relies on green meaning green. If `make audit` reports old high/critical vulnerabilities, fix them or log them as bugs and raise the threshold temporarily.

4. **Architecture map** `[agent]`: fill `docs/product/ARCHITECTURE.md` from the codebase (under 150 lines) and propose real paths for the protected areas in `AGENTS.md` §4. You review.

5. **Product context** `[agent drafts, you confirm]`: `docs/product/PRODUCT.md`: what it is, users, journeys that must never break, non-negotiables, current priorities. This is what every agent reads to make judgement calls.

6. **Onboarding doc** `[agent]`: fill the `TODO(setup)` items in `docs/ONBOARDING.md` (clone URL, runtime, local URL).

7. **Secrets hygiene** `[agent]`: `make hooks`, then scan history once: `gitleaks git --redact -v .` Anything real must be **revoked and rotated** with the provider: it's already exposed to anyone with repo access. You approve any false-positive fingerprints added to `.gitleaksignore`.

8. **Parallel chats** `[agent]`: list the local-only files the app needs (like `.env`) in `.worktreeinclude`, exclude `.claude/worktrees/` from any tool that scans the whole folder (test runner, linter, watcher), and try a fresh worktree: `python3 tools/haam/haam.py worktree new setup-check`, then `make setup && make check` in it, then `git worktree remove .claude/worktrees/setup-check`. From then on, every new agent chat starts with `/work`.

9. **Check:** `python3 tools/haam/haam.py doctor` shows what's left.

---

## Phase 3: Open the adoption PR (5 min)

```bash
git add -A
git commit -m "Adopt the Human-Agent Agile Methodology (HAAM)"
git push -u origin chore/adopt-haam
gh pr create --fill
```
This makes the checks exist in GitHub so they can be required. The first AI review comment will appear on this PR.

---

## Phase 4: GitHub gates (20 min)

1. **Plan, then apply** `[agent, with your OK]`:
   ```bash
   python3 tools/haam/haam.py github           # shows the plan
   python3 tools/haam/haam.py github --apply   # after you agree
   ```
   It creates the labels, a ruleset on the default branch (PR required, the six required checks, no force pushes, admins can bypass for emergencies), the `production` environment with your approvers, the `PRODUCTION_URL` variable, and turns on secret scanning, push protection and Dependabot where your plan allows.
2. **Reviewer key** `[YOU, in your terminal]`: `gh secret set ANTHROPIC_API_KEY -R owner/repo` (it asks for the key without showing it).
3. **Fork PRs** `[YOU, in the browser]`: Settings → Actions → General → require approval for outside collaborators.
4. **Deploys:**
   - *Already deploying from GitHub Actions?* Add `environment: production` to your deploy job: that alone gives you Gate G5. Delete the kit's `deploy.yml` or keep it as reference.
   - *Deploying another way* (a hosting platform's Git integration, manual)? Either move deploys into `deploy.yml` (fill in `make deploy`) or keep your method and treat G5 as a manual step: the product owner deploys after merge, then runs `/release`. Turn off auto-deploy-on-push if it would bypass the approval.
5. **Private repos on the free plan** can't enforce rulesets or deploy approvals; the tool tells you if so. Options: upgrade, or rely on the checks plus discipline until you do.

Detail and manual equivalents: `docs/setup/GITHUB-SETUP.md`.

---

## Phase 5: The tracker (20 min)

### Option A: GitHub Projects (free)
1. `[YOU, in your terminal]` `gh auth refresh -s project` (lets your GitHub login use Projects).
2. `[agent, with your OK]`
   ```bash
   python3 tools/haam/haam.py github-project           # plan
   python3 tools/haam/haam.py github-project --apply   # creates the board, links the repo, 12 statuses, Priority, labels
   ```
3. `[YOU, in your terminal]` automation token, so cards move when PRs open and merge: create a classic token at github.com/settings/tokens with the `project` scope (plus `repo` if the repository is private), then `gh secret set HAAM_PROJECT_TOKEN -R owner/repo`.
4. `[YOU, in the browser]` on the board, create the views the tool lists: Board grouped by Status, **Agent queue**, **Waiting on me**, **Ideas inbox**, **Bugs**.
5. Test: `python3 tools/haam/haam.py issue list`.

Agents use `python3 tools/haam/haam.py issue …` for every board operation (`docs/process/TRACKER.md`), so it works the same from Claude Code, Cursor, Codex, Grok or anything else.

### Option B: Linear
1. **Statuses, labels, team** `[YOU, in your terminal]` (needs your Linear personal API key, which never goes through an agent):
   ```bash
   python3 tools/haam/haam.py linear           # plan; asks for the key securely
   python3 tools/haam/haam.py linear --apply
   ```
   It creates the team if needed, turns on Triage, creates the 12 statuses (renaming Linear's default "Todo" to "Ready"), and the 9 labels. It never deletes anything; it lists extra statuses for you to archive.
2. **Browser-only settings** `[YOU, in the browser]`: connect GitHub, PR automations (PR opened → In Review, merged → Deploying), branch name format `{issue-identifier}-{issue-title}`, saved views. See `docs/setup/LINEAR-SETUP.md`.
3. **Connect your agent** to Linear (`docs/setup/AGENTS-SETUP.md`) and test: *"List the issues in Linear team ACM."*

**Existing backlog?** Ask your agent to bring it into the tracker (GitHub issues can simply be added to the board). Put everything in **Triage**, triage once (`stream:bug`, `stream:idea`, or `stream:feature` + Backlog), and spec only the top five.

---

## Phase 6: Merge, trial loop, and people

### Merge the adoption PR
When the checks are green, add `uat-passed` yourself (the gate is live now, so even this PR goes through it) and merge. If the reviewer agents nitpick the kit itself, overrule with `ai-review-overruled`. Run `python3 tools/haam/haam.py doctor --role admin` for a final check.

### Run one full loop (45–60 min)
Pick something small and real. Walk it through every stage once:

| Step | You type | What should happen |
|---|---|---|
| 1 | `/idea Add a "last updated" date to the dashboard` | New issue in Triage, label `stream:idea` (on GitHub: `#1`; on Linear: `ACM-1`) |
| 2 | `/assess #1` | Assessment doc in a docs PR; issue moves to Decision |
| 3 | `/decide #1 approve medium` | Issue moves to Backlog, label becomes `stream:feature` |
| 4 | `/spec #1` | Spec doc in a docs PR with acceptance criteria |
| 5 | Review the spec, merge the docs PR, tell the agent "spec approved" | Issue gets `agent-ready`, moves to Ready |
| 6 | `/build #1` | Claims it, branches, codes, writes tests, self-reviews, opens PR; the tracker shows In Review |
| 6b | (automatic) | `ci`, `secrets`, `dependencies` run; the reviewer agent comments; the building agent fixes Blocking findings |
| 7 | (when all green) `/uat #1` | UAT plan committed; issue moves to UAT; you're notified |
| 8 | `/test #1` | The agent puts the change on your machine, starts the app and gives you a short checklist |
| 9 | Try it, reply `pass` | PR gets `uat-passed`; `release-gate` turns green; the agent asks "Ship it?" |
| 10 | Reply `ship` | The agent merges, approves the production deploy for you, waits, and closes the issue: Done |
| 11 | (try once) `/test` on a change and describe a problem instead | It goes back to the agents with your notes (`uat-failed`) and returns to you when fixed |

(On Linear the IDs look like `ACM-1`.)

Then try the edges once: ask the agent to commit a fake key on a throwaway branch (`AKIA` + 16 capital letters/digits): the commit must be blocked. Then fail a UAT, and use an override. Tune the skills in `.agents/skills/` or the process in `docs/process/LIFECYCLE.md` where something felt wrong.

**Try a second agent tool on the trial loop too** (e.g. Cursor or Codex for step 6). That confirms the shared rules and skills work beyond your main tool.

### Adding developers
1. `[agent, with your OK]` `python3 tools/haam/haam.py invite --github THEIR_USER --linear-email THEM@… --apply`: GitHub write access (not admin), access to the GitHub Projects board, or a Linear invitation.
2. Send them the repo link and test credentials (password manager or one-time link, never chat or email).
3. They open their own agent in the repo and run `/haam-onboard` (Codex: `$haam-onboard`).
4. Once there are two of you: the tool sets "1 approval required" when you add backup approvers (`config --backup-approvers`, then `github --apply`), and you can add `.github/CODEOWNERS` for protected areas.

### Letting agents work semi-autonomously

| Level | How | When |
|---|---|---|
| **1. Supervised** | You type `/next` or `/build`, approve each push and PR | First 2–3 weeks |
| **2. Batched** | 2–3 chat windows (any mix of tools and computers), each started with `/work`, which gives it its own worktree; you review PRs in a batch | Once specs are reliably good |
| **3. Scheduled** | A scheduled task runs an agent headless with `/next` and stops at UAT | Once you trust the gates |

At every level, agents stop at the human gates.

### Running costs
Besides GitHub, Linear (if you use it) and each person's agent subscription, the only usage-based cost is the reviewer agents: two Claude calls per reviewed PR push, billed to `ANTHROPIC_API_KEY`. Keep the spend limit on and PRs small.

### Staying up to date
New kit versions are published at https://github.com/jorgedpl/haam-kit/releases. `python3 tools/haam/haam.py doctor --check-updates` tells you when one is out. Run `/haam-update` (Codex: `$haam-update`) on a branch: files you never changed are updated, your customisations are kept, and where both changed the agent merges them. The CHANGELOG lists any migration steps.

### Your rhythm as product owner
Daily (10–15 min): test **UAT**, empty **Triage** (`/triage`). Weekly (30–45 min): decide everything in **Decision**, re-rank the backlog (`/triage backlog`), chase stuck work (`/triage stale`), revisit **Parked**, close **Overrides**. The full guide, with priority rules and checklists: `docs/process/PRODUCT-MANAGER.md`.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Not sure what's left | – | `python3 tools/haam/haam.py doctor --role admin` |
| Agent doesn't follow the rules | Tool not reading `AGENTS.md` | First-run check in `docs/setup/AGENTS-SETUP.md` |
| `haam.py issue` says the login can't use Projects | gh login lacks the `project` scope | `gh auth refresh -s project` |
| Board cards don't move when PRs open/merge | `HAAM_PROJECT_TOKEN` missing, or the PR doesn't say `Refs #123` | Add the secret (Phase 5); check the PR description |
| Agent doesn't see Linear | MCP not connected or not signed in | Per-tool steps in `docs/setup/AGENTS-SETUP.md` |
| Skills show twice in Cursor | Cursor reads both `.agents/skills` and `.claude/skills` | Turn off Claude-skills compatibility in Cursor's settings |
| `.claude/skills` or `.grok/skills` missing after clone (Windows) | Git symlinks off | `git config core.symlinks true` and re-clone, or `haam.py agents --apply` (copies instead) |
| `haam.py github` says rulesets/approvals unavailable | Private repo on a free plan | Upgrade, or protect manually and rely on the checks |
| `haam.py linear` errors on a step | API change or permissions | Finish that step by hand with `docs/setup/LINEAR-SETUP.md` |
| Two chats changed the same files or branch | They shared one folder | Start every agent chat with `/work` (own worktree) |
| Tests or linter find duplicate files under `.claude/worktrees/` | The tool scans the whole folder | Exclude `.claude/worktrees/` in that tool's config |
| A worktree can't run the app | Local files missing | Add them to `.worktreeinclude`, then `haam.py worktree prep` in the worktree |
| `/build` refuses to start | Issue not in Ready, or missing `agent-ready` | `/spec` and approve it, or move the issue to Ready yourself |
| Linear statuses don't move on PR events | GitHub integration or automations not set | Team settings → Workflow → PR automations; PR title must start with the issue ID |
| `release-gate` stays red after `uat-passed` | Workflow didn't re-run | Remove and re-add the label |
| A required check is missing from the list | It hasn't run yet | Open any PR first |
| Commits blocked: "gitleaks is not installed" | gitleaks missing on that machine | Install it, then `make hooks` |
| Commit blocked for a secret that isn't one | False positive | A human adds the fingerprint to `.gitleaksignore` in a reviewed commit |
| `ai-review` pending or erroring | Missing `ANTHROPIC_API_KEY`, fork PR, or ran out of turns | Add the secret; re-run; raise `--max-turns`; or `ai-review-overruled` |
| Reviewer too strict | Instructions not tuned | Edit `.github/review/REVIEWER.md` |
| `dependencies` fails on every PR | Old vulnerabilities | Fix, or raise the threshold temporarily and track as bugs |
| Specs too vague, builds go wrong | G2 too loose | Tighten the Definition of Ready in `docs/process/GATES.md` |

---

## Principles

1. **Humans decide, agents execute.**
2. **If it isn't in Git or the tracker, it doesn't exist** for the next person or agent.
3. **Small slices:** one issue, one branch, one PR, reviewable in 15 minutes.
4. **Gates are cheap to pass and expensive to skip.** Overrides are allowed, always recorded, always followed up.
5. **Green means green.** Never weaken a test to pass a gate.
6. **No one marks their own homework.** The agent that writes code never reviews it; secrets are caught by tools, not by judgement.
7. **Any agent, same rules.** Tools are interchangeable; the process and the gates are not.
