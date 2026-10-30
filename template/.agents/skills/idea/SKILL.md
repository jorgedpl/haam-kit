---
name: idea
description: Capture a new product idea as an issue in the tracker, in Triage. Use when the user describes a new idea, feature request, improvement or "what if we...".
argument-hint: "<short description of the idea>"
---

# /idea: capture an idea

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step below the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Idea: $ARGUMENTS

Capture is fast and cheap. Do not assess or judge yet.

1. **Check for duplicates.** Search the tracker for open issues with similar titles or keywords. If a close match exists, show it to the user and ask whether to add this as a comment there instead.
2. **Fill the template** `docs/templates/idea.md` from what the user said. Only ask follow-up questions if the *problem* or *who it's for* is completely unclear (max 2 questions). Leave unknown fields as `Unknown`; don't invent evidence.
3. **Create the issue in the tracker** (GitHub Projects: `haam.py issue create --stream idea --title "…" --body-file <file>`):
   - Title: short, outcome-focused (e.g. "Let admins bulk-invite users from CSV")
   - Description: the filled template
   - Status: `Triage`
   - Labels: `stream:idea`
   - Priority: none (humans set priority at G1)
   - The board's own fields (GitHub: `haam.py issue fields`): if `haam.config.json` lists `required_issue_fields`, set **every** name there with `--field NAME=VALUE` (pick the closest option; create refuses without them). Otherwise add `--field` only for fields the idea clearly answers; leave out any you'd have to guess.
4. **Epics:** if an open epic clearly covers this idea, say so and offer to add it there (GitHub: `issue link <n> --parent <epic>`). If the idea is big enough to be several features, say it could be an epic and suggest `/epic "<theme>"`.
5. **Reply** with the issue ID and link, and one line: "Run `/assess <ID>` when you want it evaluated."

No Git changes in this step.
