# Working as the product manager

*A guide for the human who decides what gets built. Agents don't need to read it; you do.*

In HAAM you decide **what** and **why**; agents work out **how** and do it. Agents are fast, so the speed of the whole system is set by how quickly you triage, decide, approve and test. Your main job is to keep the **Waiting on me** queue short and the **Agent queue** pointed at the right things.

Examples use GitHub Projects IDs (`#12`); on Linear the same item is `APP-12`. Commands are written `/name`; in Codex use `$name`.

---

## 1. Your job on one page

| What only you do | How often | With AI | Directly in the tracker |
|---|---|---|---|
| Keep `docs/product/PRODUCT.md` current: current priorities, non-negotiables, core journeys | Monthly | "Update PRODUCT.md: our priorities are now…" | Edit the file (via a PR) |
| Triage new ideas and bugs | Daily | `/triage` | Triage view: priority, status, labels |
| Set and change priorities | Daily and weekly | `/triage`, `/triage backlog` | Priority field |
| Decide on assessed ideas (G1) | Weekly | `/decide #12 approve high` | Status, labels, comment (§6) |
| Approve specs (G2) | As they arrive | Merge the spec PR, then "spec for #12 approved, mark it ready" | Merge the spec PR, Status Ready, label `agent-ready` |
| Test changes locally (G4) | Daily | Follow the UAT plan, then `/uat-result #12 pass` | (needs the skill: it adds the PR label) |
| Merge and approve deploys (G5) | When UAT passes | Merge, approve the deploy, `/release #12` | GitHub: merge and approve |
| Close override follow-ups | Weekly | "Show the open override follow-ups" | View: label `override-followup` |

Everything you decide goes into the tracker or Git, never only into a chat. If it isn't written down there, the next agent doesn't know it.

---

## 2. Your rhythm

### Daily (10–15 minutes)
1. **Test first.** Open **Waiting on me** and test anything in **UAT**, oldest first. Agents can't finish until you do, and their context goes stale.
2. **Empty the Triage inbox** (`/triage`, or the Triage view). Nothing should sit there for more than two working days.
3. **Urgent bugs:** if one exists, start an agent on it now: new chat window, `/work bugs`.
4. Skim the handover and "blocked" comments from agents and answer their questions.

### Weekly (30–45 minutes)
1. **Decide** everything in **Decision** (G1).
2. **Review spec PRs** and approve or comment (G2).
3. **Re-rank** Ready and Backlog against the current priorities (`/triage backlog`).
4. **Find stuck work:** `/triage stale` (claimed but quiet, UAT waiting too long, decisions overdue).
5. **Revisit Parked** items whose "revisit when" has come true.
6. **Close override follow-ups** (label `override-followup`).
7. Improve one thing in the process (an `/idea` with label `area:process`).

### Monthly or quarterly (30 minutes)
1. Rewrite **Current priorities** in `PRODUCT.md`: 3–5 outcomes, in order. Agents use them to suggest priorities and break ties, so this is the single most useful thing you can keep current.
2. **Prune:** anything Low that has waited more than two months → Park it with a "revisit when". A short backlog is a usable backlog.

---

## 3. Triage: deciding what each new item is

The **Triage** status is your inbox. Ideas and bugs land there from `/idea`, `/bug`, the issue forms, other people and agents. Aim for an empty inbox at the end of each day.

For each item, answer four questions:

1. **Is it clear and new?** Duplicate → close it and link the original. Not enough information → comment with your question and leave it in Triage.
2. **What is it?** A **bug** means something doesn't work as intended. An **idea** means new or changed behaviour. "Works as designed, but the user expected something else" is an idea, not a bug. Fix the stream label if it's wrong.
3. **How important is it?** Set the priority (§4).
4. **What happens next?**

| Item | Your call | Status after | What follows |
|---|---|---|---|
| Bug with clear steps to reproduce | **Ready** | Ready, with a priority | An agent picks it up (`/work bugs`) |
| Bug without enough to go on | **Needs info** | Stays in Triage, with your question as a comment | You or the reporter answer, then triage again |
| Urgent bug | **Ready, start now** | Ready, Urgent | Start an agent now; `/override` is available if the deploy can't wait |
| Idea worth exploring | **Assess** | Discovery, with a priority | An agent writes the assessment (`/work ideas` or `/assess #12`) |
| Good idea, wrong time | **Park** | Parked, with a "revisit when…" comment | Comes back at a weekly review |
| Idea you won't do | **Reject** | Canceled, with a one-line reason | Closed |
| Duplicate | **Duplicate** | Canceled, linked to the original | Closed |

