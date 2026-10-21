# HAAM: Human-Agent Agile Methodology

**Humans decide. Agents execute. Everything lives in Git and your tracker.**

HAAM is an open methodology and kit for building software with AI coding agents, from idea to production, without losing control. It gives every agent the same rules, the same commands and the same gates, whatever tool it runs in: **Claude Code, Cursor, Codex, Grok Build, Gemini CLI or GitHub Copilot**. Work is tracked on a **GitHub Projects** board (free) or in **Linear**, your choice. Several people, each with their own agent and account, can work on the same product in parallel.

```
Idea ─► Assess ─► [G1 Decide] ─► Spec ─► [G2 Ready] ─► Build + unit tests ─► [G3 CI + secret scan + AI review]
     ─► UAT plan ─► [G4 Human tests locally] ─► Merge ─► [G5 Approve deploy] ─► Production ─► Done
```

## What you get

- **A lifecycle with five human gates**: decide the idea, approve the spec, automated checks with independent AI review, human acceptance test, production approval. Every gate can be overridden in an emergency, and every override is recorded and followed up.
- **Three work streams** agents pull from: bugs, ready features, and ideas to assess. The tracker (GitHub Projects or Linear) holds the backlog, priorities and status.
- **19 shared skills** (`/idea`, `/bug`, `/assess`, `/triage`, `/epic`, `/decide`, `/spec`, `/work`, `/next`, `/build`, `/uat`, `/test`, `/uat-result`, `/override`, `/release`, `/haam-setup`, `/haam-onboard`, `/haam-update`, `/haam-settings`), in the open Agent Skills format.
- **Your settings, your trade-offs:** `/haam-settings` lets the product owner choose when CI and the AI reviews run (every PR, locally, only for protected areas, or off), what they test themselves, how work is grouped (per issue, per epic, or one release PR), whether deploys wait for approval, and the limits, each with its trade-off and the project's own numbers.
- **Testing in one word, before anything costs CI minutes**: type `/test`, try the agent's change on your computer, reply `pass` (only now is the pull request opened and checked, once, on exactly what you tested) then `ship` (the agent merges, deploys and closes it), or just say what's wrong (it goes straight back to the agents and returns to you when fixed). `/test all` takes everything waiting in one sitting, and `ship --all` deploys it with one approval.
- **A no-UAT lane** for changes you can't meaningfully test (config, dependency bumps, invisible refactors): mark the issue `uat:skip` once, and its PR merges by itself when CI and both AI reviews pass.
- **Epics with an agent that asks the right questions**: `/triage group` turns a pile of loose issues into epics (one per feature); `/epic` reads each one, writes a short brief, asks you a few focused questions, then tidies the issues: duplicates, gaps, splits, order.
- **A decisions guide** ([DECISIONS.md](template/docs/setup/DECISIONS.md)): every choice a team makes when it adopts HAAM, with a recommendation for each. It covers GitHub accounts and the plan you need, GitHub Projects or Linear, the settings, how to size the limits for your testing time, and what to protect. `/haam-setup` walks you through it.
- **A guide for the product manager** ([PRODUCT-MANAGER.md](template/docs/process/PRODUCT-MANAGER.md)): daily and weekly rhythm, how to triage, priority rules with a bug impact × reach matrix, healthy queue sizes, done with an agent (`/triage`) or directly in GitHub Projects or Linear.
- **Parallel agents without collisions**: open a new chat window, type `/work bugs`, and the agent gets its own copy of the project (a git worktree), picks the top bug and works it through to your test. Run as many as you like, on one computer or several.
- **Code review where no one marks their own homework**: a secret scan before every commit and in CI, dependency audit, and two independent AI reviewers (spec/quality and security) that never saw the code being written. Humans review protected areas and can overrule.
- **Gates enforced by GitHub**, not by trust: branch rules, required checks, a UAT label gate and deploy approvals, so they hold whatever agent or person is pushing.
- **A setup tool** (`haam.py`, Python 3, no dependencies) that installs the kit into an existing repo without overwriting anything, configures GitHub and the tracker (GitHub Projects or Linear), gives agents one command set for the board, onboards developers, checks the setup and upgrades projects to new kit versions.

