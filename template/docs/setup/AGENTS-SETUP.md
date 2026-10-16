# Agent tools: setup per tool

HAAM works with any coding agent. Every tool reads the **same rules** (`AGENTS.md`) and the **same skills** (`.agents/skills/`), and connects to the **same Linear** (`https://mcp.linear.app/mcp`). Only the plumbing differs.

Run `python3 tools/haam/haam.py agents` to see what's wired up in this repo, and `python3 tools/haam/haam.py dev` to check your machine.

## How each tool picks up HAAM

| | Rules | Skills | Calling a skill | Linear (MCP) | Human-only skills |
|---|---|---|---|---|---|
| **Claude Code** | `CLAUDE.md` → imports `AGENTS.md` | `.claude/skills` (link to `.agents/skills`) | `/build APP-1` | `.mcp.json` (in repo) | `disable-model-invocation` |
| **Cursor** | `AGENTS.md` | `.agents/skills` | `/build APP-1` | `.cursor/mcp.json` (in repo) | `disable-model-invocation` |
| **Codex** | `AGENTS.md` | `.agents/skills` | `$build APP-1` | per user: `codex mcp add` | `agents/openai.yaml` in each skill |
| **Grok Build** | check on first run (see below) | `.grok/skills` (link to `.agents/skills`) | `/build APP-1` | reads `.mcp.json` | as per skill text |
| **Gemini CLI** | `AGENTS.md` via `.gemini/settings.json` | follow `SKILL.md` by name | "follow .agents/skills/build" | per user | as per skill text |
| **GitHub Copilot** | `AGENTS.md` | follow `SKILL.md` by name | "follow .agents/skills/build" | per user | as per skill text |

If a tool doesn't load skills, tell it: *"Open `.agents/skills/<name>/SKILL.md` and follow it."* The skills are plain Markdown.

## Connect to Linear (one time per person)

Linear signs you in with your own account (OAuth). Agents act as you.

- **Claude Code:** open `claude` in the repo → approve the `linear` server → `/mcp` → **linear** → sign in.
- **Cursor:** Settings → MCP → `linear` appears from `.cursor/mcp.json` → enable → sign in.
- **Codex:** `codex mcp add linear --url https://mcp.linear.app/mcp`, then follow the sign-in prompt.
- **Grok Build:** it reads `.mcp.json`; if not, `grok mcp add linear --transport http https://mcp.linear.app/mcp`. Sign in when prompted.
- **Gemini CLI / Copilot / others:** add a remote MCP server named `linear` with URL `https://mcp.linear.app/mcp` in the tool's MCP settings.

**Test:** ask your agent *"List the Ready issues in Linear team APP."*

## Safe settings per tool

The hard guard-rails live in GitHub and git, so they protect you **whatever the tool does**: no pushes to `main`, required checks, UAT label, deploy approval, the commit secret hook (`make hooks`) and the CI secret scan. Tool settings are a second layer that stops mistakes earlier. Recommended:

| Tool | Recommended settings |
|---|---|
| **Claude Code** | Already configured in `.claude/settings.json`: asks before pushes/PRs, blocks merges/deploys/`.env` reads, secret-scan hook before commits. Keep it. |
| **Cursor** | Agent auto-run: use an allow-list (make targets, git status/diff/log, `gh pr view/checks`) and require confirmation for `git push`, `gh pr create/edit/merge`, anything with `deploy`. Add `.env*` to Cursor's ignore so the agent can't read it. |
| **Codex** | Sandbox *workspace-write* and approval policy *on-request* (asks before network actions and pushes). Avoid "full access" modes in this repo. |
| **Grok Build** | Use its permission rules (repo-level allowed) to require approval for `git push`, `gh pr merge`, deploy commands; deny reading `.env*`. It supports `PreToolUse` hooks: you can call `bash scripts/scan-secrets.sh` before `git commit`, like the Claude hook does. Avoid `--always-approve` outside CI. |
| **Gemini CLI / Copilot** | Keep confirmations on for shell commands; never auto-approve pushes or merges. |

Never give any agent tool your production credentials or a GitHub token with admin rights.

## First-run check for every tool

Ask the agent, in the repo:
1. *"What are the hard rules in this repository?"* It should list the rules from `AGENTS.md` §3. If not, tell it to read `AGENTS.md` first, and check the tool's settings for the instructions file name.
2. *"Which skills do you have for this project?"* It should list idea, bug, assess, spec, next, build, uat… If not, see the table above.
3. *"List the Ready issues in Linear team APP."* This checks the Linear connection.

## Recording which tool did the work
The claim comment in Linear and the PR's **Built with** field record the tool and model. After a few weeks you can compare review findings and UAT failures by tool.

## Cross-model review
The CI reviewer agents use Claude. When code is written with a different tool (Codex, Grok, Cursor with another model), the review is also cross-model, which is a useful extra check.
