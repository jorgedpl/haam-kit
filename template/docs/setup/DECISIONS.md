# Decisions to make when you adopt HAAM

The product owner makes these, with the project admin. `/haam-setup` walks through them in this order, with a recommendation for each, and `/haam-settings` changes them later. Start with the recommended choice, then revisit after the first busy week. By then, `haam.py ci-usage` shows where the Actions minutes went and `haam.py capacity` shows what's waiting for you.

**A few words used here:**
- **PR** (pull request): a proposed change, waiting to be merged into `main`.
- **CI:** the automated checks (lint, types, tests, build) that run on GitHub for a PR. They use Actions minutes.
- **UAT** (user acceptance test): your own test of a change, on your computer, before it ships.
- **The no-UAT lane:** changes you mark `uat:skip` (dependency updates, config, invisible refactors). They skip your test and go straight to the checks.
- **Release gate:** the check that stops a PR merging until your test passed, or you chose the no-UAT lane.
- **Worktree:** a separate copy of the project folder for one agent chat, so chats don't overwrite each other.

## At a glance

| Decision | Start with | Change it when | See |
|---|---|---|---|
| GitHub account and plan | An organization. Public repository: Free. Private: Team | The repository is private and you need an approver on deploys: Enterprise Cloud | §1 |
| Tracker | GitHub Projects | The team already works in Linear every day | §2 |
| Who's who | One product owner, one backup approver | Several products or owners | §3 |
| Testing order (`flow`) | `test-first` | You test on a shared staging site rather than locally | §4 |
| What you test (`uat`) | `owner-decides` | Regulated product: `always`. Many small, well-tested fixes: `bugs-skip` | §4 |
| Grouping (`grouping`) | `per-issue` | Epics made of small items: `per-epic`. Actions minutes are scarce: `release` | §4 |
| Checks (`ci`, `review`, `nightly`, `runner`) | `every-pr`, `github`, `on`, `github` | Actions minutes run short | §4 |
| Shipping (`deploy`, `deploy_approval`) | `github`, `each` | You deploy another way, or your plan can't hold deploys for approval | §4 |
| Limits | `settings --recommend` | Your testing time or the number of agents changes | §5 |
| Protected areas | The defaults, plus your sensitive code | The architecture changes | §6 |
| Shared test resources (`heavy_runs`) | None | Tests share a local database, a simulator or a device | §7 |

## 1. GitHub account, organization and plan

### Accounts
Each person creates and keeps their own account; never share a login.

