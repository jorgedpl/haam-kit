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
- **Statuses:** Triage → Discovery → Decision → Backlog → Ready → In Progress → UAT → In Review → Deploying → Done (plus Parked, Canceled). That's the default test-first order; checks-first projects put In Review before UAT.
- **Gates:** G1 Decision (human) · G2 Ready (human approves spec) · G3 automated checks + independent AI review (+ human for protected areas) · G4 UAT (human, local) · G5 production approval (human).
- **Epics:** a parent issue labelled `epic` groups the issues (its sub-issues) that make up one feature; its brief in `docs/epics/` holds the context.
- **Issue IDs:** `#123` on GitHub Projects, `APP-123` on Linear (`TODO(setup)`: replace with your team key everywhere). Skills write `<ID>` for either.

Every piece of work has an issue in the tracker. If you are asked to do something with no issue, create one first with `/idea` or `/bug` (ask the human which, if unclear).

## 2. Skills (commands) for each stage

Skills live in `.agents/skills/<name>/SKILL.md` (the shared Agent Skills format). How to call one depends on the tool: `/build <ID>` in Claude Code, Cursor and Grok; `$build <ID>` in Codex. If your tool doesn't load skills, open the skill's `SKILL.md` and follow it step by step. Wherever a skill says `$ARGUMENTS`, use the text the human typed after the command.

| Stage | Skill | Who runs it |
|---|---|---|
| Capture an idea | `/idea <text>` | anyone |
| Report a bug | `/bug <text>` | anyone |
| Assess an idea + feasibility | `/assess <ID>` | agent |
| Build a throwaway prototype to try (never merged) | `/spike <ID>` | agent |
| Triage and prioritise with the product owner | `/triage [group\|inbox\|backlog\|stale]` | **human only** |
| Shape an epic with the product owner | `/epic <ID>` or `/epic "<theme>"` | **human only** |
| Record a decision (G1) | `/decide <ID> approve\|park\|reject` | **human only** |
| Write the spec (no ID: the next Backlog feature by priority) | `/spec [<ID>]` | agent |
| Start an agent in a new chat window | `/work [bugs\|features\|specs\|ideas\|epic <ID>]` | anyone |
| Pick the next work item | `/next` | agent |
| Build a ready issue | `/build <ID>` | agent |
| Prepare UAT | `/uat <ID>` | agent |
| Test a change, then ship it or send it back (G4, G5) | `/test [<ID>]` | **human only** |
| Record UAT result (G4) | `/uat-result <ID> pass\|fail` | **human only** |
| Override a gate | `/override <ID> "<reason>"` | **human only** |
| Close after deploy (G5) | `/release <ID>` | **human only** |
| Adopt HAAM in a repo | `/haam-setup` | **human only** (project admin) |
| Onboard a developer | `/haam-onboard` | **human only** (new developer) |
| Upgrade HAAM to a new version | `/haam-update` | **human only** (project admin) |
| Change how HAAM runs here (CI, reviews, testing, grouping, shipping, limits) | `/haam-settings` | **human only** (product owner) |

Each skill's `SKILL.md` has the exact steps. Follow them; don't improvise a different process.

The setup skills drive `tools/haam/haam.py`; run `python3 tools/haam/haam.py doctor` any time to see what's missing.

## 3. Hard rules: never break these

1. **Never push to `main`, never merge a PR, never deploy, never run production commands.** Humans do that. The one exception: inside `/test`, typed by a human, after the human said `pass` (`haam.py publish` opens the PR) and `ship` in this session, `haam.py ship <ID> --human` merges the commit they tested, approves the deploy and closes the issue for them. (`/release` uses `ship --merged-only`, which never merges.) **Only the owner's chat ships:** agent chats in worktrees never run `ship`, and the tool refuses there.
2. **Never add the PR labels `uat-passed`, `gate-override` or `ai-review-overruled`, never add `uat:skip`, `mode:prototype` or `mode:epic-build` to an issue, never post the `uat` commit status, never change the project's settings** (`haam.py settings --human` is only for `/haam-settings`), and never move an issue to Done, Backlog (from Decision), Parked or Canceled. Those are human decisions. The only exception is when a human has typed `/triage`, `/epic`, `/decide`, `/test`, `/uat-result`, `/override`, `/release` or `/haam-settings` in this session; then you carry out exactly what that skill says. (`/spec` adds `agent-ready`, and `uat:skip` when the owner said "no UAT", only on their explicit approval.)
3. **Only build issues that are in `Ready` and have the `agent-ready` label** (bugs: `Ready` is enough). A prototype (`/spike`) is the exception: it's built before the spec, on a branch that never merges. If something isn't ready, help make it ready (`/spec`) instead of building it. **Never build an epic** (label `epic`) as one piece: build its sub-issues, and read the epic's brief in `docs/epics/` for context. When the owner labelled the epic `mode:epic-build`, one lead agent builds its sub-issues on one branch (`/build`, *Epic build mode*); other chats leave them alone.
4. **Claim before you build, assess, prototype or write a spec** (see §6). Never work on an issue another chat has claimed: every chat runs as the same person, so the claim, not the assignee, is what tells them apart.
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

