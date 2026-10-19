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
| Group related issues into epics and answer the agent's questions about each | Weekly | `/triage group`, then `/epic #9` | Epic issue (label `epic`) with sub-issues |
| Set and change priorities | Daily and weekly | `/triage`, `/triage backlog` | Priority field |
| Decide on assessed ideas (G1) | Weekly | `/decide #12 approve high` | Status, labels, comment (§7–8) |
| Approve specs (G2) | As they arrive | Read the spec (linked on the issue), then "spec for #12 approved" | Comment "spec approved"; Status Ready, label `agent-ready` |
| Test changes (G4) and ship them (G5) | Daily | `/test`, then reply `pass` → `ship`, or say what's wrong | GitHub: label `uat-passed`, merge, approve the deploy |
| Close override follow-ups | Weekly | "Show the open override follow-ups" | View: label `override-followup` |

Everything you decide goes into the tracker or Git, never only into a chat. If it isn't written down there, the next agent doesn't know it.

---

## 2. Your rhythm

### Daily (10–15 minutes)
1. **Test first.** Type `/test all`: the agent walks you through every change waiting for you, one after another (§2a), then ships everything that passed with one deploy. Agents can't finish until you do, and their context goes stale.
2. **Empty the Triage inbox** (`/triage`, or the Triage view). Nothing should sit there for more than two working days.
3. **Urgent bugs:** if one exists, start an agent on it now: new chat window, `/work bugs`.
4. Skim the handover and "blocked" comments from agents and answer their questions.

### 2a. Testing a change: the whole loop
1. Type **`/test`** (or `/test #12`). The agent puts the change on your computer, starts the app, and gives you the link and a short checklist: *do this → you should see that*.
2. Try it. Then reply with one word or one sentence:
   - **`pass`** → the agent opens the pull request (until now there wasn't one: you tested the agent's branch), the checks run once on exactly what you tested, and it asks *"Ship it when the checks pass?"* Reply **`ship`**: it waits for them, merges, approves the production deploy for you, and closes the issue. You get *"#12 is live."* Reply `later` to hold it.
   - If your project **deploys by hand** (`"deploy": "manual"`), the agent merges and then asks you to deploy; reply **`live`** when it's out and it closes the issue.
   - If the checks or reviews then find a problem, it goes back to the agents like a failed test, and comes back to you once fixed.
   - **What went wrong** (*"step 3: the export button is still missing on mobile"*) → the agent records it on the issue, labels it `uat-failed` and sends it back to the agents, who fix it first. When it's fixed it comes back to `/test`.
3. That's all. You don't need to touch branches, labels or the board.

**How HAAM runs is your choice.** Type `/haam-settings`: it goes through each setting with your own numbers (Actions minutes, the UAT queue), recommends one option, and applies what you choose:
- when CI and the AI reviews run (every PR, on your computer, only for protected areas, or off);
- what you test yourself (everything, what you decide per issue, or bugs skip);
- how changes are grouped (per issue, per epic, or one release PR for everything you passed);
- whether deploys wait for your approval;
- the limits.

`python3 tools/haam/haam.py settings --explain` lists them all.

**Changes you can't test yourself** (kit or config updates, dependency bumps, refactors you wouldn't notice, CI): mark them `uat:skip` when you triage them, or say "spec approved, no UAT". They never come to `/test`: their PR merges by itself once CI and both AI reviews pass (GitHub Projects), and your next `ship` deploys them with everything else and closes them. If you don't ship anything for a while, run `/test` and reply `ship` anyway, or `ship --all`: their deploy waits for your approval. On Linear, ship them by name (`ship APP-12 --human`). Keep it for changes no user would notice; never for protected areas.

### Weekly (30–45 minutes)
1. **Group** loose issues into epics (`/triage group`) and shape the top epic with the agent (`/epic #9`).
2. **Decide** everything in **Decision** (G1).
3. **Review specs** (linked on each issue) and approve or comment (G2).
4. **Re-rank** Ready and Backlog against the current priorities (`/triage backlog`).
5. **Find stuck work:** `/triage stale` (claimed but quiet, UAT waiting too long, decisions overdue).
6. **Revisit Parked** items whose "revisit when" has come true.
7. **Close override follow-ups** (label `override-followup`).
8. Improve one thing in the process (an `/idea` with label `area:process`).

