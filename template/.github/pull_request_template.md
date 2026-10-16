## Linear issue
APP-XXX: <link>

## Built with
<!-- Agent tool and model (e.g. Claude Code / Opus, Cursor / <model>, Codex, Grok Build), or "human". -->

## What and why
<!-- 2–4 sentences. What changed for the user, and why. -->

## Acceptance criteria → tests
| AC | Test(s) | Status |
|---|---|---|
| AC1 | `test_…` | ✅ |

## How to verify
- UAT plan: `docs/uat/APP-XXX-*.md` (added by `/uat`)
- Screenshots / notes:

## Risk
- Protected areas touched: none / <list> (if any → label `human-review`)
- Migrations: none / <describe + rollback>
- Config / env changes: none / <list>

## Checklist (G3)
- [ ] `make check` passes locally
- [ ] Every acceptance criterion has a test
- [ ] No unrelated changes
- [ ] Docs updated (ARCHITECTURE.md, .env.example, …) or not needed
- [ ] No secrets or real personal data

<!-- Release gate (G4): this PR can only merge with label `uat-passed`, or `gate-override` plus an "OVERRIDE: <reason>" comment. Docs-only PRs are exempt. -->
