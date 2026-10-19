---
name: haam-update
description: Upgrade this project to a newer version of the HAAM kit, keeping the project's customisations, and apply any migration steps. Use when the admin asks to update or upgrade HAAM, or doctor reports an update is available.
argument-hint: "[version, e.g. v1.1.0; default: latest release]"
disable-model-invocation: true
---

# /haam-update: upgrade HAAM in this project (project admin)

Target version: $ARGUMENTS (empty = latest release)

**Rules:** work on a branch; show the plan before applying; never paste or ask for secrets in chat; nothing is deleted without the human's OK.

## 1. Where are we?
1. `python3 tools/haam/haam.py version --check`: current project version and latest release.
2. If already on the target version, say so and stop.
3. `git switch -c chore/haam-<target-version>` from an up-to-date default branch.

## 2. Get the new kit (outside the project)
```bash
git clone --depth 1 --branch <target-version> https://github.com/jorgedpl/haam-kit.git /tmp/haam-kit-<target-version>
```
(If git can't reach GitHub, ask the human to download the release zip and tell you where they unzipped it.)

## 3. Read what changed
Open `/tmp/haam-kit-<target-version>/CHANGELOG.md`. Summarise for the human, in a few lines, every release between the project's version and the target: what's new, and any **Migration** steps. A major version change (e.g. 1.x → 2.0) always has migration steps; read them carefully.

## 4. Plan, then apply
1. `python3 /tmp/haam-kit-<target-version>/template/tools/haam/haam.py update --target .` (plan only). Explain it: new files, files updated (the project hadn't changed them), customised files kept, files needing a merge, files no longer in the kit.
2. On the human's OK: same command with `--apply`.

## 5. Merge and tidy
1. For each file in `.haam/incoming/`: merge the kit's changes into the project's version, keeping the project's customisations (project knowledge, protected-area paths, filled-in commands). Show the human a short summary per file. Then delete `.haam/incoming/`.
2. Files no longer in the kit: tell the human which they can delete; delete only with their OK.
3. `python3 tools/haam/haam.py agents --apply`

## 6. Migration steps
Do each step from the CHANGELOG. Typical ones:
- New required checks or labels: `python3 tools/haam/haam.py github` (plan) → `--apply` on the human's OK.
- New statuses, fields or labels: GitHub Projects: `python3 tools/haam/haam.py github-project` (plan) → `--apply` on the human's OK. Linear: the **human** runs `python3 tools/haam/haam.py linear` then `--apply` in their own terminal (it needs their API key).
- New `TODO(setup)` placeholders: fill them from the codebase or ask the human.

## 7. Verify and open the PR
1. `python3 tools/haam/haam.py doctor --role admin` and `make check`.
2. Commit (`Update HAAM to <target-version>`), including `haam.lock.json`; ask before pushing; open a PR summarising the changes and migration steps done.
3. Remind the human to tell the other developers to pull and re-run `python3 tools/haam/haam.py dev --apply` (it turns the commit secret scan on without switching off anyone's own git hooks: if a clone has hooks of its own in `.git/hooks`, it chains the scan from there instead of setting `core.hooksPath`).