1. **Each person** signs up at [github.com/signup](https://github.com/signup) with their work email and turns on two-factor authentication (Settings → Password and authentication).
2. **One admin** creates an organization ([github.com/organizations/plan](https://github.com/organizations/plan)) and invites the team. The free plan is enough for a public repository; a private one needs Team (see the table below). The organization owns the repositories, so nothing depends on one person's account. Make two people owners.
3. **The repository** lives in the organization: create it there, or move an existing one (repository Settings → General → Transfer ownership).
4. **On each computer**, install the GitHub CLI ([cli.github.com](https://cli.github.com)) and run `gh auth login`. With GitHub Projects as the tracker, also run `gh auth refresh -s project`.
5. **No separate accounts for agents.** Agents act under the logged-in person's account. The gates assume the person at the keyboard is accountable for what their agents do.

### Which plan you need

| What HAAM uses | Public repository, any plan | Private, Free | Private, Pro | Private, Team | Private, Enterprise Cloud |
|---|---|---|---|---|---|
| Branch rules and required checks ([rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)) | Yes | No | Yes | Yes | Yes |
| An approver on production deploys ([environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)) | Yes | No | No | No | Yes |
| GitHub's own secret scanning and push protection ([Secret Protection](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security)) | Yes | No | No | Paid add-on | Paid add-on |
| GitHub Projects board | Yes | Yes | Yes | Yes | Yes |
| Actions minutes | Free on standard runners | A monthly allowance | A larger allowance | A larger allowance | A larger allowance |

Pro is for a personal account; Team and Enterprise Cloud are for organizations.

What each missing piece means:
- **No branch rules** (private repository on Free): GitHub doesn't stop a merge into `main` without the checks. Agents are still told never to merge, and `ship` still runs every gate, but nothing enforces it. For any private product, use Team (organization) or Pro (personal account).
- **No deploy approver** (private repository below Enterprise Cloud): deploys start when a PR merges. Your `ship`, which does the merge, is then the release decision. Set `deploy_approval: automatic` so HAAM doesn't wait for an approval that can't happen, and keep `uat` at `owner-decides` or `always` (§4).
- **No GitHub secret scanning:** fine. The kit's own `secrets` check and the pre-commit hook run on every plan.

Plans and allowances change, so check [github.com/pricing](https://github.com/pricing) before you choose.

### The reviewers' access to Claude
The two AI reviews run with one repository secret, added by the owner in their own terminal and never pasted into a chat:
- `CLAUDE_CODE_OAUTH_TOKEN` (from `claude setup-token`): the reviews count against that person's Claude plan.
- `ANTHROPIC_API_KEY`: billed per review, separately from anyone's subscription. Set a monthly spend limit in the Anthropic console.

## 2. The tracker: GitHub Projects or Linear

| | GitHub Projects | Linear |
|---|---|---|
| Cost | Free on every GitHub plan | Free up to 250 active (non-archived) issues and 2 teams; paid plans per user remove the cap. Check [linear.app/pricing](https://linear.app/pricing) |
| How agents use it | `haam.py issue …` from any agent tool, with the person's `gh` login | The Linear connection (MCP) set up in each agent tool |
| Done for you | Claims that stop two chats taking the same task; the UAT queue counted for the limits; the board's own fields (`--field`); the no-UAT lane merging by itself; `ship` closing issues | Agents make the moves through the connection, and count the UAT queue for `capacity --in-uat N`. The no-UAT lane doesn't merge by itself: you ship those PRs |
| Setup | `haam.py github-project --apply` | `haam.py linear --apply` with the owner's API key, plus the browser steps in `LINEAR-SETUP.md` |
| Best for | Most teams: everything in one place | Teams that already live in Linear |

**Recommendation:** GitHub Projects, unless the team already uses Linear every day. Triage and agents create issues quickly, so Linear's free cap can be reached within weeks.

## 3. Who's who
- **Product owner:** one person, who decides, tests and ships. Only they run the human-only skills: `/triage`, `/epic`, `/decide`, `/test`, `/uat-result`, `/override`, `/release` and `/haam-settings`.
- **Backup approvers:** one or two people who can approve deploys when the owner is away (`config --backup-approvers a,b`). This needs an approver on deploys, so it has no effect on a private repository below Enterprise Cloud.
- **Builders:** everyone who runs agent chats. Each needs their own GitHub account with write access, and their own agent tool. The admin runs `haam.py invite --github USER` to see the plan, then the same with `--apply`. Each builder then runs `/haam-onboard`.
- **Admin:** sets up GitHub, the tracker and the secrets. Often the owner.
- **Once two people work on the code,** require one approval in the branch rules (`GITHUB-SETUP.md` §2).

## 4. How work flows: the settings
`python3 tools/haam/haam.py settings --explain` prints every option with its trade-off. The choices that matter:

| Setting | Start with | Choose otherwise when | What it costs or risks |
|---|---|---|---|
| `flow` | `test-first`: you test the agent's branch, then the PR and checks run once | `checks-first`: you only want to test code that passed the checks, or you test on a shared staging site | Each rework round runs the checks again |
| `uat` | `owner-decides`: you test everything except what you mark `uat:skip` | `always`: regulated or safety-critical products. `bugs-skip`: many small fixes with strong tests | `bugs-skip`: a wrong fix can ship without your eyes |
| `grouping` | `per-issue`: one PR per issue | `per-epic`: epics made of small items. `release` (test-first only): scarce minutes and batch releases | One failing item holds back the batch |
| `ci` | `every-pr`, on GitHub | `local`: minutes run out and your computer builds everything. `off`: solo prototypes only | `local` isn't tamper-proof |
| `review` | `github`: two independent AI reviews per PR | `protected-only`: saves most review cost. `local`: saves minutes | Fewer independent checks |
| `nightly` | `on` | `off`: when minutes are very scarce | You find breakage and new vulnerabilities later |
| `runner` | `github` | `self-hosted`: a private repository with heavy builds and a machine that stays on | Upkeep. Never for public repositories |
| `deploy` | `github`: `deploy.yml` deploys on merge | `manual`: you deploy another way | `ship` waits for you to say "live" |
| `deploy_approval` | `each`: every deploy waits for your approval | `automatic`: your plan can't hold deploys (§1), or you chose `uat: always` | A merged change goes live without a last look |
| `worktree_cleanup` | `after-ship` | `manual`: you'd rather tidy worktrees yourself | Disk space |

The no-UAT lane merges by itself only on GitHub Projects, with the `HAAM_PROJECT_TOKEN` secret, `ci: every-pr` and `review: github`. Otherwise you ship those PRs yourself.

Avoid these pairs, because together they remove the last check:
- `ci: off` with `review: off`: nothing checks the code before your test.
- `deploy_approval: automatic` with `uat: bugs-skip`: a bug fix can reach production without any person looking at it. Deploys are automatic on a private repository below Enterprise Cloud, so don't choose `bugs-skip` there.

## 5. Limits: how much work may wait
The limits stop agents producing more than you can test, and more PRs than your CI budget covers. When a limit is reached, agents stop starting new builds. They still fix rework, write specs and assess ideas.

| Limit | What it counts | How to size it |
|---|---|---|
| `max_in_uat` | Changes waiting for your test. The main limit in test-first | What you can test in one sitting: minutes per sitting ÷ minutes per test (a test often takes 5 to 10 minutes). One hour a day at about 6 minutes a test is 10 |
| `max_open_prs` | Ready PRs. Drafts, docs-only PRs and bots' PRs (Dependabot) don't count | Test-first: PRs live briefly (from your pass to `ship`), so twice the agent chats running at once is plenty. Checks-first: every change waiting for your test is a ready PR, so set it to at least `max_in_uat` plus the chats running at once |
| `max_review_rounds` | Failing AI review rounds before an agent stops and asks you | 2. Raise it to 3 for hard areas |
| `max_pr_lines` | Target size of one PR, in changed lines | 400. Smaller PRs get better reviews and tests |

Work it out for your team:
```
python3 tools/haam/haam.py settings --recommend --builders 2 --chats 3 --testing-hours 5 --sittings 5
```
It prints the suggested limits and warns when the agents can produce more than you can test. Then it gives the command that applies them. It assumes about 6 minutes a test and 2 changes per chat a day; pass `--minutes-per-test` and `--changes-per-chat` with your own numbers. It reads `flow` from the project's settings, or takes `--flow`.

If the agents out-produce your testing:
- the queue fills and agents pause new builds, which is the limit doing its job;
- `/test all` with "pass all verified" clears the changes the agents proved themselves;
- `uat: bugs-skip` sends small bug fixes straight to the checks;
- or run fewer agent chats.

For a weekend of agent work tested in one sitting, open a **batch window**: a raise that ends by itself after its last day, e.g. `settings --set max_in_uat=30 --until <last day, YYYY-MM-DD> --human`.

## 6. What to protect
**The rule:** protect the code where a wrong change could hurt users, lose money or data, break the law, or weaken HAAM's own gates. Every protected change needs your code review and your test, and never takes the no-UAT lane. So protect what matters, not everything.

| Area | Protect | Typical paths (examples) |
|---|---|---|
| Sign-in, sessions, permissions, roles | Always | `src/auth/**`, `**/permissions/**`, *the auth middleware* |
| Payments, billing, refunds, pricing | Always | `src/billing/**`, `src/payments/**` |
| Personal data: storage, retention, deletion, exports | Whenever you hold personal data | `src/users/**`, `**/privacy/**` |
| Logging that could capture personal data | Whenever you hold personal data | *the logging configuration and audit modules* |
| Decisions about users: eligibility, verification, approvals, scoring | When a wrong result harms someone | `src/verification/**`, `src/decisions/**` |
| External providers that act for users or receive their data | Yes | `src/integrations/**` |
| Database migrations | Always | `db/migrations/**`, `**/migrations/**` |
| Security configuration: crypto, CORS, CSP, secrets handling | Yes | `**/security/**`, `**/crypto/**` |
| Infrastructure as code | Yes | `infra/**`, `terraform/**` |
| Mobile signing and release configuration | If you ship apps | *entitlements, signing and release build files* |
| CI, deploy and build scripts | Protected by default | `.github/**`, `Makefile`, `scripts/**` |
| HAAM and the agent setup | Protected by default | `AGENTS.md`, `CLAUDE.md`, `.agents/**`, `.claude/**`, `tools/haam/**`, `haam.config.json`, and more: `haam.py settings` lists them |

Paths in italics describe what to look for; turn them into real patterns for your code.

How to set it up:
1. `/haam-setup` proposes real paths from your code for each area that applies. You confirm them.
2. `config --protected "src/auth/**,db/migrations/**" --human` adds patterns, and `config --unprotected "…" --human` removes one. `**` means any folders and `*` means within one folder. A plain folder name covers everything inside it.
3. `haam.py protected` on any branch lists the protected files it changes.
4. The release gate decides from the files a PR changes. It reads the list from `main`, so an agent can't remove a protection in its own PR.

Review the list whenever `docs/product/ARCHITECTURE.md` changes.

## 7. Shared test resources
Some tests use something the whole computer shares, such as a local database the tests clone, a phone simulator or a connected device. Two agent chats running them at once break each other, and the failure looks like a broken change. List those commands as patterns: `config --heavy-run "make (check|test-integration)"`. Agents then run them one at a time through `haam.py exclusive`. Leave the list empty when your tests are self-contained.

## Sources
- GitHub: [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) (plans that include them) · [Deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments) (required reviewers on private repositories) · [About GitHub Advanced Security](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security) (Secret Protection) · [Pricing](https://github.com/pricing)
- Linear: [Pricing](https://linear.app/pricing)
