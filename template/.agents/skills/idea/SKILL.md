---
name: idea
description: Capture a new product idea as a Linear issue in Triage. Use when the user describes a new idea, feature request, improvement or "what if we...".
argument-hint: "<short description of the idea>"
---

# /idea: capture an idea

Idea: $ARGUMENTS

Capture is fast and cheap. Do not assess or judge yet.

1. **Check for duplicates.** Search Linear (team `APP`) for open issues with similar titles or keywords. If a close match exists, show it to the user and ask whether to add this as a comment there instead.
2. **Fill the template** `docs/templates/idea.md` from what the user said. Only ask follow-up questions if the *problem* or *who it's for* is completely unclear (max 2 questions). Leave unknown fields as `Unknown`; don't invent evidence.
3. **Create the Linear issue:**
   - Team: `APP`
   - Title: short, outcome-focused (e.g. "Let admins bulk-invite users from CSV")
   - Description: the filled template
   - Status: `Triage`
   - Labels: `stream:idea`
   - Priority: none (humans set priority at G1)
4. **Reply** with the issue ID and link, and one line: "Run `/assess APP-xxx` when you want it evaluated."

No Git changes in this step.