The same areas as path patterns live in `haam.config.json` → `"protected_paths"` (the owner adds theirs with `haam.py config --protected "src/auth/**" --human`, or `/haam-settings`). `python3 tools/haam/haam.py protected` lists the protected files your branch changes; the release gate checks them too, adds `human-review` when they're touched and never lets them through the no-UAT lane.

## 5. Code review: how your PR gets checked

You never review your own work, and you never decide that a review is wrong on your own.
- Before opening a PR: `make check`, then do a security self-review of your diff and fix what it finds (Claude Code: `/security-review`; other tools: review `git diff origin/main...` against section D of `.github/review/REVIEWER.md`).
- When the PR is marked ready: `secrets`, `dependencies`, `ai-review` and `security-review` run (on GitHub, or `ai-review`/`security-review` via `haam.py review` on the owner's computer when the project chose local reviews). The reviewer agent posts a comment with **Blocking / Should fix / Nits**.
- Fix every Blocking item and push. Should-fix items: fix if small and in scope, otherwise log a `/bug`. Ignore nits unless trivial.
- If you disagree with a finding, reply on the PR with your reasoning and ask the human. Never push changes just to game the reviewer.
- After `max_review_rounds` failing review rounds (`haam.config.json`, default 2), stop and hand over to the human (issue comment + chat).

## 6. Working with the tracker

The tracker is either a GitHub Projects board (`"tracker": "github"`) or Linear (`"tracker": "linear"`). How to do each operation in each one: `docs/process/TRACKER.md`.
- **GitHub Projects:** use `python3 tools/haam/haam.py issue …` (works from any agent tool; uses your `gh` login).
- **Linear:** use the Linear connection (MCP, `https://mcp.linear.app/mcp`; per-tool setup in `docs/setup/AGENTS-SETUP.md`).

You act as the human who is running this session. If you can't reach the tracker, stop and tell the human; don't track work anywhere else.

**Claim protocol (before building, assessing or writing a spec):**
1. Re-fetch the issue. If it's `In Progress`, has label `claimed`, or is assigned to someone else, stop and pick another.
2. Assign it to the current user. Building: set status `In Progress`. Assessing (`Discovery`) or writing a spec: add label `claimed`.
3. Comment: ``🤖 Claimed by <user> via <agent tool> [on <machine>] [to assess it | to write its spec] · branch `<branch-name>` · claim <id>`` (the branch in backticks: `/test` reads it; the id is any 6 random hex characters, and tells this chat's claim from another's).
4. Re-read the comments. If another chat's claim comment landed just before yours (within 10 minutes, with no `🔓 Claim released` after it), you lost the race: comment that yours is withdrawn and pick another.
5. When an assessment or spec is pushed, release the claim: unassign, remove `claimed`, comment ``🔓 Claim released``. A build's claim ends by itself when its PR opens.
On GitHub Projects, `haam.py issue claim <number> [--for assess|spec|spike] --tool "<tool>" --machine "<machine>"` does steps 1–4 and prints the claim id; `haam.py issue release <number> --claim <id> [--status Decision]` does step 5.

**Never move an issue another chat has claimed.** On GitHub Projects, `issue status` and `issue release` refuse for a claimed issue unless this chat is on its branch or gives its claim id (`--claim`); `--force` is only for when the human asks (e.g. `/triage stale` releasing a stuck claim).

**While working:** keep the issue updated with short comments at meaningful points (plan posted, PR opened, blocked, handover). Not a running commentary.

**If you stop before finishing:** push the branch (checks-first: open or update a **draft** PR; test-first: no PR) and post a handover comment: *Done / Not done / Next step / Gotchas*.

## 7. Working with Git

- Branch from fresh `main`. Branch, commit and PR naming per tracker (`docs/process/TRACKER.md`):

  | | GitHub Projects | Linear |
  |---|---|---|
  | Branch | `123-short-title` | `app-123-short-title` |
  | Commit | `#123: <imperative summary>` | `APP-123: <imperative summary>` |
  | PR title | `#123: <summary>` | `APP-123: <summary>` |
  | PR description | must include `Refs #123` | (title links it) |

- The assessment and spec are committed on the issue's own branch, without a PR, and ship with the code in one PR (epics and split specs are the exception: they get a docs PR). Fewer PRs means fewer CI runs.
- **Spikes** (`/spike`) use `spike/<branch-name>` and never merge: the release gate and `publish` refuse them. Build freely there: no spec, no PR, no size limit. Put stand-alone prototype code in `prototypes/<slug>/`.
- **Production code** is what runs for real users: `production_paths` in `haam.config.json`, minus `non_production_paths` (prototypes, tests, docs by default). `python3 tools/haam/haam.py production` lists the production files your branch changes. Every change meets every gate, whatever mode it was built in; the production list tells you and the owner what runs for users. A kept prototype reaches production code only through `/spec` and a normal branch, behind a feature flag that's off by default. Production code never imports from `prototypes/`, and nothing under `prototypes/` merges.
- **The owner's settings** (`haam.config.json`, changed with `/haam-settings`; `python3 tools/haam/haam.py settings` shows them) decide when CI and the AI reviews run, what the owner tests, how work is grouped (`grouping`: per-issue, per-epic, or one `release` PR for everything passed) and the limits. Follow them; never change them yourself.
- **No-UAT lane:** if the owner marked the issue `uat:skip` (their decision, for changes they can't meaningfully test; with the setting `uat: bugs-skip`, `/triage` marks bugs that way by default), don't run `/uat`: open the PR ready (not draft) with `--label uat:skip`, and it merges by itself once CI and both AI reviews pass on GitHub (otherwise the owner ships it). Never for protected areas (§4). `/build` step 7 has the details.
- **Test first (default, `"flow": "test-first"`):** push your branch as you go (free: branch pushes start no workflows) but **don't open a PR**. Hand over with `/uat`; the owner tests it on their computer, and their `/test` opens the PR after they pass it, so CI and the reviews run once, on tested code. If a PR exists during rework, turn it back into a draft before pushing (`gh pr ready --undo`).
- **Keep CI cost down (checks-first projects):** open PRs as **drafts** (CI and reviews skip them), make the ready version complete (UAT plan and release note included), mark it ready once (`gh pr ready`), and group each round of fixes into one push. Before starting new work, `/next` checks `haam.py capacity`. If `haam.config.json` says `"review": "local"`, run `haam.py review <ID>` after marking ready (a fresh session reviews it; you don't review your own work).
- Fill in `.github/pull_request_template.md` completely, including **Built with** (your agent tool and model).
- Rebase on `main` before opening or updating a PR. Keep PRs small (target: `max_pr_lines` changed lines, default 400).
- **One chat, one folder.** Chats that share a folder overwrite each other's files and branches. When more than one agent chat may be open on a machine, each agent chat that changes files works in its own git worktree under `worktree_dir` in `haam.config.json` (default `.claude/worktrees/`); `/work` sets one up (`python3 tools/haam/haam.py worktree status|new|prep|clean`). The main folder belongs to the human's chat. When unsure, use a worktree.
- **One heavy run at a time.** Some test runs use something the whole machine shares (a local database the tests clone, a simulator, a device), so two chats running them at once break each other and it looks like a broken change. If `haam.config.json` lists `heavy_runs`, run those commands through `python3 tools/haam/haam.py exclusive "<this chat, #ID>" -- <command>` (e.g. `-- make check`): it waits for the machine-wide lock and for any other heavy run to finish, runs the command and returns its exit code (124: it gave up waiting, nothing ran). Waiters take turns in the order they came. On a machine where the owner set `HAAM_REMOTE_RUNNER=<ssh host>`, a waiting `make …` run goes to that host as soon as its lock is free: the same commit, with your uncommitted changes, in a temporary worktree there, with the output and exit code back here as if it ran locally. A chat's own scripts always run here. A failure right after another chat's run is worth one rerun through `exclusive` before you call the change broken.

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

- Epic briefs: `docs/epics/` · Specs: `docs/specs/` · Assessments: `docs/assessments/` · UAT plans: `docs/uat/` · Decisions: `docs/decisions/` · Templates: `docs/templates/`. Files are named `<FILE-ID>-<slug>.md`, where `<FILE-ID>` is `GH-123` (GitHub Projects) or `APP-123` (Linear).
- If you learn something about the codebase that the next agent would need (a gotcha, a module's purpose, a convention), add it to `docs/product/ARCHITECTURE.md` in the same PR.
- Don't rely on chat memory for anything that matters. If it isn't in Git or the tracker, the next session won't know it.

## 10. Communication style with the human

- Lead with the outcome: what changed, what's waiting on them, links (issue, PR, UAT plan).
- When you need a decision, give options and a recommendation in a few lines.
- Plain language. Assume the product owner is technical but not a full-time developer.
- **Language:** write to people in the project's language (`language` in `haam.config.json`; `en` if unset): chat, tracker issues and comments, specs, assessments, UAT plans, PR descriptions and docs. Keep commands, labels, statuses, setting names, file names, branch names and code exactly as they are, in English. These agent rules stay in English whatever the language.

## 11. Tool-specific notes

The rules above are the same for every tool. Only the plumbing differs:
- **Guard-rails that apply to everyone, whatever the tool:** GitHub branch protection, required checks, the UAT label, deploy approval, the git pre-commit secret hook (`make hooks`) and the CI secret scan. Your tool's own permission settings are an extra layer, not a substitute.
- **Per-tool setup** (MCP, skills, safe settings): `docs/setup/AGENTS-SETUP.md`.
- **Personal preferences** go in git-ignored files (`CLAUDE.local.md`, `AGENTS.local.md`, `.claude/settings.local.json`…), never in shared files.