### Monthly or quarterly (30 minutes)
1. Rewrite **Current priorities** in `PRODUCT.md`: 3–5 outcomes, in order. Agents use them to suggest priorities and break ties, so this is the single most useful thing you can keep current.
2. **Prune:** anything Low that has waited more than two months → Park it with a "revisit when". A short backlog is a usable backlog.

---

## 3. Triage: deciding what each new item is

The **Triage** status is your inbox. Ideas and bugs land there from `/idea`, `/bug`, the issue forms, other people and agents. Aim for an empty inbox at the end of each day.

If several items look related, or most of them lack context, **group them first** (§4): triaging one feature at a time is faster and better than triaging fragments.

For each item, answer four questions:

1. **Is it clear and new?** Duplicate → close it and link the original. Not enough information → comment with your question and leave it in Triage.
2. **What is it?** A **bug** means something doesn't work as intended. An **idea** means new or changed behaviour. "Works as designed, but the user expected something else" is an idea, not a bug. Fix the stream label if it's wrong.
3. **How important is it?** Set the priority (§5).
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

## 4. Epics: grouping issues into features

Single issues often lack context. "Export button missing on mobile", "Export to CSV" and "Scheduled reports" are three fragments of one feature, and triaged one by one each looks small and unclear. An **epic** is a parent issue (label `epic`) that groups the issues for one outcome and carries the context they lack: who it's for, what success looks like, what's in and out of scope, and the order of the slices. That context lives in a short **epic brief** in `docs/epics/`.

**Use an epic for:** three or more issues about the same outcome; an idea too big for one spec (size L or XL); a request that touches several screens or modules.
**Don't use one for:** a single bug; a "misc" bucket of unrelated things; a theme that never ends ("performance", "UX polish"): those are priorities, not epics. An epic should be finishable, in weeks rather than quarters.

### How an epic flows
1. **Group.** `/triage group` looks at the loose issues and proposes epics: a title, the outcome in one line, which issues belong and why. You say `ok` or adjust (`merge 2 and 3`, `#40 out`). Or start from a theme: `/epic "reporting"`.
2. **Shape.** `/epic #9`: the agent reads every issue in the epic, the product context and the relevant code, drafts the brief, then **asks you up to five questions per round**: who it's for, what success looks like, must-haves versus nice-to-haves, constraints, what must not change, how it ranks. Then it proposes a clean-up: duplicates to close, gaps to add as new issues, unclear issues to rewrite, big ones to split, an order. Nothing changes until you confirm.
3. **Decide once (G1).** `/assess #9` adds effort and feasibility for the whole epic; `/decide #9 approve high` approves it and the ideas inside it in one go.
4. **Spec and build slice by slice.** Each sub-issue gets its own spec and passes G2 on its own. Agents build sub-issues, never the epic itself.
5. **Finish.** When the last sub-issue ships, the agent offers to close the epic.

**Priorities:** give the epic a priority; its issues take the same one unless you say otherwise. A bug inside an epic can still be more urgent than the epic.

**Answering the agent's questions:** short answers are fine. "Don't know yet" is a valid answer: it stays open in the brief. Answer about what users need and why; leave the how to the agents.

### Epics directly in the tracker
- **GitHub Projects:** create an issue and add the label `epic`; then, in the epic's sub-issues section, add the issues that belong to it (or set the parent from each issue). On the board, use the **Epics** view, and show the *Parent issue* and *Sub-issues progress* fields in table views so every card shows its epic.
- **Linear:** create an issue with the label `epic` and make the related issues its sub-issues (set their parent). For a very large initiative that spans several epics, a Linear project can hold the epics.

---

## 5. Prioritising

### 5.1 The four levels

| Priority | Test | Expected handling |
|---|---|---|
| **Urgent** | Production is broken for a core journey, data could be lost or exposed, a security hole, or a legal/compliance deadline is at risk | Start today. Gates can be overridden, with a follow-up |
| **High** | Directly advances one of the current priorities in `PRODUCT.md`, or a bug in a core journey with no workaround | Next up, this week |
| **Medium** | Useful, but not on the current priorities, or the evidence is thin | In order, when High is clear |
| **Low** | Nice to have, cosmetic, edge case | When idle; prune after two months |
| *(none)* | Not triaged yet | Agents won't build it |