Small ideas still go through assessment. Ask for a quick one ("assess #12, keep it short"). The assessment is where the agent checks the codebase and the risks, and it costs you a minute to read.

---

## 4. Prioritising

### 4.1 The four levels

| Priority | Test | Expected handling |
|---|---|---|
| **Urgent** | Production is broken for a core journey, data could be lost or exposed, a security hole, or a legal/compliance deadline is at risk | Start today. Gates can be overridden, with a follow-up |
| **High** | Directly advances one of the current priorities in `PRODUCT.md`, or a bug in a core journey with no workaround | Next up, this week |
| **Medium** | Useful, but not on the current priorities, or the evidence is thin | In order, when High is clear |
| **Low** | Nice to have, cosmetic, edge case | When idle; prune after two months |
| *(none)* | Not triaged yet | Agents won't build it |

Keep it honest: if more than about one in five open items is High or Urgent, the levels have stopped meaning anything. Demote something.

### 4.2 Bugs: impact × reach

| | Most users, or a core journey | Some users | A few users, or an edge case |
|---|---|---|---|
| **Blocks the task, loses or exposes data, security, legal** | Urgent | Urgent | High |
| **Wrong result, but there's a workaround** | High | Medium | Low |
| **Annoying or cosmetic** | Medium | Low | Low |

### 4.3 Ideas and features: value, confidence, size

After an assessment you have three things: **value** (how much it moves a current priority), **confidence** (how good the evidence is) and **size** (XS–XL, from the codebase). Rules of thumb:
- **High:** clear value for a current priority, good evidence, size S–M.
- **Medium:** good value but weaker evidence; or high value but L–XL size (ask for it to be split).
- **Low:** small value, whatever the size.
- **Not on the current priorities?** Medium at most, unless you change the priorities first.

To compare two ideas quickly: value (1–3) × confidence (0.5 / 0.8 / 1) ÷ size (XS 1, S 2, M 3, L 5, XL 8). The higher score goes first. It's a tie-breaker, not a formula to obey.

### 4.4 Order inside a priority
Agents take **bugs before features, older before newer, smaller before larger**. They read the priority, not the position of a card on the board. If X must happen before Y, give X a higher priority, or write `Blocked by #X` in Y's description.

### 4.5 Keep the queues healthy

| Queue | Healthy size | If not |
|---|---|---|
| **Agent queue** (Ready) | 3–10 items | Empty: agents sit idle, so spec more. Over 10: priorities go stale, so re-rank |
| **Decision** | 5 or fewer | Book 20 minutes and decide |
| **UAT** | 3 or fewer | Stop starting agents and test. Agents produce faster than you can test |
| **Agents running** | No more than you can test tomorrow | Fewer agents, smaller items |

### 4.6 Changing priorities
Change them whenever the facts change, but say why in a comment. Agents and colleagues read the history. Never quietly demote an Urgent item: comment, and tell whoever reported it.

---

## 5. Doing it with AI

Use **your own chat in the project's main folder**, not one of the agent chats running `/work`.

| You want to… | Type |
|---|---|
| Triage the inbox | `/triage` |
| Re-rank Ready and Backlog against the priorities | `/triage backlog` |
| Find stuck or forgotten work | `/triage stale` |
| Capture an idea or bug from anywhere | `/idea …`, `/bug …` |
| Get an idea assessed | `/assess #12` (or let `/work ideas` pick it) |
| Decide (G1) | `/decide #12 approve high "start with the admin side"` · `park` · `reject` |
| Approve a spec (G2) | Review and merge the spec PR, then: "spec for #12 approved, mark it ready" |
| Record a test result (G4) | `/uat-result #12 pass` or `/uat-result #12 fail <what went wrong>` |
| Close after deploy (G5) | `/release #12` |
| Emergency | `/override #12 "<reason>"` |

**How `/triage` works.** The agent reads `PRODUCT.md` and the items, then shows you one table: proposed stream, priority, next step and a short reason for each. Reply `ok` to apply it all, or with changes (`#14 Low, #9 park until Q3`). It changes nothing until you reply, applies exactly what you confirmed, and comments on each item so the reason is on record. It never approves ideas for you; for that it points you to `/decide`.

