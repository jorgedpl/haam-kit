# Contributing to HAAM

Thanks for helping improve the Human-Agent Agile Methodology. Contributions of all sizes are welcome: typo fixes, clearer docs, better skills, tool fixes, support for more agent tools.

## Before you start

- **Bugs:** open an issue with the bug template. Include `python3 template/tools/haam/haam.py version` and, if relevant, `doctor --json` output (remove anything private first).
- **Ideas and bigger changes:** open an issue with the idea template first, so we can agree the direction before you spend time on it. Changes to the lifecycle, gates or skill behaviour affect every project using HAAM.

## How the repository is organised

- `template/` is the kit: everything here gets copied into users' projects. Keep it **generic**: no company names, no product names, no personal data. The Linear team key placeholder is `APP`; the product name placeholder is `` `TODO(setup): product name` ``.
- `tests/` tests the setup tool (`template/tools/haam/haam.py`).
- Workflows under `template/.github/` are for users' projects; they don't run on this repository. This repository's own CI is in the root `.github/`.

## Making a change

1. Fork, create a branch, make your change.
2. Run the tests: `python3 -m unittest discover -s tests -v`
3. If you changed workflows: `actionlint template/.github/workflows/*.yml`
4. Keep the setup tool dependency-free (Python standard library only) and working on Python 3.8+.
5. Add a line under **[Unreleased]** in `CHANGELOG.md`. If projects need to do anything beyond `haam.py update` (e.g. re-run `github --apply` for a new required check), add a **Migration** note.
6. Open a pull request using the template.

## Principles for changes

- **Humans decide, agents execute.** Don't add ways for agents to pass human gates on their own.
- **Secrets never pass through an agent.** Anything needing a key is run by a human in their own terminal.
- **Show before change.** Tool commands plan first and act only with `--apply`. Nothing is deleted automatically.
- **Any agent, same rules.** New features should work for every supported tool, or degrade to "follow this Markdown file".
- **Plain English.** Docs and skills are read by people who aren't full-time developers, and by agents.

## Releases

Maintainers release by updating `VERSION`, the `VERSION` constant in `template/tools/haam/haam.py` and `CHANGELOG.md`, then pushing a tag `vX.Y.Z`. The release workflow checks the versions match, runs the tests and publishes the release with a zip.

## Licence

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
