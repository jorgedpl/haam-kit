---
name: decide
description: Record the product owner's Gate G1 decision on an assessed idea (approve, park or reject).
argument-hint: "<ID> approve|park|reject [urgent|high|medium|low] [notes]"
disable-model-invocation: true
---

# /decide: Gate G1 (human decision)

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Decision: $ARGUMENTS

This skill only runs when a human types it. You are recording *their* decision, not making one.

1. **Parse** the issue ID, decision and optional priority/notes. If the decision word is missing or ambiguous, ask. Do not infer it.
2. **Load the issue.** It should be in `Decision`. If not, warn and ask for confirmation before continuing.
3. **Apply in the tracker** (GitHub Projects: these moves need `--human`, e.g. `haam.py issue status 12 Backlog --human`):
   - **approve** → status `Backlog`; replace label `stream:idea` with `stream:feature`; set priority (ask if not given); comment `✅ Approved at G1 by <user>: <notes>`.
   - **park** → status `Parked`; ask for a "revisit when…" trigger if not in the notes; comment `⏸️ Parked: <notes>`.
   - **reject** → status `Canceled`; comment `❌ Rejected: <notes>` (ask for a one-line reason if none given).
4. **Epics:** if the issue is an epic, show its open sub-issues and ask whether the decision applies to them too (default: yes for sub-issues that are ideas; bugs keep their own path). On yes, apply the same move to each (approve: `Backlog` + `stream:feature`, with the epic's priority unless the human says otherwise) and comment `Decided with epic <ID>`.
5. **The assessment's branch:** on approve, it stays: the spec and code continue on it. On park, it stays for later. On reject, offer to delete it (`git push origin --delete <branch>`, with the human's OK); the reasoning stays in the issue comments.
6. **ADR:** if the decision fixes a technical choice that future agents must respect (e.g. "use provider X", "no new database"), draft an ADR in `docs/decisions/` from `docs/templates/adr.md` on the issue's branch (or a small docs PR for an epic) and say so.
7. **Reply** with the new status and, for approvals: "Next: `/spec <ID>`."