**Questions worth asking your agent:**
- "What's waiting on me?"
- "What did the agents finish since yesterday, and what's blocked?"
- "Which Ready items don't fit our current priorities?"
- "#12 is too big. Propose a split into pieces of size S."
- "Compare #12 and #15: which should go first, and why?"
- "Draft new current priorities for PRODUCT.md from what we've shipped and what's in the backlog."

The agent's suggestions are drafts, and you own the decisions. When `/bug` files a bug it fills in a suggested priority; you confirm or change it when you triage.

---

## 6. Doing it directly in GitHub Projects

Everything above can be done by hand on the board. The saved views (set up with `haam.py github-project`) are your workspace:

| View | Use it for |
|---|---|
| **Triage** (status: Triage) | Your daily inbox |
| **Waiting on me** (status: Decision, UAT) | Decisions and tests |
| **Agent queue** (status: Ready, unassigned) | What agents will pick up next, by priority |
| **Bugs** | All open bugs by priority |
| **Ideas inbox** | Ideas being triaged or assessed |
| **Board** | The whole flow, grouped by status |

| Task | On the board |
|---|---|
| Triage an item | Open it. Set **Priority** and **Status**; fix the stream label in the issue's sidebar; comment your reason |
| Park | Status **Parked**, and a comment: "revisit when…" |
| Reject or mark a duplicate | Status **Canceled**, then close the issue as *not planned* or *duplicate* |
| Approve an idea (G1) | Status **Backlog**; replace label `stream:idea` with `stream:feature`; set Priority; comment "Approved" |
| Approve a spec (G2) | Merge the spec PR; then Status **Ready** and label `agent-ready` |
| Re-rank many items | Table layout, grouped or sorted by Priority; edit the cells (you can copy a value and paste it into several selected cells) |

Leave these to the skills: claiming (**In Progress**) is the agents' job; **UAT pass** needs `/uat-result` (it adds the PR label that unlocks merging); **Done** needs `/release` (it closes the issue and updates the changelog after the deploy).

---

## 7. Doing it directly in Linear

| Task | In Linear |
|---|---|
| Triage | Use the team's **Triage** inbox. You can accept, decline, mark as duplicate or snooze. After accepting, **set the HAAM status yourself** (Ready for a bug, Discovery for an idea to assess), because accepting moves the item to the team's default status. Set the priority |
| Park or reject | Status **Parked** or **Canceled**, with a comment |
| Approve an idea (G1) | Status **Backlog**, replace label `stream:idea` with `stream:feature`, set priority, comment |
| Approve a spec (G2) | Merge the spec PR; then status **Ready** and label `agent-ready` |
| Re-rank | The views from `docs/setup/LINEAR-SETUP.md` §7, sorted by priority; the command menu (Cmd/Ctrl+K) changes priority or status quickly |

As on GitHub, agents follow the priority field, not the manual order of a list.

---

## 8. Working with other people

- **One product owner per product** sets priorities and passes the gates. Everyone else proposes: `/idea`, `/bug`, comments.
- Ask colleagues to suggest a priority when they report something. You confirm it at triage.
- **Disagreements go on the issue,** not in private chats. The product owner decides and says why in a comment.
- If you're away, name a backup approver (`haam.py config --backup-approvers`) and tell them which items can move without you.

---

## 9. Traps to avoid

- **Everything is High.** Then nothing is. Demote until roughly one item in five is High or Urgent.
- **More agents than you can test.** Work piles up in UAT and goes stale. Fewer, smaller items move faster.
- **"Just build it" in a chat.** Create the issue first (`/bug`, `/idea`): it takes a minute and keeps the history, the priority and the claim.
- **Approving a spec without reading the acceptance criteria.** That's what the agent builds and what you test against. Read them.
- **Priorities only in your head.** If they aren't in `PRODUCT.md` and the tracker, agents can't follow them.
- **Leaving Triage for "later".** The inbox grows, and urgent bugs hide in it.

---

## 10. Checklists

**Daily**
- [ ] UAT items tested, oldest first
- [ ] Triage inbox empty
- [ ] Urgent bugs have an agent on them
- [ ] Agents' questions answered

**Weekly**
- [ ] Decision queue decided
- [ ] Spec PRs approved or commented
- [ ] Ready and Backlog re-ranked
- [ ] Stale work chased (`/triage stale`)
- [ ] Parked items revisited
- [ ] Override follow-ups closed
- [ ] One process improvement logged

**Monthly**
- [ ] `PRODUCT.md` current priorities rewritten
- [ ] Old Low items parked
