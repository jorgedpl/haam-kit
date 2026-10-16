# Security policy

The HAAM kit installs files and runs a setup tool on people's machines, and configures their GitHub repositories and Linear workspaces. Security reports are taken seriously.

## Reporting a vulnerability

Please **don't** open a public issue. Use GitHub's private reporting: **Security → Report a vulnerability** on this repository. Include what's affected, how to reproduce it, and the impact. You'll get a reply within 7 days.

## Supported versions

Security fixes go into the latest minor release. Upgrade with `haam.py update`.

## Using the kit safely

- **Install from a tagged release, not `main`,** and review what you run. The setup tool is a single readable Python file with no dependencies.
- **Never paste API keys or passwords into an agent's chat.** The tool asks for them only in your own terminal, uses them for that run, and never stores them.
- The kit's commands plan first and change things only with `--apply`. Read the plan before applying.
- The CI reviewer workflows use an Anthropic API key stored as a GitHub secret. Use a dedicated key with a spend limit.
- If a secret is ever committed to your project: revoke and rotate it with the provider first, then clean the history.
