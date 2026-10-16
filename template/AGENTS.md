# AGENTS.md: rules for every agent working in this repo

This project follows the **Human-Agent Agile Methodology (HAAM)**: humans decide, agents execute, and everything lives in Git and the tracker. You are working on **`TODO(setup): product name`**.

These rules apply to **every** coding agent (Claude Code, Cursor, Codex, Grok, Copilot, Gemini…) and to humans. Read this whole file at the start of every session, then read these two files before doing any work:
- `docs/product/PRODUCT.md`: what the product is and what matters now
- `docs/product/ARCHITECTURE.md`: map of the codebase

Full methodology: `docs/process/LIFECYCLE.md` · Gates and overrides: `docs/process/GATES.md` · Tracker how-to: `docs/process/TRACKER.md`

---

## 1. How we work (summary)

We run a product lifecycle with three work streams and five gates.

- **Streams:** `stream:idea` (new ideas), `stream:feature` (approved work), `stream:bug` (issues).
- **Tracker:** `haam.config.json` → `"tracker"` is `github` (GitHub Projects board) or `linear`. Every tracker operation (find, create, claim, move, comment) is in `docs/process/TRACKER.md`; check which tracker once per session and use that column.
- **Statuses:** Triage → Discovery → Decision → Backlog → Ready → In Progress → In Review → UAT → Deploying → Done (plus Parked, Canceled).
- **Gates:** G1 Decision (human) · G2 Ready (human approves spec) · G3 automated checks + independent AI review (+ human for protected areas) · G4 UAT (human, local) · G5 production approval (human).
- **Issue IDs:** `#123` on GitHub Projects, `APP-123` on Linear (`TODO(setup)`: replace with your team key everywhere). Skills write `<ID>` for either.

Every piece of work has an issue in the tracker. If you are asked to do something with no issue, create one first with `/idea` or `/bug` (ask the human which, if unclear).

## 2. Skills (commands) for each stage

Skills live in `.agents/skills/<name>/SKILL.md` (the shared Agent Skills format). How to call one depends on the tool: `/build <ID>` in Claude Code, Cursor and Grok; `$build <ID>` in Codex. If your tool doesn't load skills, open the skill's `SKILL.md` and follow it step by step. Wherever a skill says `$ARGUMENTS`, use the text the human typed after the command.

| Stage | Skill | Who runs it |
|---|---|---|
| Capture an idea | `/idea <text>` | anyone |
| Report a bug | `/bug <text>` | anyone |
| Assess an idea + feasibility | `/assess <ID>` | agent |
| Record a decision (G1) | `/decide <ID> approve\|park\|reject` | **human only** |
| Write the spec | `/spec <ID>` | agent |
| Start an agent in a new chat window | `/work [bugs\|features\|ideas]` | anyone |
| Pick the next work item | `/next` | agent |
| Build a ready issue | `/build <ID>` | agent |
| Prepare UAT | `/uat <ID>` | agent |
| Record UAT result (G4) | `/uat-result <ID> pass\|fail` | **human only** |
| Override a gate | `/override <ID> "<reason>"` | **human only** |
| Close after deploy (G5) | `/release <ID>` | **human only** |
| Adopt HAAM in a repo | `/haam-setup` | **human only** (project admin) |
| Onboard a developer | `/haam-onboard` | **human only** (new developer) |
| Upgrade HAAM to a new version | `/haam-update` | **human only** (project admin) |

Each skill's `SKILL.md` has the exact steps. Follow them; don't improvise a different process.

The setup skills drive `tools/haam/haam.py`; run `python3 tools/haam/haam.py doctor` any time to see what's missing.

## 3. Hard rules: never break these

