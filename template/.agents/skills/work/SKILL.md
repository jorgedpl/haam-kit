---
name: work
description: Start an agent in a new chat window — give it its own worktree so parallel chats don't collide, prepare it, then pick the next work item and do it. Use when a human opens a chat to have an agent pick up work, e.g. "/work bugs".
argument-hint: "[bugs|features|specs|ideas|epic <ID>]  (optional: one kind of work, or the Ready items of one epic)"
---

# /work: one chat, one workspace, one issue

> **Tracker:** check `"tracker"` in `haam.config.json` and do every tracker step the way `docs/process/TRACKER.md` says (GitHub Projects: `python3 tools/haam/haam.py issue …`; Linear: the Linear connection). `<ID>` means `#123` (GitHub) or `APP-123` (Linear).

Stream: $ARGUMENTS (empty = all streams)

Several chats working in the same folder overwrite each other's files and branches. So every agent chat that changes code gets its own copy of the repository, a **git worktree**, under `.claude/worktrees/`. The main folder stays with the human's own chat (ideas, decisions, UAT, releases).

## 1. Get your own workspace
Run `python3 tools/haam/haam.py worktree status --json`.
- `"in_worktree": true` → you already have one. Go to step 2.
- Otherwise:
  - **Claude Code:** create and enter a new worktree yourself (the `EnterWorktree` tool, as when a human says "work in a worktree"). Then go to step 2.
  - **A tool with its own worktree or parallel-agent mode** (e.g. the Codex app, Cursor's parallel agents): if the human started this chat that way, `in_worktree` is already true. If not, tell the human to start the chat that way, or use the next option.
  - **Any other tool:** run `python3 tools/haam/haam.py worktree new`. It prints a folder. Tell the human: *"Open `<folder>` in a new window, start your agent there and type `/work <stream>` again."* Then stop.

## 2. Prepare it
1. `python3 tools/haam/haam.py worktree prep`: copies the local-only files listed in `.worktreeinclude` (such as `.env`) from the main folder. Never open, read or print those files.
2. If it says the git secret hook is off, run `make hooks`.
3. If dependencies aren't installed in this worktree yet, run `make setup`.

## 3. Pick and do the work
With `epic <ID>`: if the epic has the label `mode:epic-build` (the owner's decision), build the whole epic as its lead agent (`/build`, *Epic build mode*). Otherwise take that epic's Ready items (bugs, and small features with approved specs) as one batch (`/build` explains the batch: one branch, one PR). Otherwise follow `/next` with the filter above (`bugs`, `features`, `specs` or `ideas`; `/next` says what each takes), in **just-pick mode**: take the top candidate without waiting for a choice, and say in your first line which one and why. Then follow the skill it leads to (`/build`, `/spec`, `/assess` or `/spike`) to the end, including the claim protocol. If the human told you this computer's name, pass it when claiming (`--machine`).

## 4. Hand over
1. When the item reaches its hand-over point (UAT plan ready, spec or assessment waiting for the human), reply with: the ID and title, the branch (test-first) or the PR link (checks-first), and exactly what the human does next (usually: type `/test <ID>` in their own chat).
2. **One issue per chat.** Don't start another item unless the human asked for more (e.g. "and keep going"). If they did, start again at step 3 in this same worktree.
3. Nothing to pick? Report what's waiting on the human, as `/next` does, and stop.

**Never run `ship` from here.** Only the owner's own chat, in the main folder, merges and deploys (`/test`).

Finished worktrees are tidied later with `python3 tools/haam/haam.py worktree clean` (plan), then `--apply`. It only removes worktrees whose work is merged or abandoned and that have nothing unsaved.
