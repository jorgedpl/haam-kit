# Developer onboarding

Welcome. This repo is built by humans and coding agents working together using the **Human-Agent Agile Methodology (HAAM)**. You can use the agent tool you prefer: Claude Code, Cursor, Codex, Grok, Gemini or Copilot. This guide gets you from zero to your first issue in about an hour.

## The fast way: let your agent onboard you

1. Clone the repo and open your agent tool in its root folder:
   ```bash
   git clone git@github.com:TODO(setup)/TODO.git && cd TODO
   ```
2. Tell your agent:
   - Claude Code, Cursor or Grok: `/haam-onboard`
   - Codex: `$haam-onboard`
   - Any other tool: *"Read `.agents/skills/haam-onboard/SKILL.md` and follow it."*

It checks your machine, access and tracker connection, sets up your local hooks and `.env`, runs the project checks, explains how we work and suggests a first issue. Steps that need your password or keys are done by you, in your own terminal or editor. You never paste secrets into the chat.

Prefer to do it by hand? The sections below cover the same ground.

---

## 1. Read first (15 minutes)
1. `AGENTS.md`: the rules every agent follows, whatever the tool. They apply to you too.
2. `docs/process/LIFECYCLE.md`: streams, statuses, gates, who does what.
3. `docs/process/GATES.md`: checklists, code review and overrides.
4. `docs/product/PRODUCT.md` and `docs/product/ARCHITECTURE.md`: what we're building and how it's structured.

## 2. Accounts you need
| Account | Why | Ask for |
|---|---|---|
| GitHub | Code, PRs, CI | Write access to the repo |
| Tracker | Backlog and status | **GitHub Projects:** access to the board (comes with the repo invite). **Linear:** membership of team **APP** |
| Your agent tool | Coding agent | Your **own** account (Claude, Cursor, OpenAI, xAI…). Never share accounts |
| Test services | Running locally | Test credentials only, from the product owner |

The project admin invites you with one command: `python3 tools/haam/haam.py invite --github <you> --linear-email <you@…> --apply`. You will **not** get production credentials; deploys go through GitHub with approval.

## 3. Install tools
- Git, GitHub CLI (`gh auth login`), Make, Python 3
- **gitleaks** (required; commits are blocked without it): macOS `brew install gitleaks`; others: https://github.com/gitleaks/gitleaks/releases
- Language runtime for this repo: `TODO(setup): e.g. Node 22 via nvm / Python 3.12 / PHP 8.3`
- Your agent tool

Check everything with: `python3 tools/haam/haam.py dev`

## 4. Get the code running
```bash
python3 tools/haam/haam.py dev --apply   # commit hook on, .env created from .env.example
# put the TEST values from the product owner into .env yourself
python3 tools/haam/haam.py dev --run-checks   # make setup + make check
make dev                                       # app at http://localhost:TODO
```

## 5. Connect to the tracker
Check `"tracker"` in `haam.config.json`:
- **GitHub Projects:** run `gh auth refresh -s project` once, then test: `python3 tools/haam/haam.py issue list --status Ready`.
- **Linear:** follow your tool's section in `docs/setup/AGENTS-SETUP.md` (one sign-in), then ask your agent: *"List the Ready issues in Linear team APP."*

## 6. Your personal settings (not shared)
Personal notes and preferences go in git-ignored files: `AGENTS.local.md`, `CLAUDE.local.md`, `.claude/settings.local.json`, or your tool's user settings. Never put shared rules there. If something should apply to everyone, propose a change to `AGENTS.md` via PR.

## 7. Day-to-day workflow
Commands are written `/name` below; in Codex use `$name`.

| You want to… | Do this |
|---|---|
| See what's waiting | Tracker view **Agent queue** (to build) or **Waiting on me** |
| Start an agent in a new chat window | `/work` (or `/work bugs`) |
| Start work in this chat | `/next`, or `/build APP-123` |
| Triage and prioritise (product owner) | `/triage`, `/triage group`, `/epic`, and `docs/process/PRODUCT-MANAGER.md` |
| Log an idea | `/idea …` |
| Report a bug | `/bug …` |
| Turn an approved idea into a spec | `/spec APP-123` |
| Test a change (product owner) | `/test`, then `pass` → `ship`, or say what's wrong |
| Test someone's change (developer) | Follow `docs/uat/APP-123-*.md`, then tell the product owner |
| Check your setup | `python3 tools/haam/haam.py doctor` |

### Running agents in parallel
Open one new chat window per agent and type `/work` (or `/work bugs`, `/work features`; Codex: `$work`). The agent gets its own copy of the project (a git worktree under `.claude/worktrees/`), copies the local files listed in `.worktreeinclude` (like `.env`), picks the top item and works it through to the hand-over. Keep your own chat in the main folder for ideas, decisions and testing.

- **Claude Code in VS Code:** new chat tab with Cmd+Shift+Esc (Mac) or Ctrl+Shift+Esc (Windows/Linux). In a terminal: `claude --worktree`.
- **Other tools:** if the tool has its own worktree or parallel-agent option, use it; otherwise `/work` creates the worktree and tells you which folder to open in a new window.
- **Another computer:** same thing. The claim on the tracker stops two agents taking the same issue; name the machine when asked so the claim comment shows where it's running.
- **Tidy up** finished worktrees now and then: `python3 tools/haam/haam.py worktree clean` (plan), then `--apply`.
- **Testing an agent's branch:** the UAT plan uses `git switch --detach origin/<branch>`, which works while the agent's worktree still has the branch.

### Running agents semi-autonomously
- **Attended:** type `/next`, review its choice, let it run. Your tool should ask before it pushes or opens PRs (see safe settings in `docs/setup/AGENTS-SETUP.md`).
- **Unattended:** a scheduled task or cron runs your agent headless with the prompt `/next` (Codex: `$next`). It only takes work that has passed its gate, and stops at UAT for a human.
- Agents stop at every human gate by design. Your job is to keep the **Waiting on me** view short.

## 8. How your work gets reviewed
Every PR is checked by tests, a secret scan, a dependency audit and two independent AI reviewers (spec/quality and security) that never saw the code being written. Fix their **Blocking** findings; if you think one is wrong, reply on the PR and ask the product owner, who can overrule with the label `ai-review-overruled`. Protected areas also get a human review. Details: `docs/process/GATES.md` § How code review works.

**If you ever commit a real secret:** tell the product owner straight away. It has to be revoked and rotated, even if you delete it in the next commit.

## 9. Rules worth repeating
- No pushes to `main`, no merges, no deploys from agents.
- No secrets or real personal data in code, tests, fixtures, the tracker or chat. Personal data is protected by law (e.g. GDPR).
- One issue → one branch → one PR, small enough to review in 15 minutes.
- Fill in **Built with** on every PR (your tool and model).
- If it isn't in Git or the tracker, it doesn't exist for the next person.

## 10. Getting help
- Process questions: ask your agent *"according to LIFECYCLE.md, what should happen when…"*
- Access and credentials: the product owner.
- Improving the process: open an `/idea` with label `area:process`. Changes to `AGENTS.md`, `.agents/`, agent config folders and `.github/` need the product owner's review.