1. **Never push to `main`, never merge a PR, never deploy, never run production commands.** Humans do that.
2. **Never add the PR labels `uat-passed`, `gate-override` or `ai-review-overruled`**, and never move an issue to Done, Backlog (from Decision), Parked or Canceled. Those are human decisions. The only exception is when a human has typed `/decide`, `/uat-result`, `/override` or `/release` in this session; then you carry out exactly what that skill says.
3. **Only build issues that are in `Ready` and have the `agent-ready` label** (bugs: `Ready` is enough). If something isn't ready, help make it ready (`/spec`) instead of building it.
4. **Claim before you build** (see §6). Never work on an issue someone else has claimed.
5. **Never put secrets or real personal data** (names, emails, dates of birth, addresses, document numbers of real people) in code, tests, fixtures, logs, commits, the tracker or docs. Use the synthetic fixtures in the test folder.
6. **Never read or print `.env*` files or production credentials.** If you need a config value, ask.
7. **Stay in scope.** Implement the acceptance criteria, nothing else. Note other problems you spot as new `/bug` or `/idea` issues instead of fixing them in the same PR.
8. **Don't fake green.** Never skip, delete or weaken a test to make CI pass. If a test is wrong, say so in the PR and on the issue.
9. **Ask when the spec is ambiguous.** Post the question as a comment on the issue and in chat, and stop. Don't guess on behaviour that affects core business outcomes, data handling or money.
10. **Never bypass the secret guards.** No `--no-verify`, no editing `.gitleaksignore`, `.gitleaks.toml`, the hooks or the scan script. If a commit is blocked for a possible secret, remove it and tell the human. If a real secret was ever committed or pushed, stop and tell the human immediately so it can be rotated.

## 4. Protected areas: human review required

Changes touching any of these get the `human-review` label and need a human code review at G3, even if CI is green:

- Core business logic where a wrong result harms users (e.g. pricing, eligibility, verification or approval decisions)
- Integrations with external providers that act on users' behalf or exchange personal data
- Authentication, sessions, permissions, roles
- Storage, retention or deletion of personal data; logging that could capture personal data
- Payments, billing, refunds
- Database migrations
- CI/CD, deploy config, infrastructure
- Agent configuration: this file, `CLAUDE.md`, `.agents/`, `.claude/`, `.cursor/`, `.codex/`, `.grok/`, `.gemini/`, `tools/haam/`, `.github/review/`

`TODO(setup): replace the examples above with the real module paths once ARCHITECTURE.md is filled in.`

## 5. Code review: how your PR gets checked

You never review your own work, and you never decide that a review is wrong on your own.
- Before opening a PR: `make check`, then do a security self-review of your diff and fix what it finds (Claude Code: `/security-review`; other tools: review `git diff origin/main...` against section D of `.github/review/REVIEWER.md`).
- After opening: `secrets`, `dependencies`, `ai-review` and `security-review` run automatically. The reviewer agent posts a comment with **Blocking / Should fix / Nits**.
- Fix every Blocking item and push. Should-fix items: fix if small and in scope, otherwise log a `/bug`. Ignore nits unless trivial.
- If you disagree with a finding, reply on the PR with your reasoning and ask the human. Never push changes just to game the reviewer.
- After **two** failing review rounds, stop and hand over to the human (issue comment + chat).

## 6. Working with the tracker

The tracker is either a GitHub Projects board (`"tracker": "github"`) or Linear (`"tracker": "linear"`). How to do each operation in each one: `docs/process/TRACKER.md`.
- **GitHub Projects:** use `python3 tools/haam/haam.py issue …` (works from any agent tool; uses your `gh` login).
- **Linear:** use the Linear connection (MCP, `https://mcp.linear.app/mcp`; per-tool setup in `docs/setup/AGENTS-SETUP.md`).

You act as the human who is running this session. If you can't reach the tracker, stop and tell the human; don't track work anywhere else.

**Claim protocol (before any code change):**
1. Re-fetch the issue. If it's `In Progress` or assigned to someone else, stop and pick another.
2. Assign it to the current user, set status `In Progress`.
3. Comment: `🤖 Claimed by <user> via <agent tool> [on <machine>] · branch <branch-name>`.
On GitHub Projects, `haam.py issue claim <number> --tool "<tool>" --machine "<machine>"` does all three and refuses if someone got there first.

