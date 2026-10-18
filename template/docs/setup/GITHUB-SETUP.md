# GitHub setup (one-time, ~30 minutes, repo admin)

This turns gates G3–G5 from conventions into rules GitHub enforces.

> **Automated:** labels (§1), branch rules (§2), the production environment (§4) and security features (§3b–c) are done by `python3 tools/haam/haam.py github --apply` (plan first without `--apply`). This page is the manual equivalent, plus the steps GitHub only offers in the browser. The `ANTHROPIC_API_KEY` secret is always added by you: `gh secret set ANTHROPIC_API_KEY -R owner/repo`.

## 1. Labels
Create these repository labels (Issues → Labels), or run:
```bash
gh label create uat-passed     --color 0E8A16 --description "Gate G4 passed: human UAT OK"
gh label create gate-override  --color B60205 --description "Human override of G4; needs OVERRIDE: comment"
gh label create human-review   --color FBCA04 --description "Touches protected area; human code review required"
gh label create ai-review-overruled --color 5319E7 --description "Human overrules the AI reviews on this PR"
```

## 2. Branch protection on `main`
Settings → **Rules → Rulesets** → New branch ruleset (or classic Branch protection), target `main`:

- ✅ Restrict deletions; block force pushes
- ✅ Require a pull request before merging
  - Required approvals: **1** once you have a second human; **0** while you're solo (UAT label is your approval)
  - ✅ Dismiss stale approvals when new commits are pushed
- ✅ Require status checks to pass (leave "require branches to be up to date" off: it re-runs CI on every open PR after each merge)
  - Required checks: **`ci`**, **`secrets`**, **`dependencies`**, **`ai-review`**, **`security-review`** and **`release-gate`** (they appear in the list after the workflows have run once on a PR)
- ✅ Require linear history (optional, keeps history clean)
- **Bypass list:** repository admins only, **for pull requests only** (never "always": agents work under a human's login, often an admin's, and could otherwise push straight to `main`). This is the Level 2 emergency bypass in `docs/process/GATES.md`.

## 3. Code review and security

### 3a. Anthropic API key for the reviewer agents
The independent reviewers (`.github/workflows/review.yml`) run Claude in GitHub Actions.
1. Create an API key at console.anthropic.com (a dedicated key for this repo, with a monthly spend limit).
2. Settings → **Secrets and variables → Actions** → New repository secret **`ANTHROPIC_API_KEY`**.

This is billed per review, separately from anyone's Claude subscription. Draft and docs-only PRs don't call Claude. Review instructions live in `.github/review/REVIEWER.md`; tune them as you learn.

### 3b. Secret scanning and push protection
Settings → **Security** (Code security / Advanced Security, depending on your plan):
- ✅ **Secret scanning**, ✅ **Push protection**: GitHub rejects pushes containing known secret formats.
- Free for public repositories. For private repositories it may require GitHub's paid security add-on; if you don't have it, the kit's own `secrets` check (gitleaks) and the local hooks still cover you.

### 3c. Dependency alerts
Settings → **Security**: ✅ Dependabot alerts, ✅ Dependabot security updates. Then uncomment your ecosystem in `.github/dependabot.yml`. Dependabot PRs go through the same gates.

### 3d. Pull requests from forks
Settings → **Actions → General** → *Fork pull request workflows*: require approval for all outside collaborators. (Fork PRs don't get repository secrets, so AI reviews can't run on them; a human reviews and overrules if needed.)

## 4. Production environment (Gate G5)
Settings → **Environments** → New environment **`production`**:
- **Required reviewers:** product owner (+ one backup person if you have one)
- ✅ Prevent self-review: leave **off** while you're the only approver, turn on later
- **Deployment branches and tags:** selected branches → `main` only
- **Environment secrets:** production deploy credentials go here and nowhere else
- **Environment variables:** `PRODUCTION_URL` (used by the smoke test)

Now every merge to `main` runs `deploy.yml`, which pauses at *deploy-production* until an approver clicks **Review deployments → Approve**. GitHub emails/notifies the approvers.

## 5. CODEOWNERS (optional but recommended once there are two humans)
`.github/CODEOWNERS`:
```
# Protected areas need the product owner's review
/.claude/            @your-github-handle
/.github/            @your-github-handle
/AGENTS.md           @your-github-handle
/CLAUDE.md           @your-github-handle
/.agents/            @your-github-handle
/tools/haam/         @your-github-handle
# TODO(setup): add paths for verification logic, auth, payments, migrations
```
Then enable "Require review from Code Owners" in the ruleset.

## 6. Fill in the command contract
Edit `Makefile` (including `audit`) and the runtime setup steps in `.github/workflows/ci.yml`, `security.yml` and `deploy.yml` (look for `TODO(setup)`). Open a PR. The `ci` check must go green on that PR before you turn on required checks.

## 7. Optional: Claude GitHub app
If you want to tag an agent on a PR for a quick fix (e.g. the Claude GitHub app via `/install-github-app` in Claude Code, or your other tool's GitHub integration), install it. Any such app is bound by the same branch protection and checks, so it can't bypass the gates.

## 8. Keeping Actions minutes down

Private repositories get a monthly allowance of Actions minutes; agents opening many PRs use it fast. What the kit already does: by default (test-first) agents push branches without opening PRs, and a PR opens only after you've tested and passed the change, so the checks run once on tested code (checks-first projects: draft PRs don't run anything, and agents mark a PR ready once, when it's complete); docs-only PRs skip the checks; `main` is checked nightly instead of after every merge; labels, comments and new issues don't start runners; agents hold new work at 5 open PRs (`max_open_prs`).

Find out where the minutes go: `python3 tools/haam/haam.py ci-usage` (last 7 days, by workflow, job, trigger and day).

Two switches, set with `python3 tools/haam/haam.py ci-settings … --apply` (they're repository variables the workflows read):

| Switch | What changes | Trade-off |
|---|---|---|
| `--review local` | The two AI reviews run on your computer in fresh Claude sessions (`haam.py review`), using your Claude plan instead of Actions minutes. PRs labelled `human-review` are still reviewed on GitHub | The result is no longer tamper-proof: the building agent starts the review (fresh, read-only sessions, instructions from `main`), and anything using your login could post a passing result. Run `haam.py review` from your own chat for more separation |
| `--runner self-hosted` | All jobs except the deploy run on your own machine (registered under Settings → Actions → Runners) instead of GitHub's | The machine must be on, with git, make, Python 3, curl, gitleaks and your project's tools; private repositories only. Check GitHub's current pricing for self-hosted runners |

Also worth checking: jobs on macOS runners count 10 minutes for every minute they run (Windows: 2). Run mobile builds only when the mobile code changed (`make check` gets the changed files in `$CI_CHANGED_FILES`), or nightly.

## 9. Check it works
1. Open a tiny test PR (e.g. a typo fix in code). `ci`, `secrets` and `dependencies` run; the reviewer agent posts a comment and `ai-review` / `security-review` report back; `release-gate` shows **failure: waiting for UAT**.
   - **Secret test:** on a throwaway branch, commit a fake AWS-style key such as `AKIA` followed by 16 capital letters/digits in a code file. The local hook should block the commit; if you bypass it with `--no-verify`, the `secrets` check should fail. Delete the branch afterwards.
2. Add label `uat-passed` → `release-gate` turns green → merge is allowed.
3. After merge, Actions → Deploy shows **Waiting for review** on `deploy-production`.
4. Open a docs-only PR → `release-gate` passes automatically.
