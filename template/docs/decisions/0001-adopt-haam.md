# ADR 0001: Adopt the Human-Agent Agile Methodology (HAAM)

- **Status:** Accepted
- **Date:** YYYY-MM-DD
- **Deciders:** Product owner

## Context
Work on this product is increasingly done by coding agents (Claude Code, Cursor, Codex, Grok and others). Without a shared process, context lives in individual chats, priorities are implicit, and a second developer with their own Claude account cannot work in parallel. We also need production changes to be verified by a human before release, with a way to move fast in emergencies.

## Decision
- Linear is the system of record for work items, status and priority. Git is the system of record for specs, decisions, UAT plans and code.
- Work follows HAAM as described in `docs/process/LIFECYCLE.md` with five gates (`docs/process/GATES.md`).
- Agents, whatever the tool, follow `AGENTS.md` and the shared skills in `.agents/skills/`.
- Gates G3–G5 are enforced by GitHub (branch protection, required checks, a protected `production` environment). G1–G2 are enforced by convention and Linear status.
- Humans can override gates with a recorded reason and an automatic follow-up issue.

## Consequences
- Slightly more ceremony for small changes, offset by agents doing most of the paperwork.
- Anyone can pick up any issue from Linear + Git alone.
- Requires a Linear workspace, the Linear ↔ GitHub integration, and GitHub branch protection on `main`.

## Alternatives considered
- **GitHub Issues + Projects only:** fewer tools, but weaker triage, priorities and planning views.
- **Jira:** more powerful, but heavier than a small team needs.
- **No formal process:** fastest today, doesn't scale to parallel agents or a second developer.