**While working:** keep the issue updated with short comments at meaningful points (plan posted, PR opened, blocked, handover). Not a running commentary.

**If you stop before finishing:** push the branch, open/update a **draft** PR, and post a handover comment: *Done / Not done / Next step / Gotchas*.

## 7. Working with Git

- Branch from fresh `main`. Branch, commit and PR naming per tracker (`docs/process/TRACKER.md`):

  | | GitHub Projects | Linear |
  |---|---|---|
  | Branch | `123-short-title` | `app-123-short-title` |
  | Commit | `#123: <imperative summary>` | `APP-123: <imperative summary>` |
  | PR title | `#123: <summary>` | `APP-123: <summary>` |
  | PR description | must include `Refs #123` | (title links it) |

- Spikes use `spike/<branch-name>` and are never merged.
- Fill in `.github/pull_request_template.md` completely, including **Built with** (your agent tool and model).
- Rebase on `main` before opening or updating a PR. Keep PRs small (target < 400 changed lines).
- **One chat, one folder.** Chats that share a folder overwrite each other's files and branches. When more than one agent chat may be open on a machine, each agent chat that changes files works in its own git worktree under `.claude/worktrees/`; `/work` sets one up (`python3 tools/haam/haam.py worktree status|new|prep|clean`). The main folder belongs to the human's chat. When unsure, use a worktree.

## 8. Commands (the contract between agents, CI and humans)

Always use these `make` targets rather than raw tool commands, so CI and local runs behave the same.

| Command | What it does |
|---|---|
| `make setup` | Install dependencies |
| `make dev` | Run the app locally (used for UAT) |
| `make test` | Unit tests |
| `make lint` | Lint + format check |
| `make typecheck` | Type checks |
| `make check` | lint + typecheck + test + build. **Must pass before any PR** |
| `make e2e` | End-to-end / browser tests (if available) |
| `make audit` | Dependency vulnerability audit |
| `make secrets` | Scan uncommitted changes for secrets |
| `make smoke` | Post-deploy smoke test against a URL |

Project-specific test skills: `TODO(setup): list any extra test skills or scripts and when to run them (e.g. an end-to-end check of the main user journey).`

## 9. Documentation is part of the work

- Specs: `docs/specs/` · Assessments: `docs/assessments/` · UAT plans: `docs/uat/` · Decisions: `docs/decisions/` · Templates: `docs/templates/`. Files are named `<FILE-ID>-<slug>.md`, where `<FILE-ID>` is `GH-123` (GitHub Projects) or `APP-123` (Linear).
- If you learn something about the codebase that the next agent would need (a gotcha, a module's purpose, a convention), add it to `docs/product/ARCHITECTURE.md` in the same PR.
- Don't rely on chat memory for anything that matters. If it isn't in Git or the tracker, the next session won't know it.

## 10. Communication style with the human

- Lead with the outcome: what changed, what's waiting on them, links (issue, PR, UAT plan).
- When you need a decision, give options and a recommendation in a few lines.
- Plain English. Assume the product owner is technical but not a full-time developer.

## 11. Tool-specific notes

The rules above are the same for every tool. Only the plumbing differs:
- **Guard-rails that apply to everyone, whatever the tool:** GitHub branch protection, required checks, the UAT label, deploy approval, the git pre-commit secret hook (`make hooks`) and the CI secret scan. Your tool's own permission settings are an extra layer, not a substitute.
- **Per-tool setup** (MCP, skills, safe settings): `docs/setup/AGENTS-SETUP.md`.
- **Personal preferences** go in git-ignored files (`CLAUDE.local.md`, `AGENTS.local.md`, `.claude/settings.local.json`…), never in shared files.