Keep it honest: if more than about one in five open items is High or Urgent, the levels have stopped meaning anything. Demote something.

### 5.2 Bugs: impact × reach

| | Most users, or a core journey | Some users | A few users, or an edge case |
|---|---|---|---|
| **Blocks the task, loses or exposes data, security, legal** | Urgent | Urgent | High |
| **Wrong result, but there's a workaround** | High | Medium | Low |
| **Annoying or cosmetic** | Medium | Low | Low |

### 5.3 Ideas and features: value, confidence, size

After an assessment you have three things: **value** (how much it moves a current priority), **confidence** (how good the evidence is) and **size** (XS–XL, from the codebase). Rules of thumb:
- **High:** clear value for a current priority, good evidence, size S–M.
- **Medium:** good value but weaker evidence; or high value but L–XL size (ask for it to be split).
- **Low:** small value, whatever the size.
- **Not on the current priorities?** Medium at most, unless you change the priorities first.

To compare two ideas quickly: value (1–3) × confidence (0.5 / 0.8 / 1) ÷ size (XS 1, S 2, M 3, L 5, XL 8). The higher score goes first. It's a tie-breaker, not a formula to obey.

### 5.4 Order inside a priority
Agents take **bugs before features, older before newer, smaller before larger**. They read the priority, not the position of a card on the board. If X must happen before Y, give X a higher priority, or write `Blocked by #X` in Y's description.

### 5.5 Keep the queues healthy

| Queue | Healthy size | If not |
|---|---|---|
| **Agent queue** (Ready) | 3–10 items | Empty: agents sit idle, so spec more. Over 10: priorities go stale, so re-rank |
| **Decision** | 5 or fewer | Book 20 minutes and decide |
| **UAT** | 3 or fewer | Stop starting agents and test. Agents produce faster than you can test |
| **Agents running** | No more than you can test tomorrow | Fewer agents, smaller items |
| **Open PRs** | `max_open_prs` in `haam.config.json` (default 10) | Agents hold new work automatically (`haam.py capacity`): every open PR costs CI minutes on each push. Test and ship what's open |

### 5.6 Changing priorities
Change them whenever the facts change, but say why in a comment. Agents and colleagues read the history. Never quietly demote an Urgent item: comment, and tell whoever reported it.

---

## 6. Doing it with AI

Use **your own chat in the project's main folder**, not one of the agent chats running `/work`.

| You want to… | Type |
|---|---|
| Group loose issues into epics | `/triage group` |
| Shape one epic: brief, questions for you, clean-up | `/epic #9` (or `/epic "reporting"` to start from a theme) |
| Triage the inbox | `/triage` |
| Re-rank Ready and Backlog against the priorities | `/triage backlog` |
| Find stuck or forgotten work | `/triage stale` |
| Capture an idea or bug from anywhere | `/idea …`, `/bug …` |
| Get an idea assessed | `/assess #12` (or let `/work ideas` pick it) |
| Decide (G1) | `/decide #12 approve high "start with the admin side"` · `park` · `reject` |
| Approve a spec (G2) | Read it (linked on the issue), then: "spec for #12 approved" |
| Test a change, then ship it or send it back (G4, G5) | `/test` (or `/test #12`), then `pass` → `ship`, or say what's wrong |
| Close something that was merged another way | `/release #12` |
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

## 7. Doing it directly in GitHub Projects

Everything above can be done by hand on the board. The saved views (set up with `haam.py github-project`) are your workspace:

| View | Use it for |
|---|---|
| **Triage** (status: Triage) | Your daily inbox |
| **Epics** (label: epic) | Each feature and how far its sub-issues have got |
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
| Approve a spec (G2) | Comment "spec approved" on the issue; then Status **Ready** and label `agent-ready` |
| Group issues into an epic | Create an issue with label `epic`; add the others as its sub-issues |
| Re-rank many items | Table layout, grouped or sorted by Priority; edit the cells (you can copy a value and paste it into several selected cells) |

Leave these to the skills: claiming (**In Progress**) is the agents' job. Testing and shipping is easiest with `/test`; by hand it's: add the label `uat-passed` to the PR (that unlocks merging), merge it, approve the deploy (Actions → the run → Review deployments), then set the issue to **Done** and close it. If it failed, comment what's wrong on the issue, add the label `uat-failed`, set it back to **Ready** and remove the assignee.