## Quick start

### Adopt HAAM in your project (project admin, about half a day)

1. Get a released version of the kit:
   ```bash
   git clone --depth 1 --branch v1.14.0 https://github.com/jorgedpl/haam-kit.git ~/haam-kit
   ```
   (or download the zip from [Releases](https://github.com/jorgedpl/haam-kit/releases)).
2. Open your coding agent **in your project's root folder** and say:
   > Read `~/haam-kit/template/.agents/skills/haam-setup/SKILL.md` and follow it to set up HAAM in this repository. The kit is at `~/haam-kit/template`.

The agent installs the kit on a branch, asks you a few questions, fills in project knowledge from your code, and walks you through GitHub and your tracker. It shows every change before making it. Anything involving a password or API key is done by you, in your own terminal, never through the agent's chat.

Prefer doing it by hand? Follow [the adoption guide](template/docs/setup/HAAM-ADOPTION-GUIDE.md).

### Join a project that already uses HAAM (developer, about an hour)

Clone the project, open your agent in it, and run `/haam-onboard` (Codex: `$haam-onboard`; other tools: *"follow `.agents/skills/haam-onboard/SKILL.md`"*).

### Upgrade a project to a new kit version

Get the new version of the kit, then in your project run `/haam-update`, or:
```bash
python3 ~/haam-kit/template/tools/haam/haam.py update --target .            # plan
python3 ~/haam-kit/template/tools/haam/haam.py update --target . --apply    # on a branch
```
Files you never changed are updated; files you customised are kept, and where both sides changed, the new version is set aside for your agent to merge. Nothing is deleted.

## The setup tool

| Command | Who | What |
|---|---|---|
| `install --target DIR` | admin | Copy the kit into a repo. Never overwrites; merges agent settings files; parks conflicts in `.haam/incoming/`; records the version in `haam.lock.json` |
| `update --target DIR [--apply]` | admin | Upgrade a project to this kit version, keeping customisations |
| `config` | admin | Product name, Linear team key, repo, approvers → `haam.config.json`; applies them to every HAAM file |
| `agents [--apply]` | admin | Wire up skills and Linear for Claude Code, Cursor, Codex, Grok, Gemini, Copilot |
| `github [--apply]` | admin | Labels, branch ruleset with required checks, production approval, security features |
| `github-project [--apply]` | admin | GitHub Projects board: 12 statuses, Priority field, labels, repo link |
| `linear [--apply]` | admin, in own terminal | Linear team, triage, 12 statuses, 9 labels |
| `issue list\|create\|claim\|release\|status\|fields\|…` | agents | Work the GitHub Projects board from any agent tool |
| `exclusive "<who>" -- <command>` | agents | Run a heavy test run (one that uses a machine-wide resource) when no other one is running on this machine |
| `capacity` | agents | Hold new work when too many PRs are open or waiting for your test (limits in `haam.config.json`) |
| `ci-usage [--days 7]` | admin | Where the GitHub Actions minutes went, by workflow, job, trigger and day |
| `settings [--explain] [--set key=value] [--apply]` | owner/admin | Your choices: when CI and the AI reviews run, what you test, grouping, shipping, limits (`/haam-settings` walks you through them) |
| `local-ci ISSUE` | owner | With `ci: local`: run `make check` on the PR's commit here and post it (ship does it for you) |
| `review ISSUE` | agents | The two AI reviews in fresh local sessions, posted as the PR's statuses (when reviews are local) |
| `checkout-pr ISSUE`, `publish ISSUE --human`, `ship ISSUE... \| --all --human` | `/test` | Put a change on this machine to test; after `pass` + `ship`: merge, approve the deploy (one for several), wait, close |
| `worktree status\|new\|prep\|list\|clean` | agents, anyone | One worktree per agent chat; copies local files from `.worktreeinclude`; tidies finished ones |
| `invite --github USER [--linear-email EMAIL] [--apply]` | admin | Invite a developer (GitHub write, not admin; board access or Linear team) |
| `dev [--apply] [--run-checks]` | developer | Machine check, commit hook, `.env` from example, project checks |
| `doctor [--role admin] [--check-updates]` | anyone | What's done, what's missing, and who must do it |
| `version [--check]` | anyone | Tool, project and latest released kit versions |

Every command shows a plan first and changes things only with `--apply`. Add `--json` for machine-readable output.

## Running several agents at once

Each agent chat gets its own folder, so chats never overwrite each other's work:

1. Open a new chat window (Claude Code in VS Code: Cmd/Ctrl+Shift+Esc).
2. Type `/work bugs` (or `/work features`, `/work specs`, `/work ideas`, or just `/work`; Codex: `$work`).
3. The agent moves into its own git worktree, copies local files like `.env`, claims the top item on the board, builds and tests it, opens the PR and hands you a test plan.

Repeat for as many agents as you want, on any computer with the project cloned. The claim on the board stops two agents taking the same issue, whether to build it, assess it or write its spec. Your own chat stays in the main folder for ideas, decisions, testing and releases.

## Choosing a tracker

| | GitHub Projects | Linear |
|---|---|---|
| Cost | Free on every GitHub plan | Free plan with limits; paid per user |
| Where | Next to your code, one login | Separate app |
| Agents use | `haam.py issue …` (any agent) | Linear's MCP server |
| Best for | Solo and small teams, keeping everything in GitHub | Busier backlogs, several teams, richer planning |

Same lifecycle, gates and skills either way, and you can switch later. See [TRACKER.md](template/docs/process/TRACKER.md).

## Agent compatibility

| | Rules | Skills | Calling a skill | Linear (if used) |
|---|---|---|---|---|
| Claude Code | `CLAUDE.md` → `AGENTS.md` | `.claude/skills` → `.agents/skills` | `/build` | `.mcp.json` |
| Cursor | `AGENTS.md` | `.agents/skills` | `/build` | `.cursor/mcp.json` |
| Codex | `AGENTS.md` | `.agents/skills` | `$build` | `codex mcp add` |
| Grok Build | check on first run | `.grok/skills` → `.agents/skills` | `/build` | `.mcp.json` |
| Gemini CLI | `AGENTS.md` via `.gemini/settings.json` | by file | by file | per user |
| GitHub Copilot | `AGENTS.md` | by file | by file | per user |

On GitHub Projects every agent uses the same `haam.py issue` commands, so there's nothing per tool to connect. Details and recommended safe settings per tool: [AGENTS-SETUP.md](template/docs/setup/AGENTS-SETUP.md).

## Requirements

- A GitHub repository. Public repositories get everything on the free plan. On **private** ones, the branch rules need GitHub Pro or Team, and a required approver on production deploys needs GitHub Enterprise Cloud (without it, your `ship` is the release decision). [DECISIONS.md](template/docs/setup/DECISIONS.md) has the details.
- A tracker: a GitHub Projects board (free, on any GitHub plan) or a Linear workspace (any plan)
- Python 3.8+, Git, Make, GitHub CLI, [gitleaks](https://github.com/gitleaks/gitleaks)
- A Claude secret for the CI reviewer agents: a Claude plan token (`claude setup-token`) or an Anthropic API key (usage-based; set a spend limit)
- Any supported coding agent

## Repository layout

```
template/        Everything that gets installed into a project (the kit)
  AGENTS.md      Rules for every agent
  .agents/skills Shared skills
  tools/haam/    The setup tool
  docs/          Methodology, gates, setup guides, templates
  .github/       CI, security, AI review, UAT gate, deploy workflows
tests/           Tests for the setup tool
install.sh       Optional bootstrap: fetch a released version and run the tool
CHANGELOG.md     Kit release notes and migration steps
```

## Versioning

HAAM follows [semantic versioning](https://semver.org):
- **Patch** (1.0.x): fixes and wording; `update` applies cleanly.
- **Minor** (1.x.0): new skills, checks or docs; backwards compatible.
- **Major** (x.0.0): changes that need a migration step (e.g. renamed Linear statuses or required checks). The [CHANGELOG](CHANGELOG.md) lists the steps.

Always install from a tag or release, not from `main`.

## Contributing

Ideas, bug reports and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Security issues: see [SECURITY.md](SECURITY.md).

## Licence

[MIT](LICENSE) © 2026 Jorge del Prado