---

## 8. Doing it directly in Linear

| Task | In Linear |
|---|---|
| Triage | Use the team's **Triage** inbox. You can accept, decline, mark as duplicate or snooze. After accepting, **set the HAAM status yourself** (Ready for a bug, Discovery for an idea to assess), because accepting moves the item to the team's default status. Set the priority |
| Park or reject | Status **Parked** or **Canceled**, with a comment |
| Group issues into an epic | Create an issue with label `epic`; set it as the parent of the related issues |
| Approve an idea (G1) | Status **Backlog**, replace label `stream:idea` with `stream:feature`, set priority, comment |
| Approve a spec (G2) | Comment "spec approved" on the issue; then status **Ready** and label `agent-ready` |
| Re-rank | The views from `docs/setup/LINEAR-SETUP.md` §7, sorted by priority; the command menu (Cmd/Ctrl+K) changes priority or status quickly |

As on GitHub, agents follow the priority field, not the manual order of a list.

---

## 9. Working with other people

- **One product owner per product** sets priorities and passes the gates. Everyone else proposes: `/idea`, `/bug`, comments.
- Ask colleagues to suggest a priority when they report something. You confirm it at triage.
- **Disagreements go on the issue,** not in private chats. The product owner decides and says why in a comment.
- If you're away, name a backup approver (`haam.py config --backup-approvers`) and tell them which items can move without you.

---

## 10. Keeping GitHub Actions costs down

Every pull request runs CI and two AI reviews on GitHub's machines, and private repositories have a monthly allowance of minutes. Agents work fast, so the allowance can go in days. What helps most, in order:
1. **Look first:** `python3 tools/haam/haam.py ci-usage` shows which workflows and jobs used the minutes.
2. **Fewer pull requests:** batch an epic's small items into one (`/work epic #9`), and keep the open-PR limit low (`max_open_prs` in `haam.config.json`).
3. **Reviews on your computer:** `haam.py settings --set review=local --apply` (or `/haam-settings`). The AI reviews then use your Claude plan instead of minutes; protected areas (`human-review`) are still reviewed on GitHub. The trade-off: on GitHub the review result is tamper-proof; locally it isn't. The reviews run in fresh, read-only sessions with the instructions from `main`, but the agent that built the change is the one that starts them, and anything using your login could post a passing result. For more separation, run `haam.py review <ID>` from your own chat yourself.
4. **Your own runner:** `haam.py settings --set runner=self-hosted --apply` after registering a machine that stays on (`docs/setup/GITHUB-SETUP.md` §8).
5. **Ask for smaller CI:** if the project has separate parts (e.g. backend and mobile app), have an agent make `make check` run only the parts a PR touches.

## 11. Traps to avoid

- **Everything is High.** Then nothing is. Demote until roughly one item in five is High or Urgent.
- **More agents than you can test.** Work piles up in UAT and goes stale. Fewer, smaller items move faster.
- **"Just build it" in a chat.** Create the issue first (`/bug`, `/idea`): it takes a minute and keeps the history, the priority and the claim.
- **Approving a spec without reading the acceptance criteria.** That's what the agent builds and what you test against. Read them.
- **Priorities only in your head.** If they aren't in `PRODUCT.md` and the tracker, agents can't follow them.
- **Building fragments without the big picture.** If several issues are really one feature, group them into an epic and shape it before anyone specs the pieces.
- **Epics that never end.** If an epic has been open for months, split off what's done and close it.
- **Leaving Triage for "later".** The inbox grows, and urgent bugs hide in it.

---

## 12. Checklists

**Daily**
- [ ] Everything in UAT tested with `/test`
- [ ] Triage inbox empty
- [ ] Urgent bugs have an agent on them
- [ ] Agents' questions answered

**Weekly**
- [ ] Loose issues grouped into epics; top epic shaped
- [ ] Decision queue decided
- [ ] Specs approved or commented
- [ ] Ready and Backlog re-ranked
- [ ] Stale work chased (`/triage stale`)
- [ ] Parked items revisited
- [ ] Override follow-ups closed
- [ ] One process improvement logged

**Monthly**
- [ ] `PRODUCT.md` current priorities rewritten
- [ ] Old Low items parked
