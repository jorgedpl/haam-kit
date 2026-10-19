#!/usr/bin/env python3
"""
HAAM setup tool: Human-Agent Agile Methodology.

One tool that any coding agent (Claude Code, Cursor, Codex, Grok, ...) or human can
run to adopt HAAM in a repository and to onboard new developers.

    python3 tools/haam/haam.py <command> [options]

Admin (first-time adoption and upgrades):
    install   --target DIR     Copy the HAAM kit into a repository (never overwrites)
    update    --target DIR     Upgrade a project to this kit version (keeps your customisations)
    config                     Create/update haam.config.json and apply team key + names
    agents    [--apply]        Wire up Claude Code, Cursor, Codex, Grok, Gemini, Copilot
    github    [--apply]        Labels, branch rules, required checks, production env, security
    linear    [--apply]        Linear team, statuses and labels (needs a Linear API key)
    github-project [--apply]   GitHub Projects board, statuses, priority, labels (tracker: github)
    invite    --github USER [--linear-email EMAIL] [--apply]

Agents, when the tracker is GitHub Projects:
    issue create|view|list|claim|status|priority|label|comment|close|link|unlink|children|edit ...

Testing and shipping (inside /test, after the human's verdict):
    checkout-pr ISSUE | --back              Put a change on this machine to test it (its PR, or the agent's branch)
    publish ISSUE --human                   Test-first: push the tested commit and open its PR (uat-passed)
    ship ISSUE --human [--merged-only]      Merge, approve the production deploy, wait, close (exit 2: run again)

CI cost:
    ci-usage [--days 7]                     Where the Actions minutes went (by workflow, job, trigger, day)
    ci-settings --runner X --review Y       Run CI on your own runner; run the AI reviews locally
    review ISSUE                            Local AI reviews in fresh sessions, posted as the PR's statuses

Parallel chats (one worktree per agent chat):
    worktree status|new|prep|list|clean [--apply]

Everyone:
    version   [--check]                           Kit version here, in the project, and the latest release
    doctor    [--role admin|developer] [--json]   Check what's done and what's missing
    dev       [--apply] [--run-checks]            Developer onboarding on this machine

Safety rules built into the tool:
  * Without --apply nothing is changed: you see the plan first.
  * Secrets are never stored in the repo, printed, or passed through an agent's chat.
    Steps that need one are marked [YOU, in your terminal] for the human to run.
  * Nothing is deleted. Conflicting files are left alone and reported. The one exception,
    `worktree clean --apply`, only removes finished worktrees with nothing unsaved in them.

Requires: Python 3.8+, git. For github/invite: GitHub CLI (`gh`) logged in as a repo admin.

Part of the HAAM kit: https://github.com/jorgedpl/haam-kit
MIT licence. Copyright (c) 2026 Jorge del Prado. See docs/setup/HAAM-LICENSE.md.
"""

import argparse
import getpass
import hashlib
import json
import os
import re
import shutil
import time
import signal
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

VERSION = "1.7.2"
CONFIG_NAME = "haam.config.json"
LOCK_NAME = "haam.lock.json"
KIT_REPO = "jorgedpl/haam-kit"
KIT_URL = f"https://github.com/{KIT_REPO}"
PLACEHOLDER_KEY = "APP"
LINEAR_API = "https://api.linear.app/graphql"
# Test hook: only a local address is accepted, so a stray variable can't send keys elsewhere.
if os.environ.get("HAAM_LINEAR_API", "").startswith("http://127.0.0.1:"):
    LINEAR_API = os.environ["HAAM_LINEAR_API"]
LINEAR_MCP = "https://mcp.linear.app/mcp"

TRACKERS = ("github", "linear")

DEFAULT_CONFIG = {
    "product_name": "",
    "tracker": "linear",
    "github_project_owner": "",
    "github_project_number": None,
    "team_key": PLACEHOLDER_KEY,
    "linear_team_name": "",
    "github_repo": "",
    "default_branch": "main",
    "product_owner_github": "",
    "backup_approvers_github": [],
    "production_url": "",
    "agents": ["claude", "cursor", "codex", "grok"],
    "deploy": "github",          # github: deploy.yml runs on merge; manual: the owner deploys by hand
    "max_open_prs": 10,          # agents hold new work when this many PRs are open (CI minutes and your review time)
    "max_in_uat": 10,            # ...or when this many changes are waiting for the owner to test
    "review": "github",          # github: AI reviews run in Actions; local: `haam.py review` on the owner's computer
    "flow": "test-first",        # test-first: the owner tests locally before any PR exists; checks-first: PR + checks, then test
    "_applied": {"team_key": PLACEHOLDER_KEY, "product_name": ""},
}

REQUIRED_CHECKS = ["ci", "secrets", "dependencies", "ai-review", "security-review", "release-gate"]

GITHUB_LABELS = [
    ("uat-passed", "0E8A16", "Gate G4 passed: human UAT OK"),
    ("gate-override", "B60205", "Human override of G4; needs OVERRIDE: comment"),
    ("human-review", "FBCA04", "Touches protected area; human code review required"),
    ("ai-review-overruled", "5319E7", "Human overrules the AI reviews on this PR"),
]

# (name, Linear state type, colour)
LINEAR_STATES = [
    ("Triage", "triage", "#FC7840"),
    ("Discovery", "backlog", "#BEC2C8"),
    ("Decision", "backlog", "#F2C94C"),
    ("Backlog", "backlog", "#95A2B3"),
    ("Ready", "unstarted", "#E2E2E2"),
    ("In Progress", "started", "#F2C94C"),
    ("In Review", "started", "#5E6AD2"),
    ("UAT", "started", "#26B5CE"),
    ("Deploying", "started", "#4CB782"),
    ("Done", "completed", "#5E6AD2"),
    ("Parked", "canceled", "#95A2B3"),
    ("Canceled", "canceled", "#95A2B3"),
]

LINEAR_LABELS = [
    ("stream:idea", "#BB87FC", "New idea, not yet decided"),
    ("stream:feature", "#4EA7FC", "Approved work"),
    ("stream:bug", "#EB5757", "Something is broken"),
    ("agent-ready", "#4CB782", "Passed G2: agents may build it"),
    ("human-review", "#F2C94C", "Touches a protected area: human code review required"),
    ("human-only", "#95A2B3", "Agents must not pick this up"),
    ("override-followup", "#FC7840", "Created after a gate override"),
    ("epic", "#3E4B9E", "Groups the issues that make up one feature (its sub-issues)"),
    ("uat-failed", "#D93F0B", "Failed the human test: rework first, then test again"),
]

# Files the rename step rewrites (team key / product name)
RENAME_ROOTS = ["AGENTS.md", "CLAUDE.md", ".agents", ".github", "docs"]
TEXT_SUFFIXES = {".md", ".yml", ".yaml", ".json", ".sh", ".txt", ".toml", ""}

SKILL_LINKS = [".claude/skills", ".grok/skills"]
GITIGNORE_MARK = "# --- HAAM ---"
GITIGNORE_END = "# --- /HAAM ---"

# ----------------------------------------------------------------------------- output

USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def c(code, text):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


OK, WARN, BAD, INFO = c("32", "✔"), c("33", "!"), c("31", "✘"), c("36", "•")
WHO_AGENT = "[agent]"
WHO_TERMINAL = "[YOU, in your terminal]"
WHO_BROWSER = "[YOU, in the browser]"


class Report:
    """Collects results so the same data can be printed for humans or as JSON for agents."""

    def __init__(self):
        self.sections = []
        self.actions = []

    def section(self, title):
        self.sections.append({"title": title, "items": []})

    def add(self, status, text, detail=""):
        if not self.sections:
            self.section("General")
        self.sections[-1]["items"].append({"status": status, "text": text, "detail": detail})

    def action(self, who, text, command=""):
        self.actions.append({"who": who, "text": text, "command": command})

    def counts(self):
        out = {"ok": 0, "warn": 0, "fail": 0, "info": 0}
        for s in self.sections:
            for i in s["items"]:
                out[i["status"]] = out.get(i["status"], 0) + 1
        return out

    def print(self, as_json=False):
        if as_json:
            print(json.dumps({"version": VERSION, "sections": self.sections,
                              "next_actions": self.actions, "counts": self.counts()}, indent=2))
            return
        sym = {"ok": OK, "warn": WARN, "fail": BAD, "info": INFO}
        for s in self.sections:
            print(f"\n{c('1', s['title'])}")
            for i in s["items"]:
                line = f"  {sym.get(i['status'], INFO)} {i['text']}"
                if i["detail"]:
                    line += c("2", f"  ({i['detail']})")
                print(line)
        if self.actions:
            print(f"\n{c('1', 'Next actions')}")
            for n, a in enumerate(self.actions, 1):
                print(f"  {n}. {c('1', a['who'])} {a['text']}")
                if a["command"]:
                    print(f"       {c('36', a['command'])}")
        cnt = self.counts()
        summary = f"{cnt['ok']} ok · {cnt['warn']} to check · {cnt['fail']} missing"
        print("\n" + c("2", summary))


# ----------------------------------------------------------------------------- helpers

def run(cmd, cwd=None, input_text=None, check=False):
    """Run a command, return (code, stdout, stderr). Never raises for missing binaries."""
    try:
        p = subprocess.run(cmd, cwd=cwd, input=input_text, capture_output=True, text=True)
    except FileNotFoundError:
        return 127, "", f"{cmd[0]}: not installed"
    if check and p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip())
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def have(binary):
    return shutil.which(binary) is not None


def kit_root():
    return Path(__file__).resolve().parents[2]


def find_repo_root(start):
    code, out, _ = run(["git", "rev-parse", "--show-toplevel"], cwd=start)
    return Path(out) if code == 0 else Path(start).resolve()


def load_config(root):
    p = root / CONFIG_NAME
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    if p.exists():
        try:
            data = json.loads(p.read_text())
            cfg.update(data)
            cfg.setdefault("_applied", {"team_key": PLACEHOLDER_KEY, "product_name": ""})
        except json.JSONDecodeError as e:
            sys.exit(f"{CONFIG_NAME} is not valid JSON: {e}")
    return cfg


def save_config(root, cfg):
    (root / CONFIG_NAME).write_text(json.dumps(cfg, indent=2) + "\n")


def detect_github_repo(root):
    code, url, _ = run(["git", "remote", "get-url", "origin"], cwd=root)
    if code != 0:
        return ""
    m = re.search(r"github\.com[:/]+([^/]+/[^/.]+?)(?:\.git)?$", url)
    return m.group(1) if m else ""


def iter_text_files(root, rel_roots):
    for rel in rel_roots:
        base = root / rel
        if base.is_file():
            yield base
        elif base.is_dir():
            for p in base.rglob("*"):
                if p.is_file() and not p.is_symlink() and p.suffix in TEXT_SUFFIXES:
                    yield p


def todo_count(root):
    hits = []
    for p in iter_text_files(root, ["AGENTS.md", "Makefile", "docs", ".github"]):
        try:
            for n, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
                if "TODO(setup)" in line:
                    hits.append(f"{p.relative_to(root)}:{n}")
        except OSError:
            pass
    return hits


def is_tty():
    return sys.stdin.isatty() and sys.stdout.isatty()


def ask(prompt, default=""):
    if not is_tty():
        return default
    suffix = f" [{default}]" if default else ""
    val = input(f"{prompt}{suffix}: ").strip()
    return val or default


# ----------------------------------------------------------------------------- install

def merge_json(dst, src_bytes, merger):
    try:
        a = json.loads(dst.read_text())
        b = json.loads(src_bytes)
    except (json.JSONDecodeError, OSError):
        return False
    before = json.dumps(a, sort_keys=True)
    merged = merger(a, b)
    if json.dumps(merged, sort_keys=True) == before:
        return "same"
    dst.write_text(json.dumps(merged, indent=2) + "\n")
    return True


def merge_mcp(a, b):
    a.setdefault("mcpServers", {})
    for k, v in b.get("mcpServers", {}).items():
        a["mcpServers"].setdefault(k, v)
    return a


def merge_gemini(a, b):
    ctx = a.setdefault("context", {})
    names = ctx.get("fileName", [])
    if isinstance(names, str):
        names = [names]
    for n in b.get("context", {}).get("fileName", []):
        if n not in names:
            names.append(n)
    ctx["fileName"] = names
    return a


def merge_claude_settings(a, b):
    perms_a = a.setdefault("permissions", {})
    for key, vals in b.get("permissions", {}).items():
        cur = perms_a.setdefault(key, [])
        for v in vals:
            if v not in cur:
                cur.append(v)
    for key in ("enabledMcpjsonServers",):
        cur = a.setdefault(key, [])
        for v in b.get(key, []):
            if v not in cur:
                cur.append(v)
    a.setdefault("enableAllProjectMcpServers", b.get("enableAllProjectMcpServers", False))
    hooks_a = a.setdefault("hooks", {})
    for event, entries in b.get("hooks", {}).items():
        cur = hooks_a.setdefault(event, [])
        existing_cmds = {h.get("command", "") for entry in cur for h in entry.get("hooks", [])}
        for e in entries:
            cmds = [h.get("command", "") for h in e.get("hooks", [])]
            if not all(cmd in existing_cmds for cmd in cmds):
                cur.append(e)
    return a


LINEAR_FILES = (".mcp.json", ".cursor/mcp.json", ".claude/settings.json")


def without_linear(data, keep_enabled=False):
    """A kit JSON file minus its Linear connection (for projects that track work on GitHub). A server called
    "linear" that isn't Linear's own (a project's proxy, say) is left alone, and so is its switch when keep_enabled."""
    servers = data.get("mcpServers")
    if isinstance(servers, dict) and LINEAR_MCP in json.dumps(servers.get("linear", {})):
        servers.pop("linear")
    if isinstance(data.get("enabledMcpjsonServers"), list) and not keep_enabled:
        data["enabledMcpjsonServers"] = [x for x in data["enabledMcpjsonServers"] if x != "linear"]
    return data


def remove_linear_connection(root, apply=True):
    """GitHub-tracker projects don't use Linear: take the kit's Linear connection out of the MCP and Claude settings
    (a file that held nothing else is removed, and forgotten in the lock so switching to Linear later restores it).
    Returns the files changed. Other servers are left alone."""
    changed, own_linear = [], False
    for rel in LINEAR_FILES:          # the MCP files first: they decide whether a project's own "linear" stays on
        f = root / rel
        if not f.exists():
            continue
        try:
            data = json.loads(f.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        before = json.dumps(data, sort_keys=True)
        data = without_linear(data, keep_enabled=own_linear)
        if rel == ".mcp.json" and "linear" in (data.get("mcpServers") or {}):
            own_linear = True
        if json.dumps(data, sort_keys=True) == before:
            continue
        changed.append(rel)
        if apply:
            if rel != ".claude/settings.json" and data == {"mcpServers": {}}:
                f.unlink()
                if (root / LOCK_NAME).exists():
                    lock = load_lock(root)
                    if lock.get("files", {}).pop(rel, None) is not None:
                        save_lock(root, lock)
            else:
                f.write_text(json.dumps(data, indent=2) + "\n")
    return changed


JSON_MERGERS = {
    ".mcp.json": merge_mcp,
    ".cursor/mcp.json": merge_mcp,
    ".gemini/settings.json": merge_gemini,
    ".claude/settings.json": merge_claude_settings,
}

def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_lock(root):
    p = root / LOCK_NAME
    if p.exists():
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError:
            pass
    return {"kit_version": None, "kit_repo": KIT_REPO, "files": {}}


def save_lock(root, lock):
    lock["files"] = dict(sorted(lock["files"].items()))
    (root / LOCK_NAME).write_text(json.dumps(lock, indent=2) + "\n")


def make_renderer(target):
    """Return render(path, rel) -> bytes: kit file content as it should look in this project."""
    tcfg = load_config(target) if (target / CONFIG_NAME).exists() else None
    applied_key = (tcfg or {}).get("_applied", {}).get("team_key", PLACEHOLDER_KEY)
    applied_product = (tcfg or {}).get("_applied", {}).get("product_name", "")
    github_tracker = (tcfg or {}).get("tracker") == "github"
    # The project removed the .mcp.json the kit installed: don't switch on servers it no longer declares.
    mcp_removed = ".mcp.json" in (load_lock(target).get("files") or {}) and not (target / ".mcp.json").exists()

    def render(path, rel_s):
        data = path.read_bytes()
        if github_tracker and rel_s in LINEAR_FILES:
            kit = without_linear(json.loads(data))
            if kit == {"mcpServers": {}}:
                return None          # nothing left for this project: don't install the file
            return (json.dumps(kit, indent=2) + "\n").encode()
        if mcp_removed and rel_s == ".claude/settings.json":
            kit = json.loads(data)
            kit["enabledMcpjsonServers"] = []
            return (json.dumps(kit, indent=2) + "\n").encode()
        in_scope = any(rel_s == r or rel_s.startswith(r + "/") for r in RENAME_ROOTS)
        if not in_scope or path.suffix not in TEXT_SUFFIXES or (applied_key == PLACEHOLDER_KEY and not applied_product):
            return data
        try:
            text = data.decode()
        except UnicodeDecodeError:
            return data
        if applied_key != PLACEHOLDER_KEY:
            text = re.sub(rf"\b{PLACEHOLDER_KEY}\b", applied_key, text)
            text = re.sub(rf"\b{PLACEHOLDER_KEY.lower()}-(\d)", lambda m: f"{applied_key.lower()}-{m.group(1)}", text)
            text = text.replace(" (`TODO(setup)`: replace with your team key everywhere)", "")
        if applied_product:
            text = text.replace("`TODO(setup): product name`", applied_product)
        return text.encode()
    return render


def kit_files(src):
    """Files the kit installs, as (path, posix relative path)."""
    for p in sorted(src.rglob("*")):
        rel = p.relative_to(src)
        rel_s = rel.as_posix()
        if rel.parts[0] in (".git", ".haam") or rel_s in INSTALL_SKIP or "__pycache__" in rel.parts:
            continue
        if p.is_symlink() or p.is_dir():
            continue  # links are created by `agents`; dirs are created as needed
        if any(rel_s.startswith(l + "/") or rel_s == l for l in SKILL_LINKS):
            continue
        yield p, rel_s


def sync_gitignore(src, target, dry_run):
    """Add or refresh the HAAM block in .gitignore, plus re-include lines for kit files the project's own
    rules would hide. Those go in a separate block kept at the very end of the file: in .gitignore the
    last matching rule wins, so they must come after every project rule. Returns True if it changed."""
    add_path = src / ".gitignore.additions"
    if not add_path.exists():
        return False
    gi = target / ".gitignore"
    current = gi.read_text() if gi.exists() else ""

    def cut(text, start_mark, end_mark):
        """(text without the marked block, the block's non-empty lines)."""
        if start_mark not in text:
            return text, []
        i = text.index(start_mark)
        j = text.find(end_mark, i)
        inner, after = (text[i + len(start_mark):], "") if j == -1 else (text[i + len(start_mark):j], text[j + len(end_mark):])
        return text[:i] + after.lstrip("\n"), [l.strip() for l in inner.splitlines() if l.strip()]

    body, old_unhide = cut(current, UNHIDE_MARK, UNHIDE_END)
    keep_neg = [l for l in old_unhide if l.startswith("!/")]
    block = f"{GITIGNORE_MARK}\n{add_path.read_text().rstrip()}\n{GITIGNORE_END}\n"
    if GITIGNORE_MARK in body:
        start = body.index(GITIGNORE_MARK)
        end = body.find(GITIGNORE_END, start)
        end = len(body) if end == -1 else end + len(GITIGNORE_END)
        new = body[:start] + block.rstrip("\n") + body[end:]
    else:
        new = body + ("\n" if body and not body.endswith("\n") else "") + ("\n" if body.strip() else "") + block
    new = new.rstrip("\n") + "\n"
    # Which kit files would the project's rules hide? Check against the file without our re-include lines.
    neg = list(keep_neg)
    if not dry_run or gi.exists():
        saved = current
        gi.write_text(new)
        try:
            for line in unignore_lines(target, [r for _, r in kit_files(src)]):
                if line not in neg:
                    neg.append(line)
        finally:
            if dry_run:
                gi.write_text(saved)
    if neg:
        new += "\n" + UNHIDE_MARK + "\n" + "\n".join(neg) + "\n" + UNHIDE_END + "\n"
    if new == current:
        return False
    if not dry_run:
        gi.write_text(new)
    return True

def make_executable(target, src=None):
    """Make the kit's own executable files executable in the project. Never touches the project's files."""
    src = src or kit_root()
    for p, rel_s in kit_files(src):
        dst = target / rel_s
        if p.stat().st_mode & 0o111 and dst.exists() and dst.is_file():
            dst.chmod(dst.stat().st_mode | 0o111)


def ignored_paths(target, rels):
    """Which of these paths the project's .gitignore hides (so they would never be committed)."""
    if not rels or run(["git", "rev-parse", "--git-dir"], cwd=target)[0] != 0:
        return set()
    code, out, _ = run(["git", "check-ignore", "--stdin"], cwd=target, input_text="\n".join(rels) + "\n")
    return {l.strip() for l in out.splitlines() if l.strip()} if code in (0, 1) else set()


def unignore_lines(target, rels):
    """.gitignore negations that re-include kit files hidden by the project's own rules (e.g. '**/build/'
    hides .agents/skills/build/). A negation must name the highest ignored folder, so walk up each path."""
    hidden = ignored_paths(target, rels)
    lines = []
    for rel in sorted(hidden):
        parts = rel.split("/")
        top = rel
        for k in range(1, len(parts)):
            d = "/".join(parts[:k]) + "/"
            if ignored_paths(target, [d]):
                top = d
                break
        line = f"!/{top}"
        if line not in lines:
            lines.append(line)
    return lines


INSTALL_SKIP = {".gitignore.additions", "START-HERE.md"}
UNHIDE_MARK = "# >>> HAAM: kit files your own rules would hide (kept last so they win; every machine needs them)"
UNHIDE_END = "# <<< HAAM re-include"


def cmd_install(args):
    src = kit_root()
    target = Path(args.target).resolve()
    if not (src / "AGENTS.md").exists():
        sys.exit(f"Can't find the HAAM kit next to this tool (looked in {src}).")
    if not (target / ".git").exists():
        sys.exit(f"{target} is not a git repository. Run this against your project's root folder.")
    if src == target:
        sys.exit("Source and target are the same folder.")
    if (target / LOCK_NAME).exists():
        lv = load_lock(target).get("kit_version")
        print(f"HAAM {lv} is already installed here. Use `update` to move to {VERSION}; continuing as a re-install check.\n")

    rep = Report()
    rep.section(f"Installing HAAM {VERSION} into {target}")
    render = make_renderer(target)
    lock = load_lock(target)
    incoming = target / ".haam" / "incoming"
    created, same, merged, conflicts = [], [], [], []

    for p, rel_s in kit_files(src):
        dst = target / rel_s
        content = render(p, rel_s)
        if content is None:
            continue
        lock["files"][rel_s] = sha(content)
        if not dst.exists():
            if not args.dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(content)
                shutil.copymode(p, dst)
            created.append(rel_s)
            continue
        if dst.read_bytes() == content:
            same.append(rel_s)
            continue
        if rel_s in JSON_MERGERS:
            result = "dry" if args.dry_run else merge_json(dst, content, JSON_MERGERS[rel_s])
            if result == "same":
                same.append(rel_s)
                continue
            if result:
                merged.append(rel_s)
                continue
        conflicts.append(rel_s)
        if not args.dry_run:
            out = incoming / rel_s
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(content)

    if sync_gitignore(src, target, args.dry_run):
        merged.append(".gitignore")
    if not args.dry_run:
        make_executable(target)
        lock["kit_version"] = VERSION
        lock["kit_repo"] = KIT_REPO
        save_lock(target, lock)

    rep.add("ok", f"{len(created)} files added")
    if merged:
        rep.add("ok", f"{len(merged)} existing files merged automatically", ", ".join(merged))
    if same:
        rep.add("info", f"{len(same)} files already up to date")
    for cf in conflicts:
        rep.add("warn", f"Kept your existing {cf}", f"kit version saved to .haam/incoming/{cf}")
    rep.add("info", f"Kit version {VERSION} recorded in {LOCK_NAME} (commit it)")
    if conflicts:
        rep.action(WHO_AGENT, "Merge each conflicting file using the kit version in .haam/incoming/ "
                   "(rules in docs/setup/HAAM-ADOPTION-GUIDE.md, Phase 1 table). For an existing CLAUDE.md or AGENTS.md: "
                   "move project-specific content into docs/product/ARCHITECTURE.md (or a 'Project specifics' "
                   "section at the end of AGENTS.md), then use the kit version. Delete .haam/incoming when done.")
    rep.action(WHO_AGENT, "Wire up the agent tools (skills links, MCP configs)", "python3 tools/haam/haam.py agents --apply")
    rep.action(WHO_AGENT, "Create the project config with the human's answers", "python3 tools/haam/haam.py config")
    if args.dry_run:
        rep.add("info", "Dry run: nothing was written")
    rep.print(args.json)


def version_tuple(v):
    m = re.match(r"v?(\d+)\.(\d+)\.(\d+)", v or "")
    return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)


def cmd_update(args):
    src = kit_root()
    target = Path(args.target).resolve()
    if not (src / "AGENTS.md").exists():
        sys.exit(f"Can't find the HAAM kit next to this tool (looked in {src}).")
    if src == target:
        sys.exit("Run the NEW kit's tool against your project: python3 <new-kit>/template/tools/haam/haam.py update --target .")
    if not (target / "AGENTS.md").exists():
        sys.exit("HAAM isn't installed in that folder. Use `install` first.")

    lock = load_lock(target)
    old = lock.get("kit_version") or "unknown"
    rep = Report()
    rep.section(f"Updating HAAM {old} → {VERSION} in {target}")
    if old != "unknown" and version_tuple(old) > version_tuple(VERSION):
        sys.exit(f"The project has HAAM {old}, newer than this kit ({VERSION}). Use a newer kit.")
    if version_tuple(VERSION)[0] > version_tuple(old)[0] and old != "unknown":
        rep.add("warn", f"Major version change ({old} → {VERSION})",
                "read the migration notes in the kit's CHANGELOG before applying")

    render = make_renderer(target)
    incoming = target / ".haam" / "incoming"
    added, updated, kept, conflicts, merged, same, skipped = [], [], [], [], [], [], []
    hidden = ignored_paths(target, [r for _, r in kit_files(src)])
    unhidden = []
    seen = set()
    new_lock = dict(lock.get("files", {}))

    for p, rel_s in kit_files(src):
        seen.add(rel_s)
        dst = target / rel_s
        new = render(p, rel_s)
        base = lock.get("files", {}).get(rel_s)
        if new is None:              # not used by this project (e.g. the Linear connection on a GitHub tracker)
            new_lock.pop(rel_s, None)
            continue
        if rel_s in JSON_MERGERS and dst.exists():
            result = "dry" if args.dry_run or not args.apply else merge_json(dst, new, JSON_MERGERS[rel_s])
            (same if result == "same" else merged).append(rel_s)
            new_lock[rel_s] = sha(new)
            continue
        if not dst.exists():
            if base is not None and rel_s not in hidden:
                skipped.append(rel_s)  # project deliberately removed it
                continue
            if rel_s in hidden:
                unhidden.append(rel_s)
            added.append(rel_s)
            if args.apply:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(new)
                shutil.copymode(p, dst)
            new_lock[rel_s] = sha(new)
            continue
        cur = dst.read_bytes()
        if cur == new:
            same.append(rel_s)
            new_lock[rel_s] = sha(new)
        elif base is not None and sha(cur) == base:
            updated.append(rel_s)  # untouched by the project: safe to replace
            if args.apply:
                dst.write_bytes(new)
                shutil.copymode(p, dst)
            new_lock[rel_s] = sha(new)
        elif base is not None and sha(new) == base:
            kept.append(rel_s)  # project customised it; kit didn't change it
        else:
            conflicts.append(rel_s)  # both changed (or no record): needs a merge
            if args.apply:
                out = incoming / rel_s
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(new)
            new_lock[rel_s] = sha(new)

    removed = sorted(r for r in lock.get("files", {}) if r not in seen)
    for r in removed:
        new_lock.pop(r, None)

    gi_changed = sync_gitignore(src, target, dry_run=not args.apply)
    tcfg = load_config(target) if (target / CONFIG_NAME).exists() else {}
    unlinked = remove_linear_connection(target, apply=args.apply) if tcfg.get("tracker") == "github" else []

    rep.add("ok" if added else "info", f"{len(added)} new files", ", ".join(added[:8]) + (" …" if len(added) > 8 else ""))
    rep.add("ok" if updated else "info", f"{len(updated)} files updated (you hadn't changed them)",
            ", ".join(updated[:8]) + (" …" if len(updated) > 8 else ""))
    if merged:
        rep.add("ok", f"{len(merged)} settings files merged", ", ".join(merged))
    if gi_changed:
        rep.add("ok", ".gitignore HAAM block refreshed")
    if unlinked:
        rep.add("ok", "Linear connection taken out (this project tracks work on GitHub)", ", ".join(unlinked))
    rep.add("info", f"{len(same)} files already current")
    if kept:
        rep.add("info", f"{len(kept)} of your customised files kept (no kit change)", ", ".join(kept[:8]))
    for r in skipped:
        rep.add("info", f"Skipped {r}", "you removed it; not re-added")
    if hidden:
        rep.add("warn", f"{len(hidden)} kit file(s) were hidden by your .gitignore", ", ".join(sorted(hidden)[:6])
                + (" …" if len(hidden) > 6 else "") + " · the HAAM block in .gitignore now re-includes them; commit them")
    for r in unhidden:
        rep.add("ok", f"Restored {r}", "it was missing because .gitignore hid it, not because you removed it")
    for r in conflicts:
        rep.add("warn", f"Needs a merge: {r}", f"you and the kit both changed it; new kit version → .haam/incoming/{r}")
    for r in removed:
        rep.add("warn", f"No longer in the kit: {r}", "delete it if you don't use it (nothing is deleted automatically)")

    if args.apply:
        make_executable(target)
        lock["files"] = new_lock
        lock["kit_version"] = VERSION
        lock["kit_repo"] = KIT_REPO
        save_lock(target, lock)
        rep.add("ok", f"{LOCK_NAME} now records {VERSION}")
    else:
        rep.add("info", "Plan only. Re-run with --apply (on a branch) to update")

    if conflicts:
        rep.action(WHO_AGENT, "Merge each file in .haam/incoming/ into the project's version, keeping the project's "
                   "customisations and adopting the kit's changes. Show the human what changed. Delete .haam/incoming when done.")
    rep.action(WHO_AGENT, f"Read the kit CHANGELOG entries after {old} for migration steps (e.g. new required checks or "
               "Linear statuses), then re-run the plans", "python3 tools/haam/haam.py github  ·  python3 tools/haam/haam.py linear")
    rep.action(WHO_AGENT, "Check everything", "python3 tools/haam/haam.py agents --apply && python3 tools/haam/haam.py doctor")
    rep.print(args.json)


def latest_release():
    """Latest published kit release tag, or None (no network, rate limit, etc.)."""
    req = urllib.request.Request(f"https://api.github.com/repos/{KIT_REPO}/releases/latest",
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "haam-tool"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()).get("tag_name")
    except Exception:
        return None


def cmd_version(args):
    root = find_repo_root(Path.cwd())
    lock = load_lock(root)
    info = {"tool": VERSION, "project": lock.get("kit_version"), "latest": None}
    if args.check:
        info["latest"] = latest_release()
    if args.json:
        print(json.dumps(info, indent=2))
        return
    print(f"HAAM tool:        {VERSION}")
    print(f"This project:     {info['project'] or 'not recorded (no haam.lock.json)'}")
    if args.check:
        latest = info["latest"]
        print(f"Latest release:   {latest or 'unknown (offline or not published yet)'}")
        if latest and info["project"] and version_tuple(latest) > version_tuple(info["project"]):
            print(f"\nUpdate available. See {KIT_URL}/releases and run /haam-update.")


# ----------------------------------------------------------------------------- config

def apply_renames(root, cfg, rep, dry_run=False):
    old_key = cfg["_applied"].get("team_key", PLACEHOLDER_KEY)
    new_key = cfg["team_key"].upper()
    changed = 0
    key_re = re.compile(rf"\b{re.escape(old_key)}\b")
    branch_re = re.compile(rf"\b{re.escape(old_key.lower())}-(\d)")
    product = cfg.get("product_name", "")
    lock = load_lock(root)
    lock_changed = False
    for p in iter_text_files(root, RENAME_ROOTS):
        try:
            text = p.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        new = text
        if old_key != new_key:
            new = key_re.sub(new_key, new)
            new = branch_re.sub(lambda m: f"{new_key.lower()}-{m.group(1)}", new)
        if product:
            new = new.replace("`TODO(setup): product name`", product)
        if new_key != PLACEHOLDER_KEY:
            new = new.replace(" (`TODO(setup)`: replace with your team key everywhere)", "")
        if new != text:
            changed += 1
            if not dry_run:
                p.write_text(new)
                rel = p.relative_to(root).as_posix()
                # Keep the lock in step: a kit file renamed by config is still "unmodified by the project".
                if lock["files"].get(rel) == sha(text.encode()):
                    lock["files"][rel] = sha(new.encode())
                    lock_changed = True
    if lock_changed:
        save_lock(root, lock)
    if not dry_run:
        cfg["_applied"]["team_key"] = new_key
        if product:
            cfg["_applied"]["product_name"] = product
    if old_key != new_key:
        rep.add("ok", f"Team key {old_key} → {new_key} applied", f"{changed} files updated")
    elif changed:
        rep.add("ok", "Product name applied", f"{changed} files updated")


def cmd_config(args):
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    rep = Report()
    rep.section("Project configuration")

    detected = detect_github_repo(root)
    if args.tracker is not None:
        if args.tracker not in TRACKERS:
            sys.exit(f"--tracker must be one of: {', '.join(TRACKERS)}")
        cfg["tracker"] = args.tracker
    elif not (root / CONFIG_NAME).exists() and is_tty():
        t = ask("Where do you track work: github (GitHub Projects, free) or linear", "github").lower()
        cfg["tracker"] = t if t in TRACKERS else "github"
    if args.project_number is not None:
        cfg["github_project_number"] = int(args.project_number)
    if args.project_owner is not None:
        cfg["github_project_owner"] = args.project_owner
    fields = [
        ("product_name", args.product, "Product name (e.g. Acme)"),
        ("team_key", args.team_key, "Short product key, 2-5 capital letters (e.g. ACM); used as the Linear team key"),
        ("linear_team_name", args.linear_team if cfg.get("tracker") == "linear" else (args.linear_team or None),
         "Linear team name"),
        ("github_repo", args.github_repo or (detected if not cfg["github_repo"] else None), "GitHub repo owner/name"),
        ("product_owner_github", args.owner, "Product owner's GitHub username (approves deploys)"),
        ("production_url", args.production_url, "Production URL (for the smoke test; blank if none)"),
    ]
    for key, flag_val, prompt in fields:
        if flag_val is not None and flag_val != "":
            cfg[key] = flag_val
        elif not cfg.get(key) and is_tty():
            default = ""
            if key == "linear_team_name":
                default = cfg.get("product_name", "")
            if key == "team_key":
                default = cfg.get("team_key", "")
            cfg[key] = ask(prompt, default)
    if args.backup_approvers is not None:
        cfg["backup_approvers_github"] = [x.strip() for x in args.backup_approvers.split(",") if x.strip()]
    if args.agents is not None:
        cfg["agents"] = [x.strip().lower() for x in args.agents.split(",") if x.strip()]
    if args.flow is not None:
        if args.flow not in ("test-first", "checks-first"):
            sys.exit("--flow must be test-first (owner tests before the PR) or checks-first (PR and checks, then test)")
        cfg["flow"] = args.flow
    if args.deploy is not None:
        if args.deploy not in ("github", "manual"):
            sys.exit("--deploy must be github (deploy.yml runs on merge) or manual (you deploy by hand)")
        cfg["deploy"] = args.deploy
    for key, val in (("max_open_prs", args.max_open_prs), ("max_in_uat", args.max_in_uat)):
        if val is not None:
            cfg[key] = int(val)

    cfg["team_key"] = (cfg.get("team_key") or PLACEHOLDER_KEY).upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9]{1,6}", cfg["team_key"]):
        sys.exit(f"Team key '{cfg['team_key']}' should be 2-7 capital letters/digits, starting with a letter.")
    if cfg["github_repo"] and not re.fullmatch(r"[\w.-]+/[\w.-]+", cfg["github_repo"]):
        sys.exit(f"github_repo should look like owner/name, got '{cfg['github_repo']}'.")
    if not cfg.get("linear_team_name"):
        cfg["linear_team_name"] = cfg.get("product_name", "")

    apply_renames(root, cfg, rep, dry_run=args.dry_run)
    if not args.dry_run:
        save_config(root, cfg)
    if cfg.get("tracker") == "github":
        unlinked = remove_linear_connection(root, apply=not args.dry_run)
        if unlinked:
            rep.add("ok", "Linear connection taken out (work is tracked on GitHub)", ", ".join(unlinked))

    missing = [k for k in ("product_name", "github_repo", "product_owner_github") if not cfg.get(k)]
    for k in ("product_name", "tracker", "team_key", "github_repo", "product_owner_github",
              "production_url", "agents", "deploy", "flow", "max_open_prs", "max_in_uat") + (("linear_team_name",) if cfg.get("tracker") == "linear" else ()):
        v = cfg.get(k)
        rep.add("ok" if v else "warn", f"{k}: {v if v else '(not set)'}")
    if missing:
        rep.action(WHO_AGENT, "Ask the human for the missing values, then re-run with flags",
                   "python3 tools/haam/haam.py config --product NAME --tracker github --team-key KEY --github-repo owner/name --owner USER")
    if not missing:
        nxt = "github-project" if cfg.get("tracker") == "github" else "linear"
        rep.action(WHO_AGENT if nxt == "github-project" else WHO_TERMINAL,
                   f"Set up the tracker ({'GitHub Projects' if nxt == 'github-project' else 'Linear'})",
                   f"python3 tools/haam/haam.py {nxt}  →  then with --apply")
    rep.add("info", f"Saved to {CONFIG_NAME} (commit it; it holds no secrets)" if not args.dry_run else "Dry run: not saved")
    rep.print(args.json)


# ----------------------------------------------------------------------------- agents

def ensure_skill_link(root, rel, apply, rep):
    link = root / rel
    target_rel = os.path.relpath(root / ".agents" / "skills", link.parent)
    if link.is_symlink():
        if os.readlink(link) == target_rel and link.resolve() == (root / ".agents/skills").resolve():
            rep.add("ok", f"{rel} → .agents/skills")
            return
        rep.add("warn", f"{rel} is a link to something else", os.readlink(link))
        return
    if link.is_dir():
        # Existing real folder: move its skills into .agents/skills (no overwrite), then link.
        extra = [d for d in link.iterdir() if not (root / ".agents/skills" / d.name).exists()]
        clash = [d.name for d in link.iterdir() if (root / ".agents/skills" / d.name).exists()]
        if not apply:
            rep.add("warn", f"{rel} is a folder", f"would move {len(extra)} skill(s) to .agents/skills, then link"
                    + (f"; name clashes kept in place: {', '.join(clash)}" if clash else ""))
            return
        if clash:
            rep.add("fail", f"{rel}: skills with the same name as HAAM skills", ", ".join(clash))
            rep.action(WHO_AGENT, f"Rename these skills in {rel} so they don't clash, then re-run agents --apply",
                       ", ".join(clash))
            return
        for d in extra:
            shutil.move(str(d), str(root / ".agents/skills" / d.name))
        link.rmdir()
    if not apply:
        rep.add("warn", f"{rel} missing", "would link to .agents/skills")
        return
    link.parent.mkdir(parents=True, exist_ok=True)
    try:
        link.symlink_to(target_rel, target_is_directory=True)
        rep.add("ok", f"{rel} → .agents/skills (linked)")
    except OSError:
        shutil.copytree(root / ".agents/skills", link)
        rep.add("warn", f"{rel}: copied (this system can't create links)",
                "re-run `haam.py agents --apply` after changing any skill")


def cmd_agents(args):
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    rep = Report()
    rep.section("Shared rules and skills")
    rep.add("ok" if (root / "AGENTS.md").exists() else "fail", "AGENTS.md (rules for every agent)")
    skills = sorted(p.parent.name for p in (root / ".agents/skills").glob("*/SKILL.md"))
    rep.add("ok" if skills else "fail", f".agents/skills: {len(skills)} skills", ", ".join(skills))
    for rel in SKILL_LINKS:
        ensure_skill_link(root, rel, args.apply, rep)

    hook_on = secret_hook_on(root)
    rep.add("ok" if hook_on else "warn", "Git pre-commit secret hook (works for every agent that commits with git)",
            "on" if hook_on else "off on this machine: run `make hooks`")

    agents = cfg.get("agents") or DEFAULT_CONFIG["agents"]
    guide = "docs/setup/AGENTS-SETUP.md"
    linear = cfg.get("tracker") != "github"
    if not linear:
        unlinked = remove_linear_connection(root, apply=args.apply)
        rep.section("Tracker")
        rep.add("ok" if not unlinked or args.apply else "warn", "GitHub Projects: no Linear connection",
                ("removed from " if args.apply else "will remove from ") + ", ".join(unlinked) if unlinked else "")

    def present(*names):
        return any(have(n) for n in names)

    if "claude" in agents:
        rep.section("Claude Code")
        cm = root / "CLAUDE.md"
        points = cm.exists() and "AGENTS.md" in cm.read_text(errors="ignore")
        rep.add("ok" if points else "fail", "CLAUDE.md points to AGENTS.md",
                "" if points else ("missing" if not cm.exists() else "it's your old CLAUDE.md: merge it (see .haam/incoming)"))
        rep.add("ok" if (root / ".claude/settings.json").exists() else "fail",
                ".claude/settings.json (guard-rails + hooks)")
        if linear:
            rep.add("ok" if (root / ".mcp.json").exists() else "fail", ".mcp.json declares Linear")
        rep.add("info", "CLI " + ("found" if present("claude") else "not found on this machine"))
    if "cursor" in agents:
        rep.section("Cursor")
        rep.add("ok", "Reads AGENTS.md and .agents/skills natively")
        if linear:
            rep.add("ok" if (root / ".cursor/mcp.json").exists() else "fail", ".cursor/mcp.json declares Linear")
        rep.add("info", "Cursor also reads .claude/skills for compatibility; if skills show twice, "
                        "disable 'Claude skills' compatibility in Cursor settings", "")
    if "codex" in agents:
        rep.section("Codex")
        rep.add("ok", "Reads AGENTS.md and .agents/skills natively")
        policies = list((root / ".agents/skills").glob("*/agents/openai.yaml"))
        rep.add("ok" if len(policies) >= 4 else "warn", f"Human-only skills marked explicit-only: {len(policies)}")
        if linear:
            rep.add("info", "Linear MCP is configured per user (not per repo) in Codex")
            rep.action(WHO_TERMINAL, "Each Codex user connects Linear once", f"codex mcp add linear --url {LINEAR_MCP}")
    if "grok" in agents:
        rep.section("Grok Build")
        rep.add("ok" if (root / ".grok/skills").exists() else "warn", ".grok/skills → .agents/skills")
        if linear:
            rep.add("ok" if (root / ".mcp.json").exists() else "warn", "Linear via .mcp.json (Grok reads it)")
        rep.add("warn", "Confirm Grok loads AGENTS.md on first run",
                f"ask it 'what are the hard rules in this repo?'; if it can't answer, see {guide}")
    if "gemini" in agents or (root / ".gemini/settings.json").exists():
        rep.section("Gemini CLI")
        rep.add("ok" if (root / ".gemini/settings.json").exists() else "warn", ".gemini/settings.json → AGENTS.md")
    rep.section("GitHub Copilot")
    rep.add("ok", "Reads AGENTS.md natively")

    if not args.apply:
        rep.add("info", "Plan only. Re-run with --apply to make changes")
    if linear:
        rep.action(WHO_TERMINAL, "Each developer signs in to Linear from their agent tool (OAuth, one time)",
                   f"see {guide}")
    rep.print(args.json)


# ----------------------------------------------------------------------------- github

def gh_api(method, path, body=None):
    cmd = ["gh", "api", "-X", method, path, "-H", "Accept: application/vnd.github+json"]
    if body is not None:
        cmd += ["--input", "-"]
    code, out, err = run(cmd, input_text=json.dumps(body) if body is not None else None)
    data = None
    if out:
        try:
            data = json.loads(out)
        except json.JSONDecodeError:
            data = out
    return code, data, err


def gh_ready(rep, cfg):
    if not have("gh"):
        rep.add("fail", "GitHub CLI (gh) not installed")
        rep.action(WHO_TERMINAL, "Install the GitHub CLI and log in", "https://cli.github.com  then  gh auth login")
        return False
    code, _, _ = run(["gh", "auth", "status"])
    if code != 0:
        rep.add("fail", "GitHub CLI not logged in")
        rep.action(WHO_TERMINAL, "Log in to GitHub", "gh auth login")
        return False
    if not cfg.get("github_repo"):
        rep.add("fail", "github_repo not set in haam.config.json")
        rep.action(WHO_AGENT, "Set the repo", "python3 tools/haam/haam.py config --github-repo owner/name")
        return False
    return True


def ruleset_body(cfg):
    return {
        "name": "HAAM main protection",
        "target": "branch",
        "enforcement": "active",
        # Admins may bypass only when merging a pull request, never by pushing straight to main:
        # every agent works under a human's login, often an admin's.
        "bypass_actors": [{"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "pull_request"}],
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "rules": [
            {"type": "deletion"},
            {"type": "non_fast_forward"},
            {"type": "pull_request", "parameters": {
                "required_approving_review_count": 1 if cfg.get("backup_approvers_github") else 0,
                "dismiss_stale_reviews_on_push": True,
                "require_code_owner_review": False,
                "require_last_push_approval": False,
                "required_review_thread_resolution": False,
            }},
            {"type": "required_status_checks", "parameters": {
                # Off: "must be up to date before merging" re-runs CI on every open PR after each merge.
                "strict_required_status_checks_policy": False,
                "required_status_checks": [{"context": c_} for c_ in REQUIRED_CHECKS],
            }},
        ],
    }


def merge_ruleset(current, wanted):
    """Add what HAAM needs to an existing ruleset, keeping everything the project set itself.
    Returns (body to PUT, list of changes, list of warnings)."""
    keep = {k: current.get(k) for k in ("name", "target", "enforcement", "conditions", "bypass_actors")}
    rules = [dict(r) for r in current.get("rules") or []]
    changes, notes = [], []
    types = {r["type"]: r for r in rules}
    for r in wanted["rules"]:
        if r["type"] not in types:
            rules.append(r)
            changes.append(f"Add the '{r['type']}' rule")
    checks_rule = next(r for r in rules if r["type"] == "required_status_checks")
    params = checks_rule.setdefault("parameters", {})
    have = {c.get("context") for c in params.get("required_status_checks") or []}
    missing = [c["context"] for c in wanted["rules"][-1]["parameters"]["required_status_checks"] if c["context"] not in have]
    if missing:
        params["required_status_checks"] = list(params.get("required_status_checks") or []) + [{"context": c} for c in missing]
        params.setdefault("strict_required_status_checks_policy", False)
        changes.append("Require the check(s) " + ", ".join(missing))
    if params.get("strict_required_status_checks_policy"):
        notes.append("'Branches must be up to date before merging' is on: every merge re-runs CI on all open PRs "
                     "(costs CI minutes). Turn it off in the ruleset, or run github --apply --reset")
    if any(a.get("bypass_mode") == "always" for a in keep.get("bypass_actors") or []):
        notes.append("Admins can bypass the rules 'always': agents working under an admin login could push straight "
                     "to main. Set bypass to 'pull request only' in the ruleset, or run github --apply --reset")
    if keep.get("enforcement") != "active":
        notes.append(f"The ruleset's enforcement is '{keep.get('enforcement')}', not 'active': the gates aren't enforced")
    body = {k: v for k, v in keep.items() if v is not None}
    body["rules"] = [{k: v for k, v in r.items() if k in ("type", "parameters")} for r in rules]
    return body, changes, notes


def cmd_github(args):
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    rep = Report()
    rep.section("GitHub")
    if not gh_ready(rep, cfg):
        rep.print(args.json)
        return
    repo = cfg["github_repo"]
    apply = args.apply

    code, info, err = gh_api("GET", f"repos/{repo}")
    if code != 0:
        rep.add("fail", f"Can't access {repo}", err)
        rep.print(args.json)
        return
    perms = info.get("permissions", {}) if isinstance(info, dict) else {}
    rep.add("ok" if perms.get("admin") else "fail", f"Repository {repo}",
            "you are an admin" if perms.get("admin") else "admin rights needed for this step")
    if not perms.get("admin"):
        rep.action(WHO_TERMINAL, "Run `haam.py github` as a repository admin")
        rep.print(args.json)
        return
    private = info.get("private", False)

    # Labels
    rep.section("Labels")
    code, out, _ = run(["gh", "label", "list", "-R", repo, "--json", "name", "-L", "200"])
    existing = {l["name"] for l in json.loads(out)} if code == 0 and out else set()
    for name, color, desc in GITHUB_LABELS:
        if name in existing:
            rep.add("ok", name)
        elif apply:
            c2, _, e2 = run(["gh", "label", "create", name, "--color", color, "--description", desc, "-R", repo])
            rep.add("ok" if c2 == 0 else "fail", f"{name} created" if c2 == 0 else f"{name}", e2)
        else:
            rep.add("warn", f"{name} missing", "will create")

    # Ruleset
    rep.section("Branch rules on the default branch")
    code, rulesets, err = gh_api("GET", f"repos/{repo}/rulesets")
    current = None
    if code == 0 and isinstance(rulesets, list):
        current = next((r for r in rulesets if r.get("name") == "HAAM main protection"), None)
    body = ruleset_body(cfg)
    if code != 0:
        rep.add("fail", "Can't read rulesets", (err or "")[:160])
        rep.action(WHO_BROWSER, "Rulesets on private repos need a paid GitHub plan (Pro/Team). Upgrade, "
                   "or set equivalent classic branch protection manually (docs/setup/GITHUB-SETUP.md §2)")
    else:
        full = None
        if current:
            c0, full, _ = gh_api("GET", f"repos/{repo}/rulesets/{current['id']}")
            full = full if c0 == 0 and isinstance(full, dict) else None
        if current and not full and not args.reset:
            rep.add("fail", "Couldn't read the existing ruleset, so it's left unchanged",
                    "re-run later, or use --reset to replace it with HAAM's defaults")
        elif current and full and not args.reset:
            merged, changes, notes = merge_ruleset(full, body)
            for n in notes:
                rep.add("warn", n)
            if not changes:
                rep.add("ok", "Ruleset 'HAAM main protection' has everything HAAM needs", "your own settings are kept")
            elif apply:
                c2, _, e2 = gh_api("PUT", f"repos/{repo}/rulesets/{current['id']}", merged)
                for ch in changes:
                    rep.add("ok" if c2 == 0 else "fail", ch)
                if c2 != 0:
                    rep.add("fail", "Ruleset not updated", (e2 or "")[:200])
            else:
                for ch in changes:
                    rep.add("warn", f"Will {ch[0].lower() + ch[1:]}", "everything else in your ruleset is kept")
        elif apply:
            if current:
                c2, _, e2 = gh_api("PUT", f"repos/{repo}/rulesets/{current['id']}", body)
            else:
                c2, _, e2 = gh_api("POST", f"repos/{repo}/rulesets", body)
            rep.add("ok" if c2 == 0 else "fail", "Ruleset 'HAAM main protection' " + ("reset to HAAM defaults" if current else "created")
                    if c2 == 0 else "Ruleset not applied", (e2 or "")[:200])
            if c2 != 0 and private:
                rep.action(WHO_BROWSER, "Rulesets on private repos need GitHub Pro/Team. Upgrade or protect the "
                           "branch manually (docs/setup/GITHUB-SETUP.md §2)")
        else:
            rep.add("ok" if current else "warn", "Ruleset 'HAAM main protection'",
                    "exists: --reset replaces it with HAAM defaults" if current else "will create")
    rep.add("info", "Required checks: " + ", ".join(REQUIRED_CHECKS))
    rep.add("info", "Admins can bypass only when merging a pull request (Level 2 emergency override), never by pushing to main")

    # Production environment
    rep.section("Production environment (Gate G5)")
    approvers = [cfg.get("product_owner_github")] + list(cfg.get("backup_approvers_github") or [])
    approvers = [a for a in approvers if a]
    if not approvers:
        rep.add("fail", "No approver configured", "set product_owner_github")
        rep.action(WHO_AGENT, "Set the approver", "python3 tools/haam/haam.py config --owner USER")
    else:
        code, env, _ = gh_api("GET", f"repos/{repo}/environments/production")
        exists = code == 0
        if apply:
            reviewers = []
            for a in approvers:
                c3, uid, _ = run(["gh", "api", f"users/{a}", "--jq", ".id"])
                if c3 == 0 and uid:
                    reviewers.append({"type": "User", "id": int(uid)})
                else:
                    rep.add("fail", f"GitHub user {a} not found")
            env_body = {"reviewers": reviewers, "prevent_self_review": False,
                        "deployment_branch_policy": {"protected_branches": False, "custom_branch_policies": True}}
            c2, _, e2 = gh_api("PUT", f"repos/{repo}/environments/production", env_body)
            if c2 == 0:
                rep.add("ok", "Environment 'production' with required approval", ", ".join(approvers))
                c4, _, e4 = gh_api("POST", f"repos/{repo}/environments/production/deployment-branch-policies",
                                   {"name": cfg.get("default_branch", "main"), "type": "branch"})
                rep.add("ok" if c4 == 0 or "already" in (e4 or "").lower() else "warn",
                        f"Deploys only from {cfg.get('default_branch', 'main')}", "" if c4 == 0 else (e4 or "")[:120])
            elif reviewers and private and "422" in (e2 or "") and any(
                    k in (e2 or "").lower() for k in ("protection rule", "reviewer", "plan", "upgrade", "not available")):
                # Required reviewers on private repos need GitHub Team or Enterprise: create the environment without them.
                env_body["reviewers"] = []
                c6, _, e6 = gh_api("PUT", f"repos/{repo}/environments/production", env_body)
                if c6 == 0:
                    gh_api("POST", f"repos/{repo}/environments/production/deployment-branch-policies",
                           {"name": cfg.get("default_branch", "main"), "type": "branch"})
                rep.add("warn" if c6 == 0 else "fail", "Environment 'production' created without a required approver"
                        if c6 == 0 else "Environment not configured",
                        "your GitHub plan doesn't allow required reviewers on private repos (GitHub Team or Enterprise "
                        "does). Deploys start as soon as a PR merges, so G5 is your 'ship' in /test." if c6 == 0 else (e6 or "")[:200])
            else:
                rep.add("fail", "Environment not configured", (e2 or "")[:200])
            if cfg.get("production_url"):
                c5, _, _ = run(["gh", "variable", "set", "PRODUCTION_URL", "--env", "production",
                                "--body", cfg["production_url"], "-R", repo])
                rep.add("ok" if c5 == 0 else "warn", "PRODUCTION_URL variable set")
        else:
            rep.add("ok" if exists else "warn", "Environment 'production'",
                    "exists (approvers will be refreshed)" if exists else "will create with approvers: " + ", ".join(approvers))

    # Security features
    rep.section("Security features")
    sec = info.get("security_and_analysis") or {}
    for feat, label in (("secret_scanning", "Secret scanning"), ("secret_scanning_push_protection", "Push protection")):
        on = (sec.get(feat) or {}).get("status") == "enabled"
        if on:
            rep.add("ok", label)
        elif apply:
            c2, _, e2 = gh_api("PATCH", f"repos/{repo}", {"security_and_analysis": {feat: {"status": "enabled"}}})
            rep.add("ok" if c2 == 0 else "warn", label + (" enabled" if c2 == 0 else " not available"),
                    "" if c2 == 0 else "may need a paid plan for private repos; the kit's own `secrets` check still protects you")
        else:
            rep.add("warn", label + " off", "will try to enable")
    if apply:
        c2, _, _ = gh_api("PUT", f"repos/{repo}/vulnerability-alerts")
        c3, _, _ = gh_api("PUT", f"repos/{repo}/automated-security-fixes")
        rep.add("ok" if c2 == 0 else "warn", "Dependabot alerts")
        rep.add("ok" if c3 == 0 else "warn", "Dependabot security updates")
    else:
        rep.add("info", "Dependabot alerts and security updates", "will enable")

    # Secrets
    rep.section("Secrets (never handled by agents)")
    code, out, _ = run(["gh", "secret", "list", "-R", repo, "--json", "name"])
    names = {s["name"] for s in json.loads(out)} if code == 0 and out else set()
    if "ANTHROPIC_API_KEY" in names:
        rep.add("ok", "ANTHROPIC_API_KEY (both reviewer agents; billed per review)")
    elif "CLAUDE_CODE_OAUTH_TOKEN" in names:
        rep.add("ok", "CLAUDE_CODE_OAUTH_TOKEN (both reviewer agents run on your Claude plan)")
    else:
        rep.add("fail", "No key for the reviewer agents", "set CLAUDE_CODE_OAUTH_TOKEN (your Claude plan) or ANTHROPIC_API_KEY")
        rep.action(WHO_TERMINAL, "Either run `claude setup-token` and paste the token it prints, or create a dedicated "
                   "API key with a spend limit at console.anthropic.com and paste that. The command asks for it "
                   "without showing it; it isn't stored anywhere else",
                   f"gh secret set CLAUDE_CODE_OAUTH_TOKEN -R {repo}   (or: gh secret set ANTHROPIC_API_KEY -R {repo})")

    rep.section("Manual steps GitHub doesn't expose to the tool")
    rep.add("info", "Fork PRs: Settings → Actions → General → require approval for outside collaborators")
    rep.action(WHO_BROWSER, "Require approval for workflows from fork PRs",
               f"https://github.com/{repo}/settings/actions")
    rep.add("info", "Optional once you have 2+ humans: CODEOWNERS for protected areas (docs/setup/GITHUB-SETUP.md §5)")

    if not apply:
        rep.add("info", "Plan only. Re-run with --apply to make these changes")
    rep.print(args.json)


# ----------------------------------------------------------------------------- linear

class Linear:
    def __init__(self, key):
        self.key = key
        self._mutations = None

    def q(self, query, variables=None):
        req = urllib.request.Request(
            LINEAR_API,
            data=json.dumps({"query": query, "variables": variables or {}}).encode(),
            headers={"Content-Type": "application/json", "Authorization": self.key},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="ignore")[:300]
            raise RuntimeError(f"Linear API HTTP {e.code}: {body}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Can't reach Linear: {e.reason}")
        if data.get("errors"):
            raise RuntimeError("; ".join(err.get("message", "") for err in data["errors"]))
        return data["data"]

    def has_mutation(self, name):
        if self._mutations is None:
            d = self.q("{ __schema { mutationType { fields { name } } } }")
            self._mutations = {f["name"] for f in d["__schema"]["mutationType"]["fields"]}
        return name in self._mutations

    def input_fields(self, type_name):
        d = self.q('query($n:String!){ __type(name:$n){ inputFields { name } } }', {"n": type_name})
        t = d.get("__type") or {}
        return {f["name"] for f in t.get("inputFields") or []}


def linear_key(rep):
    key = os.environ.get("LINEAR_API_KEY", "").strip()
    if key:
        return key
    if is_tty():
        print("A Linear personal API key is needed (Linear → Settings → Security & access → Personal API keys).")
        print("It is used for this run only: not shown, not saved.")
        key = getpass.getpass("Linear API key: ").strip()
        return key or None
    rep.add("fail", "No Linear API key available to this session")
    rep.action(WHO_TERMINAL, "Agents never handle API keys. Run this step yourself in a terminal; "
               "it will ask for your Linear personal API key securely",
               "python3 tools/haam/haam.py linear --apply")
    return None


TEAM_FIELDS = "id key name triageEnabled states { nodes { id name type position } }"


def cmd_linear(args):
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    rep = Report()
    rep.section("Linear")
    if cfg.get("tracker") == "github":
        rep.add("warn", "This project's tracker is GitHub Projects", "use `haam.py github-project`, or switch with `config --tracker linear`")
    key = linear_key(rep)
    if not key:
        rep.print(args.json)
        return
    lin = Linear(key)
    apply = args.apply
    team_key = cfg["team_key"]
    team_name = cfg.get("linear_team_name") or cfg.get("product_name") or team_key

    try:
        me = lin.q("{ viewer { name email organization { name } } }")["viewer"]
        rep.add("ok", f"Connected as {me['name']}", f"workspace: {me['organization']['name']}")

        teams = lin.q('query($k:String!){ teams(filter:{key:{eq:$k}}) { nodes { %s } } }' % TEAM_FIELDS,
                      {"k": team_key})["teams"]["nodes"]
        team = teams[0] if teams else None
        rep.section(f"Team {team_key}")
        if team:
            rep.add("ok", f"Team '{team['name']}' ({team_key}) exists")
        elif apply:
            d = lin.q('mutation($i:TeamCreateInput!){ teamCreate(input:$i){ success team { %s } } }' % TEAM_FIELDS,
                      {"i": {"name": team_name, "key": team_key}})
            team = d["teamCreate"]["team"]
            rep.add("ok", f"Team '{team_name}' ({team_key}) created")
        else:
            rep.add("warn", f"Team {team_key} not found", f"will create '{team_name}'")

        # Triage
        if team and not team.get("triageEnabled"):
            if apply:
                lin.q('mutation($id:String!,$i:TeamUpdateInput!){ teamUpdate(id:$id,input:$i){ success } }',
                      {"id": team["id"], "i": {"triageEnabled": True}})
                rep.add("ok", "Triage turned on")
                team = lin.q('query($id:String!){ team(id:$id){ %s } }' % TEAM_FIELDS, {"id": team["id"]})["team"]
            else:
                rep.add("warn", "Triage off", "will turn on")
        elif team:
            rep.add("ok", "Triage on")

        # States
        rep.section("Workflow statuses")
        states = {s["name"].lower(): s for s in (team["states"]["nodes"] if team else [])}
        for pos, (name, typ, color) in enumerate(LINEAR_STATES):
            s = states.get(name.lower())
            if s:
                if s["type"] != typ:
                    rep.add("warn", f"{name} exists but is type '{s['type']}', expected '{typ}'",
                            "change it in Linear → Team settings → Workflow")
                else:
                    rep.add("ok", name)
                continue
            if typ == "triage":
                rep.add("warn" if not apply else "info", name, "created by turning on Triage")
                continue
            # Linear's default 'Todo' becomes our 'Ready'
            if name == "Ready" and "todo" in states and states["todo"]["type"] == "unstarted":
                if apply:
                    lin.q('mutation($id:String!,$i:WorkflowStateUpdateInput!){ workflowStateUpdate(id:$id,input:$i){ success } }',
                          {"id": states["todo"]["id"], "i": {"name": "Ready"}})
                    rep.add("ok", "Todo renamed to Ready")
                else:
                    rep.add("warn", "Ready missing", "will rename Todo → Ready")
                continue
            if apply and team:
                lin.q('mutation($i:WorkflowStateCreateInput!){ workflowStateCreate(input:$i){ success } }',
                      {"i": {"teamId": team["id"], "name": name, "type": typ, "color": color, "position": float(pos)}})
                rep.add("ok", f"{name} created")
            else:
                rep.add("warn", f"{name} missing", "will create")
        wanted = {n.lower() for n, _, _ in LINEAR_STATES} | {"todo"}
        for n, s in states.items():
            if n not in wanted:
                rep.add("warn", f"Extra status '{s['name']}'", "not used by HAAM: archive it in Linear if no issues use it")

        # Labels
        rep.section("Labels")
        label_nodes = []
        after = None
        while True:
            d = lin.q('query($a:String){ issueLabels(first:250, after:$a){ nodes { id name team { id } } '
                      'pageInfo { hasNextPage endCursor } } }', {"a": after})["issueLabels"]
            label_nodes += d["nodes"]
            if not d["pageInfo"]["hasNextPage"]:
                break
            after = d["pageInfo"]["endCursor"]
        usable = {l["name"].lower() for l in label_nodes
                  if l.get("team") is None or (team and l["team"] and l["team"]["id"] == team["id"])}
        for name, color, desc in LINEAR_LABELS:
            if name.lower() in usable:
                rep.add("ok", name)
            elif apply and team:
                lin.q('mutation($i:IssueLabelCreateInput!){ issueLabelCreate(input:$i){ success } }',
                      {"i": {"name": name, "color": color, "description": desc, "teamId": team["id"]}})
                rep.add("ok", f"{name} created")
            else:
                rep.add("warn", f"{name} missing", "will create")

    except RuntimeError as e:
        rep.add("fail", "Linear API error", str(e)[:300])
        rep.action(WHO_BROWSER, "Do the remaining Linear steps by hand", "docs/setup/LINEAR-SETUP.md")

    rep.section("Manual steps in Linear (no API for these)")
    for t in ["Connect GitHub: Settings → Integrations → GitHub",
              "PR automations: PR opened → In Review; PR merged → Deploying",
              "Branch name format: {issue-identifier}-{issue-title} (no username prefix)",
              "Saved views: Waiting on me, Agent queue, Ideas inbox, Bugs, Epics, Overrides to close",
              "Delete Linear's sample statuses you don't need (e.g. Duplicate)"]:
        rep.add("info", t)
    rep.action(WHO_BROWSER, "Finish the Linear settings listed above", "docs/setup/LINEAR-SETUP.md §6–7")
    if not apply:
        rep.add("info", "Plan only. Re-run with --apply to make these changes")
    rep.print(args.json)


# ----------------------------------------------------------------------------- github projects

# Statuses as a single-select "Status" field on the board: (name, colour, description)
GH_STATUSES = [
    ("Triage", "ORANGE", "New idea or bug, not assessed"),
    ("Discovery", "GRAY", "Being assessed"),
    ("Decision", "YELLOW", "Waiting for a human decision (G1)"),
    ("Backlog", "GRAY", "Approved, needs a spec"),
    ("Ready", "BLUE", "Spec approved (G2): agents may build"),
    ("In Progress", "YELLOW", "Claimed and being built"),
    ("In Review", "PURPLE", "PR open: checks and AI review (G3)"),
    ("UAT", "PINK", "Waiting for human testing (G4)"),
    ("Deploying", "GREEN", "Merged: waiting for production approval (G5)"),
    ("Done", "GREEN", "Released"),
    ("Parked", "GRAY", "Good idea, not now"),
    ("Canceled", "RED", "Will not do"),
]
GH_PRIORITIES = [
    ("Urgent", "RED", "Production broken or deadline at risk"),
    ("High", "ORANGE", "Important for current goals"),
    ("Medium", "YELLOW", "Normal"),
    ("Low", "GRAY", "Nice to have"),
]
# Issue labels used on GitHub when the tracker is GitHub Projects
GH_ISSUE_LABELS = [
    ("stream:idea", "BB87FC", "New idea, not yet decided"),
    ("stream:feature", "4EA7FC", "Approved work"),
    ("stream:bug", "EB5757", "Something is broken"),
    ("agent-ready", "4CB782", "Passed G2: agents may build it"),
    ("human-only", "95A2B3", "Agents must not pick this up"),
    ("override-followup", "FC7840", "Created after a gate override"),
    ("epic", "3E4B9E", "Groups the issues that make up one feature (its sub-issues)"),
    ("uat-failed", "D93F0B", "Failed the human test: rework first, then test again"),
]
EPIC_LABEL = "epic"
# Moving into these needs a human decision (they're done through human-only skills)
HUMAN_STATUSES = {"Done", "Parked", "Canceled"}
PROJECT_TOKEN_SECRET = "HAAM_PROJECT_TOKEN"


def gql(query, variables=None):
    """GitHub GraphQL through the gh CLI (uses the caller's own login or GH_TOKEN)."""
    body = json.dumps({"query": query, "variables": variables or {}})
    code, out, err = run(["gh", "api", "graphql", "--input", "-"], input_text=body)
    data = None
    if out:
        try:
            data = json.loads(out)
        except json.JSONDecodeError:
            pass
    msg = ""
    if data and data.get("errors"):
        msg = "; ".join(e.get("message", "") for e in data["errors"])
    elif code != 0:
        msg = err or out
    if msg:
        if "INSUFFICIENT_SCOPES" in msg or "required scopes" in msg or "'project'" in msg:
            raise RuntimeError("Your GitHub login can't use Projects yet. Run in your terminal: gh auth refresh -s project")
        raise RuntimeError(msg[:400])
    return (data or {}).get("data") or {}


PROJECT_FIELDS = """
  id number url title
  items(first: 1) { totalCount }
  fields(first: 50) { nodes { __typename
    ... on ProjectV2FieldCommon { id name }
    ... on ProjectV2SingleSelectField { options { id name } } } }
"""


class GHProject:
    """The GitHub Projects board for this repository."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.repo = cfg.get("github_repo") or ""
        if "/" not in self.repo:
            raise RuntimeError("github_repo isn't set: python3 tools/haam/haam.py config --github-repo owner/name")
        self.repo_owner, self.repo_name = self.repo.split("/", 1)
        self.owner = cfg.get("github_project_owner") or self.repo_owner
        self.number = cfg.get("github_project_number")
        self.data = None

    # --- board
    def load(self):
        if not self.number:
            raise RuntimeError("No board configured. Run: python3 tools/haam/haam.py github-project --apply")
        d = gql("query($o:String!,$n:Int!){ repositoryOwner(login:$o){ ... on ProjectV2Owner { projectV2(number:$n){ %s } } } }"
                % PROJECT_FIELDS, {"o": self.owner, "n": int(self.number)})
        proj = ((d.get("repositoryOwner") or {}).get("projectV2"))
        if not proj:
            raise RuntimeError(f"Board #{self.number} not found for {self.owner}, or no access to it")
        self.data = proj
        return proj

    def field(self, name):
        for f in (self.data or self.load())["fields"]["nodes"]:
            if f.get("name") == name:
                return f
        return None

    def option_id(self, field_name, option):
        f = self.field(field_name)
        if not f:
            raise RuntimeError(f"The board has no '{field_name}' field. Run: python3 tools/haam/haam.py github-project --apply")
        for o in f.get("options") or []:
            if o["name"].lower() == option.lower():
                return f["id"], o["id"]
        valid = ", ".join(o["name"] for o in f.get("options") or [])
        raise RuntimeError(f"'{option}' isn't a {field_name} on the board (valid: {valid})")

    # --- issues
    def issue(self, number):
        d = gql("""query($o:String!,$r:String!,$n:Int!){ repository(owner:$o,name:$r){ issue(number:$n){
                     id number title state url body createdAt parent{ number repository{ nameWithOwner } }
                     assignees(first:10){ nodes{ login } } labels(first:30){ nodes{ name } }
                     projectItems(first:20){ nodes{ id project{ id number }
                       fieldValues(first:20){ nodes{ ... on ProjectV2ItemFieldSingleSelectValue {
                         name field{ ... on ProjectV2FieldCommon { name } } } } } } } } } }""",
                {"o": self.repo_owner, "r": self.repo_name, "n": int(number)})
        iss = ((d.get("repository") or {}).get("issue"))
        if not iss:
            raise RuntimeError(f"Issue #{number} not found in {self.repo}")
        proj = self.data or self.load()
        item = next((i for i in iss["projectItems"]["nodes"] if i["project"]["id"] == proj["id"]), None)
        values = {}
        if item:
            for v in item["fieldValues"]["nodes"]:
                if v and v.get("field"):
                    values[v["field"]["name"]] = v["name"]
        return {
            "number": iss["number"], "title": iss["title"], "state": iss["state"], "url": iss["url"],
            "node_id": iss["id"], "created": iss["createdAt"],
            "assignees": [a["login"] for a in iss["assignees"]["nodes"]],
            "labels": [l["name"] for l in iss["labels"]["nodes"]],
            "item_id": item["id"] if item else None,
            "status": values.get("Status"), "priority": values.get("Priority"),
            "parent": self._parent(iss.get("parent")),
        }

    def _parent(self, p):
        """Parent epic number, only when the epic lives in this project's repository."""
        if not p or (p.get("repository") or {}).get("nameWithOwner", self.repo).lower() != self.repo.lower():
            return None
        return p["number"]

    def ensure_item(self, iss):
        if iss.get("item_id"):
            return iss["item_id"]
        proj = self.data or self.load()
        d = gql("mutation($p:ID!,$c:ID!){ addProjectV2ItemById(input:{projectId:$p, contentId:$c}){ item{ id } } }",
                {"p": proj["id"], "c": iss["node_id"]})
        iss["item_id"] = d["addProjectV2ItemById"]["item"]["id"]
        return iss["item_id"]

    def set_option(self, iss, field_name, option):
        field_id, opt_id = self.option_id(field_name, option)
        item = self.ensure_item(iss)
        gql("""mutation($p:ID!,$i:ID!,$f:ID!,$o:String!){ updateProjectV2ItemFieldValue(input:{
                 projectId:$p, itemId:$i, fieldId:$f, value:{ singleSelectOptionId:$o } }){ projectV2Item{ id } } }""",
            {"p": self.data["id"], "i": item, "f": field_id, "o": opt_id})

    def link(self, parent, child):
        """Make `child` a sub-issue of the epic `parent` (both are dicts from issue())."""
        gql("""mutation($p:ID!,$c:ID!){ addSubIssue(input:{issueId:$p, subIssueId:$c, replaceParent:true}){
                 issue{ number } subIssue{ number } } }""", {"p": parent["node_id"], "c": child["node_id"]})

    def unlink(self, parent_node_id, child):
        gql("""mutation($p:ID!,$c:ID!){ removeSubIssue(input:{issueId:$p, subIssueId:$c}){ issue{ number } } }""",
            {"p": parent_node_id, "c": child["node_id"]})

    def sub_issues(self, number):
        """All sub-issues of an epic, straight from GitHub (including ones not on the board)."""
        d = gql("""query($o:String!,$r:String!,$n:Int!){ repository(owner:$o,name:$r){ issue(number:$n){
                     id subIssues(first:100){ nodes{ number title state repository{ nameWithOwner } } } } } }""",
                {"o": self.repo_owner, "r": self.repo_name, "n": int(number)})
        iss = (d.get("repository") or {}).get("issue") or {}
        return iss.get("id"), [k for k in (iss.get("subIssues") or {}).get("nodes") or []
                               if k["repository"]["nameWithOwner"].lower() == self.repo.lower()]

    def items(self):
        proj = self.data or self.load()
        out, after = [], None
        while True:
            d = gql("""query($p:ID!,$a:String){ node(id:$p){ ... on ProjectV2 { items(first:100, after:$a){
                         pageInfo{ hasNextPage endCursor }
                         nodes{ id content{ __typename ... on Issue { number title state url createdAt parent{ number repository{ nameWithOwner } }
                           repository{ nameWithOwner } assignees(first:10){ nodes{ login } } labels(first:30){ nodes{ name } } } }
                           fieldValues(first:20){ nodes{ ... on ProjectV2ItemFieldSingleSelectValue {
                             name field{ ... on ProjectV2FieldCommon { name } } } } } } } } } }""",
                    {"p": proj["id"], "a": after})
            page = d["node"]["items"]
            for n in page["nodes"]:
                c = n.get("content") or {}
                if c.get("__typename") != "Issue":
                    continue
                vals = {v["field"]["name"]: v["name"] for v in n["fieldValues"]["nodes"] if v and v.get("field")}
                out.append({"number": c["number"], "title": c["title"], "state": c["state"], "url": c["url"],
                            "repo": c["repository"]["nameWithOwner"], "created": c["createdAt"],
                            "assignees": [a["login"] for a in c["assignees"]["nodes"]],
                            "labels": [l["name"] for l in c["labels"]["nodes"]],
                            "status": vals.get("Status"), "priority": vals.get("Priority"),
                            "parent": self._parent(c.get("parent"))})
            if not page["pageInfo"]["hasNextPage"]:
                return out
            after = page["pageInfo"]["endCursor"]


def gh_login():
    code, out, _ = run(["gh", "api", "user", "--jq", ".login"])
    return out.strip() if code == 0 else ""


def options_input(spec):
    return [{"name": n, "color": col, "description": desc} for n, col, desc in spec]


def cmd_github_project(args):
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    rep = Report()
    rep.section("GitHub Projects board")
    if cfg.get("tracker") != "github":
        rep.add("warn", f"tracker is '{cfg.get('tracker')}' in {CONFIG_NAME}",
                "set it first: python3 tools/haam/haam.py config --tracker github")
    if not gh_ready(rep, cfg):
        rep.print(args.json)
        return
    apply = args.apply
    title = cfg.get("product_name") or cfg["github_repo"].split("/")[1]
    try:
        board = GHProject(cfg)
        # Find or create the board
        if board.number:
            proj = board.load()
            rep.add("ok", f"Board #{proj['number']} '{proj['title']}'", proj["url"])
        else:
            d = gql("query($o:String!){ repositoryOwner(login:$o){ id __typename ... on ProjectV2Owner {"
                    " projectsV2(first:100){ nodes{ number title url } } } } }", {"o": board.owner})
            owner = d.get("repositoryOwner")
            if not owner:
                raise RuntimeError(f"GitHub account '{board.owner}' not found")
            match = next((p for p in owner["projectsV2"]["nodes"] if p["title"] == title), None)
            if match:
                board.number = match["number"]
                rep.add("ok", f"Found board #{match['number']} '{title}'", match["url"])
            elif apply:
                rid = gql("query($o:String!,$r:String!){ repository(owner:$o,name:$r){ id } }",
                          {"o": board.repo_owner, "r": board.repo_name})["repository"]["id"]
                created = gql("mutation($o:ID!,$t:String!,$r:ID!){ createProjectV2(input:{ownerId:$o, title:$t,"
                              " repositoryId:$r}){ projectV2{ number url } } }",
                              {"o": owner["id"], "t": title, "r": rid})["createProjectV2"]["projectV2"]
                board.number = created["number"]
                rep.add("ok", f"Board #{created['number']} '{title}' created and linked to {cfg['github_repo']}", created["url"])
            else:
                rep.add("warn", f"No board called '{title}' for {board.owner}", "will create it and link the repo")
            if board.number and apply:
                cfg["github_project_number"] = board.number
                cfg["github_project_owner"] = board.owner
                save_config(root, cfg)
            if board.number:
                board.load()

        if board.data:
            proj = board.data
            # Link repo (idempotent; errors if already linked are fine)
            if apply:
                try:
                    rid = gql("query($o:String!,$r:String!){ repository(owner:$o,name:$r){ id } }",
                              {"o": board.repo_owner, "r": board.repo_name})["repository"]["id"]
                    gql("mutation($p:ID!,$r:ID!){ linkProjectV2ToRepository(input:{projectId:$p, repositoryId:$r}){"
                        " repository{ id } } }", {"p": proj["id"], "r": rid})
                except RuntimeError:
                    pass

            rep.section("Status field (12 statuses)")
            status = board.field("Status")
            want = [n for n, _, _ in GH_STATUSES]
            have_opts = [o["name"] for o in (status or {}).get("options") or []]
            if have_opts == want:
                rep.add("ok", "Status has the 12 HAAM statuses")
            elif not status:
                rep.add("fail", "The board has no Status field", "add a single-select field called Status in the browser")
            elif proj["items"]["totalCount"] and not args.force_status:
                rep.add("warn", "Status options differ and the board already has items",
                        "replacing options clears existing statuses; rerun with --force-status, or edit options in the browser")
            elif apply:
                gql("mutation($f:ID!,$o:[ProjectV2SingleSelectFieldOptionInput!]!){ updateProjectV2Field(input:{"
                    " fieldId:$f, singleSelectOptions:$o }){ projectV2Field{ ... on ProjectV2FieldCommon { id } } } }",
                    {"f": status["id"], "o": options_input(GH_STATUSES)})
                rep.add("ok", "Status options set: " + ", ".join(want))
            else:
                rep.add("warn", "Status options", "will set: " + ", ".join(want))

            rep.section("Priority field")
            prio = board.field("Priority")
            if prio:
                rep.add("ok", "Priority field exists", ", ".join(o["name"] for o in prio.get("options") or []))
            elif apply:
                gql("mutation($p:ID!,$o:[ProjectV2SingleSelectFieldOptionInput!]!){ createProjectV2Field(input:{"
                    " projectId:$p, name:\"Priority\", dataType:SINGLE_SELECT, singleSelectOptions:$o }){"
                    " projectV2Field{ ... on ProjectV2FieldCommon { id } } } }",
                    {"p": proj["id"], "o": options_input(GH_PRIORITIES)})
                rep.add("ok", "Priority field created: Urgent, High, Medium, Low")
            else:
                rep.add("warn", "Priority field missing", "will create: Urgent, High, Medium, Low")
    except RuntimeError as e:
        rep.add("fail", "GitHub Projects error", str(e))
        if "gh auth refresh" in str(e):
            rep.action(WHO_TERMINAL, "Give your GitHub login access to Projects", "gh auth refresh -s project")
        rep.print(args.json)
        return

    rep.section("Issue labels")
    code, out, _ = run(["gh", "label", "list", "-R", cfg["github_repo"], "--json", "name", "-L", "200"])
    existing = {l["name"] for l in json.loads(out)} if code == 0 and out else set()
    for name, color, desc in GH_ISSUE_LABELS:
        if name in existing:
            rep.add("ok", name)
        elif apply:
            c2, _, e2 = run(["gh", "label", "create", name, "--color", color, "--description", desc, "-R", cfg["github_repo"]])
            rep.add("ok" if c2 == 0 else "fail", f"{name} created" if c2 == 0 else name, e2[:120])
        else:
            rep.add("warn", f"{name} missing", "will create")

    rep.section("Automation token (moves cards when PRs open and merge)")
    code, out, _ = run(["gh", "secret", "list", "-R", cfg["github_repo"], "--json", "name"])
    if code == 0 and PROJECT_TOKEN_SECRET in out:
        rep.add("ok", f"{PROJECT_TOKEN_SECRET} secret present")
    else:
        rep.add("warn", f"{PROJECT_TOKEN_SECRET} secret missing", "cards won't move automatically on PR open/merge")
        rep.action(WHO_TERMINAL,
                   "Create a classic GitHub token with the 'project' scope (and 'repo' if the repository is private) at "
                   "github.com/settings/tokens, then paste it when this command asks",
                   f"gh secret set {PROJECT_TOKEN_SECRET} -R {cfg['github_repo']}")

    rep.section("Board views (browser only)")
    for v in ["Board: layout Board, group by Status",
              "Triage: filter  status:Triage  (the product owner's daily inbox)",
              "Epics: filter  label:epic  (table layout; show the Sub-issues progress field)",
              "In table views, show the Parent issue field so each card shows its epic",
              "Workflows: turn on 'Auto-add to project' for this repository (issues made on GitHub's website join the board, no Actions minutes)",
              "Agent queue: filter  status:Ready no:assignee  (features also need label:agent-ready)",
              "Waiting on me: filter  status:Decision,UAT",
              "Ideas inbox: filter  status:Triage,Discovery label:stream:idea",
              "Bugs: filter  label:stream:bug -status:Done,Canceled  sorted by Priority"]:
        rep.add("info", v)
    if board.data:
        rep.action(WHO_BROWSER, "Create the saved views listed above on the board", board.data["url"])
    rep.add("info", "Agents use `python3 tools/haam/haam.py issue ...` for this board (docs/process/TRACKER.md)")
    if not apply:
        rep.add("info", "Plan only. Re-run with --apply to make these changes")
    rep.print(args.json)


def parse_issue_number(text):
    m = re.fullmatch(r"#?(\d+)", str(text).strip())
    if not m:
        sys.exit(f"Expected an issue number like 123 or #123, got '{text}'")
    return int(m.group(1))


def linked_issue_numbers(pr):
    """Issues a PR refers to: 'Refs/Closes/Fixes #N' in title or body, or a branch named 'N-...'."""
    nums = set()
    for text in (pr.get("title") or "", pr.get("body") or ""):
        for m in re.finditer(r"(?i)\b(?:refs?|closes?|closed|fix(?:es|ed)?|resolves?|resolved)\s*:?\s+#(\d+)", text):
            nums.add(int(m.group(1)))
        m = re.match(r"\s*#(\d+)\s*:", text)
        if m:
            nums.add(int(m.group(1)))
    m = re.match(r"(\d+)-", pr.get("headRefName") or "")
    if m:
        nums.add(int(m.group(1)))
    return sorted(nums)


def cmd_issue(args):
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    if cfg.get("tracker") != "github":
        sys.exit("This project tracks work in Linear: use the Linear connection (MCP). See docs/process/TRACKER.md.")
    try:
        board = GHProject(cfg)
        board.load()
        result = issue_action(args, cfg, board)
    except RuntimeError as e:
        if args.json:
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"✘ {e}", file=sys.stderr)
        sys.exit(1)
    if args.json:
        print(json.dumps({"ok": True, **result}, indent=2))
    elif result.get("message"):
        print(result["message"])


def issue_action(args, cfg, board):
    repo = cfg["github_repo"]
    a = args.action

    if a == "list":
        items = [i for i in board.items() if i["repo"].lower() == repo.lower()]
        if args.status:
            wanted = {s.lower() for s in args.status}
            items = [i for i in items if (i["status"] or "").lower() in wanted]
        for lab in args.label or []:
            items = [i for i in items if lab in i["labels"]]
        for lab in args.no_label or []:
            items = [i for i in items if lab not in i["labels"]]
        if args.unassigned:
            items = [i for i in items if not i["assignees"]]
        if args.open_only:
            items = [i for i in items if i["state"] == "OPEN"]
        if args.parent:
            pn = parse_issue_number(args.parent)
            items = [i for i in items if i.get("parent") == pn]
        if args.no_parent:
            items = [i for i in items if not i.get("parent")]
        order = {n: k for k, (n, _, _) in enumerate(GH_PRIORITIES)}
        items.sort(key=lambda i: (order.get(i["priority"], 9), i["created"]))
        lines = [f"#{i['number']:<5} {i['status'] or '-':<12} {i['priority'] or '-':<7} "
                 f"{','.join(i['assignees']) or '-':<14} {i['title']}  [{', '.join(i['labels'])}]"
                 + (f"  (epic #{i['parent']})" if i.get("parent") else "") for i in items]
        return {"items": items, "message": "\n".join(lines) or "No matching issues."}

    if a == "create":
        if not args.title:
            sys.exit("--title is required")
        body = Path(args.body_file).read_text() if args.body_file else (args.body or "")
        labels = [f"stream:{args.stream}"] + (args.label or []) + ([EPIC_LABEL] if args.epic else [])
        parent = None
        if args.parent and args.epic:
            raise RuntimeError("Epics don't nest in HAAM: an epic can't have a parent epic")
        if args.parent:
            parent = board.issue(parse_issue_number(args.parent))
            if EPIC_LABEL not in parent["labels"]:
                raise RuntimeError(f"#{parent['number']} isn't an epic (label '{EPIC_LABEL}'). Make it one first: "
                                   f"issue label {parent['number']} --add {EPIC_LABEL}")
        cmd = ["gh", "issue", "create", "-R", repo, "--title", args.title, "--body", body]
        for lab in labels:
            cmd += ["--label", lab]
        code, out, err = run(cmd)
        if code != 0:
            raise RuntimeError(err or out)
        number = int(out.strip().rstrip("/").split("/")[-1])
        iss = board.issue(number)
        status = args.status[-1] if args.status else ("Backlog" if args.stream == "feature" else "Triage")
        board.set_option(iss, "Status", status)
        if args.priority:
            board.set_option(iss, "Priority", args.priority)
        if parent:
            board.link(parent, iss)
        return {"number": number, "url": iss["url"], "status": status, "parent": parent["number"] if parent else None,
                "message": f"Created {'epic ' if args.epic else ''}#{number} ({status}"
                           f"{', ' + args.priority if args.priority else ''}{', in epic #' + str(parent['number']) if parent else ''}): {iss['url']}"}

    number = parse_issue_number(args.number) if args.number else None
    if number is None:
        sys.exit(f"`issue {a}` needs an issue number")
    iss = board.issue(number)

    if a == "view":
        msg = (f"#{iss['number']} {iss['title']}\n  state: {iss['state']} · status: {iss['status'] or '-'} · "
               f"priority: {iss['priority'] or '-'} · assignees: {', '.join(iss['assignees']) or '-'}\n"
               f"  labels: {', '.join(iss['labels']) or '-'}"
               + (f" · epic: #{iss['parent']}" if iss.get("parent") else "") + f"\n  {iss['url']}")
        return {"issue": {k: v for k, v in iss.items() if k != "node_id"}, "message": msg}

    if a == "link":
        if not args.parent:
            sys.exit("Give the epic: `issue link 14 --parent 9`")
        epic = board.issue(parse_issue_number(args.parent))
        if EPIC_LABEL not in epic["labels"]:
            raise RuntimeError(f"#{epic['number']} isn't an epic (label '{EPIC_LABEL}')")
        if EPIC_LABEL in iss["labels"]:
            raise RuntimeError(f"#{number} is itself an epic; epics don't nest in HAAM")
        board.ensure_item(iss)
        board.link(epic, iss)
        return {"number": number, "parent": epic["number"], "message": f"#{number} is now part of epic #{epic['number']}"}

    if a == "children":
        _, subs = board.sub_issues(number)
        on_board = {i["number"]: i for i in board.items() if i["repo"].lower() == repo.lower()}
        kids = [on_board.get(k["number"]) or {"number": k["number"], "title": k["title"], "state": k["state"],
                                               "status": None, "priority": None, "created": "", "not_on_board": True}
                for k in subs]
        order = {n: k for k, (n, _, _) in enumerate(GH_PRIORITIES)}
        kids.sort(key=lambda i: (order.get(i["priority"], 9), i["created"]))
        done = len([k for k in kids if k["status"] in ("Done", "Canceled") or k["state"] == "CLOSED"])
        lines = [f"Epic #{number} {iss['title']}: {done}/{len(kids)} done"] + [
            f"  #{k['number']:<5} {k['status'] or '-':<12} {k['priority'] or '-':<7} {k['title']}"
            + ("  (not on the board: issue add " + str(k["number"]) + ")" if k.get("not_on_board") else "") for k in kids]
        return {"epic": number, "children": kids, "done": done, "message": "\n".join(lines)}

    if a == "unlink":
        if not iss.get("parent"):
            return {"number": number, "message": f"#{number} isn't in an epic"}
        epic_id, _ = board.sub_issues(iss["parent"])
        board.unlink(epic_id, iss)
        return {"number": number, "message": f"#{number} is no longer part of epic #{iss['parent']}"}

    if a == "edit":
        if not (args.title or args.body or args.body_file):
            sys.exit("Give --title and/or --body / --body-file")
        cmd = ["gh", "issue", "edit", str(number), "-R", repo]
        if args.title:
            cmd += ["--title", args.title]
        if args.body or args.body_file:
            cmd += ["--body", Path(args.body_file).read_text() if args.body_file else args.body]
        code, out, err = run(cmd)
        if code != 0:
            raise RuntimeError(err or out)
        return {"number": number, "message": f"#{number} updated"}

    if a == "add":
        board.ensure_item(iss)
        if not iss["status"]:
            board.set_option(iss, "Status", "Triage")
        return {"number": number, "message": f"#{number} is on the board ({iss['status'] or 'Triage'})"}

    if a == "status":
        new = args.value
        if not new:
            sys.exit("Give the new status, e.g. `issue status 12 \"In Progress\"`")
        canon = next((n for n, _, _ in GH_STATUSES if n.lower() == new.lower()), None)
        if not canon:
            raise RuntimeError(f"Unknown status '{new}'. Valid: {', '.join(n for n, _, _ in GH_STATUSES)}")
        branch = git_out(Path.cwd(), "branch", "--show-current")
        mine = bool(re.match(rf"^{number}-", branch or ""))
        guarded = iss["status"] == "In Progress" and not (args.force or args.human)
        if guarded and not mine and branch:
            # A batch PR's branch is named after its first issue; the claim comment names the branch.
            code, out, _ = run(["gh", "issue", "view", str(number), "-R", repo, "--json", "comments"])
            bodies = [c.get("body", "") for c in (json.loads(out).get("comments") or [])] if code == 0 and out else []
            mine = any("Claimed by" in b_ and f"`{branch}`" in b_ for b_ in bodies)
        if guarded and not mine:
            raise RuntimeError(f"#{number} is claimed (status {iss['status']}, assigned to {', '.join(iss['assignees']) or '-'}) "
                               "and this chat isn't on its branch. Leave it to the chat working on it, or add --force "
                               "only when the human asked (e.g. /triage releasing a stuck claim).")
        human_move = canon in HUMAN_STATUSES or (iss["status"] == "Decision" and canon == "Backlog")
        if human_move and not args.human:
            raise RuntimeError(f"Moving to {canon} is a human decision. Only do it while running the human-only skill "
                               "the human typed (/triage, /epic, /decide, /release …), and add --human.")
        board.set_option(iss, "Status", canon)
        msg = f"#{number}: {iss['status'] or '-'} → {canon}"
        if canon == "Canceled" and iss["state"] == "OPEN":
            code, out, err = run(["gh", "issue", "close", str(number), "-R", repo, "--reason", "not planned"])
            if code != 0:
                raise RuntimeError(err or out)
            msg += " (closed as not planned)"
        return {"number": number, "status": canon, "message": msg}

    if a == "priority":
        if not args.value:
            sys.exit("Give the priority: Urgent, High, Medium or Low")
        board.set_option(iss, "Priority", args.value)
        return {"number": number, "priority": args.value, "message": f"#{number}: priority {args.value}"}

    if a == "label":
        cmd = ["gh", "issue", "edit", str(number), "-R", repo]
        human_labels = {"agent-ready"}
        for lab in args.add or []:
            if lab in human_labels and not args.human:
                raise RuntimeError("agent-ready is added only after a human approves the spec; add --human when that happened")
            cmd += ["--add-label", lab]
        for lab in args.remove or []:
            cmd += ["--remove-label", lab]
        code, out, err = run(cmd)
        if code != 0:
            raise RuntimeError(err or out)
        return {"number": number, "message": f"#{number}: labels updated"}

    if a == "comment":
        body = Path(args.body_file).read_text() if args.body_file else (args.body or "")
        if not body:
            sys.exit("--body or --body-file is required")
        code, out, err = run(["gh", "issue", "comment", str(number), "-R", repo, "--body", body])
        if code != 0:
            raise RuntimeError(err or out)
        return {"number": number, "message": f"Commented on #{number}"}

    if a == "claim":
        me = gh_login()
        if iss["state"] != "OPEN":
            raise RuntimeError(f"#{number} is closed")
        others = [x for x in iss["assignees"] if x != me]
        if iss["status"] == "In Progress" or others:
            raise RuntimeError(f"#{number} is already claimed (status {iss['status']}, assignees {', '.join(iss['assignees']) or '-'}). "
                               "Pick another issue.")
        if iss["status"] not in ("Ready", None) and not args.force:
            raise RuntimeError(f"#{number} is in {iss['status']}, not Ready. Only Ready issues are built (AGENTS.md §3).")
        if "human-only" in iss["labels"]:
            raise RuntimeError(f"#{number} is labelled human-only")
        if EPIC_LABEL in iss["labels"]:
            raise RuntimeError(f"#{number} is an epic: build its sub-issues instead (issue children {number})")
        code, out, err = run(["gh", "issue", "edit", str(number), "-R", repo, "--add-assignee", "@me"])
        if code != 0:
            raise RuntimeError(err or out)
        board.set_option(iss, "Status", "In Progress")
        tool = args.tool or "an agent"
        where = f" on {args.machine}" if args.machine else ""
        branch = args.branch or f"{number}-<short-title>"
        run(["gh", "issue", "comment", str(number), "-R", repo, "--body",
             f"🤖 Claimed by @{me} via {tool}{where} · branch `{branch}`"])
        return {"number": number, "assignee": me, "message": f"Claimed #{number} for @{me}; status In Progress. "
                f"Branch: git fetch origin && git switch -c {number}-<short-title> origin/main"}

    if a == "close":
        if not args.human:
            raise RuntimeError("Closing an issue is done by /release (human-only). Add --human when running it.")
        board.set_option(iss, "Status", "Done")
        code, out, err = run(["gh", "issue", "close", str(number), "-R", repo, "--reason", "completed"])
        if code != 0:
            raise RuntimeError(err or out)
        return {"number": number, "message": f"#{number} Done and closed"}

    raise RuntimeError(f"Unknown action '{a}'")


def cmd_sync_pr(args):
    """Used by the tracker-sync workflow: move linked issues when a PR opens or merges."""
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    if cfg.get("tracker") != "github":
        print("tracker is not github; nothing to do")
        return
    code, out, err = run(["gh", "pr", "view", str(args.pr), "-R", cfg["github_repo"], "--json",
                          "title,body,headRefName,isDraft"])
    if code != 0:
        sys.exit(f"Can't read PR #{args.pr}: {err}")
    pr = json.loads(out)
    nums = linked_issue_numbers(pr)
    if not nums:
        print(f"PR #{args.pr} doesn't reference an issue (use 'Refs #123' in the description)")
        return
    board = GHProject(cfg)
    board.load()
    target = {"opened": "In Review", "merged": "Deploying"}[args.event]
    keep = {"opened": {"UAT", "Deploying", "Done"}, "merged": {"Done"}}[args.event]
    for n in nums:
        try:
            iss = board.issue(n)
        except RuntimeError as e:
            print(f"#{n}: {e}")
            continue
        if args.event == "opened" and pr.get("isDraft"):
            print(f"#{n}: PR is a draft; leaving status {iss['status']}")
            continue
        if iss["status"] in keep:
            print(f"#{n}: already {iss['status']}; unchanged")
            continue
        board.set_option(iss, "Status", target)
        print(f"#{n}: {iss['status'] or '-'} → {target}")


# ----------------------------------------------------------------------------- testing and shipping

def poll_seconds():
    try:
        return float(os.environ.get("HAAM_POLL_SECONDS", "15"))
    except ValueError:
        return 15.0


def issue_ref(cfg, text):
    """The issue the human means: a number on GitHub Projects, an ID like APP-12 on Linear."""
    t = (text or "").strip()
    if cfg.get("tracker") == "github":
        n = parse_issue_number(t)
        if n is None:
            sys.exit(f"Give the issue number, e.g. #12 (got '{text}')")
        return n
    if not re.fullmatch(r"[A-Za-z]{2,5}-\d+", t):
        sys.exit(f"Give the Linear issue ID, e.g. {cfg['team_key']}-12 (got '{text}')")
    return t.upper()


def show_ref(ref):
    return f"#{ref}" if isinstance(ref, int) else ref


def file_id(ref):
    return f"GH-{ref}" if isinstance(ref, int) else ref


def pr_matches(pr, ref):
    """Strict: the PR's branch or title names this issue (never a mere mention in the description)."""
    head = (pr.get("headRefName") or "").lower()
    if isinstance(ref, int):
        return bool(re.match(rf"^{ref}-", head)) or ref in pr_title_issues(pr)
    key = ref.lower()
    return bool(re.search(rf"(^|/){re.escape(key)}-", head)) or ref in pr_title_issues(pr)


def pr_title_issues(pr):
    """Issues a PR's title names before the colon: '#12: …', or a batch '#12 #13 #14: …' ('APP-12 APP-13: …')."""
    m = re.match(r"\s*((?:(?:#\d+|[A-Za-z]{2,5}-\d+)[\s,]*)+):", pr.get("title") or "")
    if not m:
        return []
    out = []
    for tok in re.findall(r"#\d+|[A-Za-z]{2,5}-\d+", m.group(1)):
        out.append(int(tok[1:]) if tok.startswith("#") else tok.upper())
    return out


def find_pr(cfg, ref, states=("open", "merged")):
    """The PR for an issue (branch `12-…` or title `#12: …`; Linear: `app-12-…` or `APP-12: …`).
    Refuses to guess when more than one PR in the same state matches."""
    for state in states:
        code, out, err = run(["gh", "pr", "list", "-R", cfg["github_repo"], "--state", state, "--limit", "100",
                              "--json", "number,title,headRefName,state,labels,url,isDraft"])
        if code != 0:
            raise RuntimeError(err or out)
        prs = [p for p in json.loads(out or "[]") if pr_matches(p, ref)]
        if len(prs) > 1:
            raise RuntimeError(f"More than one {state} PR matches {show_ref(ref)}: "
                               + ", ".join(f"#{p['number']}" for p in prs) + ". Close the extra one(s) first.")
        if prs:
            return prs[0]
    return None


def tested_file(root):
    _, main, _ = git_paths(root)
    return main / ".haam" / "tested.json"


def remember_tested(root, ref, sha, branch=None):
    f = tested_file(root)
    f.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(f.read_text()) if f.exists() else {}
    data[show_ref(ref)] = sha
    if branch:
        data.setdefault("branches", {})[show_ref(ref)] = branch
    f.write_text(json.dumps(data, indent=2) + "\n")


def tested_sha(root, ref):
    f = tested_file(root)
    return (json.loads(f.read_text()) if f.exists() else {}).get(show_ref(ref))


def tested_branch_of(root, ref):
    f = tested_file(root)
    return ((json.loads(f.read_text()) if f.exists() else {}).get("branches") or {}).get(show_ref(ref))


def cmd_checkout_pr(args):
    """Put the change for an issue on this machine, ready to test (detached, so agents' worktrees aren't disturbed)."""
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    if args.back:
        b = default_base(root)
        base = b.split("/", 1)[1] if b.startswith("origin/") else "main"
        code, _, err = run(["git", "switch", base], cwd=root)
        if code != 0:
            sys.exit(f"Couldn't switch back to {base}: {err}")
        print(f"{OK} Back on {base}. Stop the app if it's still running.")
        return
    if not args.issue:
        sys.exit("Give the issue, e.g. checkout-pr 12")
    ref = issue_ref(cfg, args.issue)
    if git_out(root, "status", "--porcelain", "--untracked-files=no"):
        sys.exit("You have unsaved changes in this folder. Commit them, or copy them somewhere safe and undo them, "
                 "then try again. (Avoid git stash: all worktrees share one stash list, so agents' work gets mixed in.)")
    try:
        pr = None if args.branch else find_pr(cfg, ref, ("open",))
    except RuntimeError as e:
        sys.exit(f"Couldn't pick the pull request: {e}")
    run(["git", "fetch", "--quiet", "--prune", "origin"], cwd=root)
    note = ""
    if pr:
        branch, target = pr["headRefName"], f"origin/{pr['headRefName']}"
    else:
        # Test-first: no PR yet. Test the branch the agent pushed (its hand-over), or one that is only on this
        # computer (worktrees share branches) if it hasn't pushed.
        try:
            branch, target, note = find_branch(root, cfg, ref, args.branch)
        except RuntimeError as e:
            sys.exit(str(e))
        if not branch:
            sys.exit(f"No pull request and no branch found for {show_ref(ref)} (looked for {branch_prefix(ref)}… and the "
                     "branch named in its claim or UAT comment). If the agent used another branch, add --branch <name>.")
    code, _, err = run(["git", "switch", "--quiet", "--detach", target], cwd=root)
    if code != 0:
        sys.exit(f"Couldn't check out {branch}: {err}")
    sha = git_out(root, "rev-parse", "HEAD")
    remember_tested(root, ref, sha, branch)
    # A batch's plan is named after the issue its branch is named after.
    plans = []
    for r in dict.fromkeys(x for x in (ref, branch_issue(branch, ref)) if x is not None):
        plans += [p.relative_to(root).as_posix() for p in sorted((root / "docs/uat").glob(f"{file_id(r)}-*.md"))]
    res = {"issue": show_ref(ref), "pr": pr["number"] if pr else None, "pr_url": pr["url"] if pr else None,
           "branch": branch, "commit": sha, "uat_plan": plans[0] if plans else None,
           "pushed": target.startswith("origin/"), "note": note}
    if args.json:
        print(json.dumps(res, indent=2))
        return
    where = f"PR #{pr['number']}, {pr['url']}" if pr else ("from GitHub, no PR yet" if res["pushed"] else "local, not pushed")
    print(f"{OK} {show_ref(ref)}: testing {branch} at {sha[:8]} ({where})")
    if note:
        print(f"{WARN} {note}")
    print(f"   Test plan: {res['uat_plan'] or 'not found in docs/uat/ (ask the agent to run /uat)'}")
    print("   Next: make setup && make dev, then follow the plan. Afterwards: python3 tools/haam/haam.py checkout-pr --back")


def branch_prefix(ref):
    return f"{ref}-" if isinstance(ref, int) else f"{ref.lower()}-"


def branch_pattern(ref):
    """An issue's branch: '12-…' (GitHub); 'app-12-…' or Linear's 'user/app-12-…'. Spikes never count."""
    return re.compile(rf"^{ref}-" if isinstance(ref, int) else rf"^(?!spike/)(?:[^/]+/)?{re.escape(ref.lower())}-")


def branch_issue(branch, like):
    """The issue a branch is named after ('12-…' → 12, 'app-12-…' → 'APP-12'), or None. `like` picks the tracker's form."""
    b = (branch or "").lower()
    if isinstance(like, int):
        m = re.match(r"^(\d+)-", b)
        return int(m.group(1)) if m else None
    m = re.match(r"^(?!spike/)(?:[^/]+/)?([a-z]{2,5}-\d+)-", b)
    return m.group(1).upper() if m else None


def named_branch(cfg, ref):
    """The branch named in the issue's latest claim or UAT comment ("branch `…`"); a batch's branch is named after its
    first issue, so the other issues are found this way. GitHub Projects only (on Linear, pass --branch)."""
    if cfg.get("tracker") != "github" or not isinstance(ref, int):
        return None
    code, out, _ = run(["gh", "issue", "view", str(ref), "-R", cfg["github_repo"], "--json", "comments"])
    bodies = [c.get("body", "") for c in (json.loads(out).get("comments") or [])] if code == 0 and out else []
    for b_ in reversed(bodies):
        m = re.search(r"branch `([^`\s]+)`", b_)
        if m and "<" not in m.group(1):
            return m.group(1)
    return None


def find_branch(root, cfg, ref, explicit=None):
    """(branch, ref to check out, note) for an issue's branch. The branch on GitHub is the agent's hand-over, so it wins;
    a branch only on this computer (an agent's worktree that hasn't pushed) is the fallback. Refuses to guess."""
    lines = git_out(root, "for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes/origin").splitlines()
    remote = {b[len("origin/"):] for b in lines if b.startswith("origin/") and b != "origin/HEAD"}
    local = {b for b in lines if not b.startswith("origin/") and b != "origin"}
    others = []
    if explicit:
        names = {explicit}
    else:
        pat = branch_pattern(ref)
        pushed = {b for b in remote if pat.search(b.lower())}
        here = {b for b in local if pat.search(b.lower())}
        names = pushed or here           # GitHub's branches are the hand-over; local-only ones are leftovers then
        others = sorted(here - pushed) if pushed else []
        if not names:
            named = named_branch(cfg, ref)
            names = {named} if named else set()
    if len(names) > 1:
        raise RuntimeError(f"Several branches match {show_ref(ref)}: {', '.join(sorted(names))}. "
                           "Delete the stale one(s), or say which with --branch <name>.")
    if not names:
        return None, None, ""
    name = names.pop()
    if name in remote:
        note = (f"Ignoring {', '.join(others)}: only on this computer. " if not explicit and others else "")
        if name in local and git_out(root, "rev-parse", name) != git_out(root, "rev-parse", f"origin/{name}"):
            note += (f"The copy of {name} on this computer differs from GitHub's. Testing GitHub's (the agent's "
                    "hand-over); if the agent has commits it hasn't pushed, ask it to push and test again.")
        return name, f"origin/{name}", note
    if name in local:
        return name, name, f"{name} is only on this computer (not pushed yet). Testing it as it is here."
    if explicit:
        raise RuntimeError(f"There's no branch {explicit}, here or on GitHub.")
    return None, None, ""


def tracker_issues(cfg, ref, branch, also):
    """The issues one PR covers: this one, the issue the branch is named after (a batch), and --also."""
    others = []
    for x in (also or "").split(","):
        if x.strip():
            others.append(issue_ref(cfg, x))
    lead = branch_issue(branch, ref)
    issues = []
    for n in [lead, ref] + others:
        if n is not None and n not in issues:
            issues.append(n)
    return issues


def uat_status_ok(repo, sha):
    """Whether the owner's pass is recorded on this exact commit (the `uat` commit status `publish` posts)."""
    code, data, _ = gh_api("GET", f"repos/{repo}/commits/{sha}/status?per_page=100")   # latest per context
    return code == 0 and isinstance(data, dict) and any(
        s.get("context") == "uat" and s.get("state") == "success" for s in data.get("statuses") or [])


def cmd_publish(args):
    """Test-first flow, after the owner's test passed: push exactly the tested commit and open the PR (already
    labelled uat-passed, with a `uat` status on that commit), so CI and the reviews run once, on tested code."""
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    if not args.human:
        sys.exit("Publishing follows the human's test. Run it only inside /test after they said 'pass', with --human.")
    if git_paths(root)[2]:
        sys.exit("publish runs only from the owner's own chat in the main project folder, never from an agent's worktree.")
    ref = issue_ref(cfg, args.issue)
    repo = cfg["github_repo"]
    sha, tested_branch = tested_sha(root, ref), tested_branch_of(root, ref)
    if not sha:
        sys.exit(f"No record of a test for {show_ref(ref)}. Test it first: python3 tools/haam/haam.py checkout-pr {args.issue}")
    run(["git", "fetch", "--quiet", "--prune", "origin"], cwd=root)
    try:
        pr = find_pr(cfg, ref, ("open",))
        branch = pr["headRefName"] if pr else (tested_branch or find_branch(root, cfg, ref)[0])
    except RuntimeError as e:
        sys.exit(str(e))
    if not branch:
        sys.exit(f"No branch found for {show_ref(ref)}.")
    if tested_branch and branch != tested_branch:
        sys.exit(f"The test was of {tested_branch}, but the PR is on {branch}. Test it again first.")
    issues = tracker_issues(cfg, ref, branch, args.also)     # read before pushing, so a bad ID changes nothing
    tip = (git_out(root, "rev-parse", "--verify", "--quiet", f"origin/{branch}")
           or git_out(root, "rev-parse", "--verify", "--quiet", branch))
    if tip and tip != sha:
        sys.exit(f"{branch} has changed since it was tested ({sha[:8]} → {tip[:8]}). Test it again first.")
    code, _, err = run(["git", "push", "--quiet", "origin", f"{sha}:refs/heads/{branch}"], cwd=root)
    if code != 0:
        sys.exit(f"Couldn't push {branch}: {err[:200]} (if GitHub has commits the test didn't include, test again)")
    who = gh_login() or "the owner"
    when = time.strftime("%Y-%m-%d")
    # The pass belongs to this commit: the gate drops uat-passed when a later push lacks this status.
    code, _, err = gh_api("POST", f"repos/{repo}/statuses/{sha}", {
        "state": "success", "context": "uat", "description": f"Tested and passed by @{who} on {when}"[:140]})
    if code != 0:
        sys.exit(f"Couldn't record the pass on the commit: {(err or '')[:200]}")
    board = None
    labels = ["uat-passed"] + [l for l in (args.label or []) if l != "uat-passed"]
    title = args.title
    if cfg.get("tracker") == "github":
        board = GHProject(cfg)
        board.load()
        title = title or board.issue(issues[0])["title"]
        if any("human-review" in board.issue(n)["labels"] for n in issues) and "human-review" not in labels:
            labels.append("human-review")
    title = title or re.sub(r"^(?:[^/]+/)?(?:\d+|[a-z]{2,5}-\d+)-", "", branch.lower()).replace("-", " ")
    if pr:
        num = str(pr["number"])
        run(["gh", "pr", "edit", num, "-R", repo] + sum((["--add-label", l] for l in labels), []))
        if pr.get("isDraft"):     # after the label, so the ready_for_review run of the gate sees it
            run(["gh", "pr", "ready", num, "-R", repo])
        run(["gh", "pr", "comment", num, "-R", repo, "--body",
             f"✅ Re-tested and passed by @{who} on {when} at `{sha[:8]}`."])
        url = pr["url"]
    else:
        ids = " ".join(show_ref(n) for n in issues)
        refs = "\n".join(f"Refs {show_ref(n)}" for n in issues)
        plan = next(iter(sorted((root / "docs/uat").glob(f"{file_id(issues[0])}-*.md"))), None)
        body = (f"{refs}\n\n## Tested first\n✅ Tested and passed by @{who} on {when} at `{sha[:8]}`, before any "
                "checks ran (HAAM test-first). The checks and reviews below run once, on exactly this commit.\n\n"
                + (f"Test plan: `{plan.relative_to(root).as_posix()}`\n\n" if plan else "")
                + "Acceptance criteria, tests and *Built with*: see the spec, the test plan and the claim comment on the issue.\n")
        f = root / ".haam" / f"pr-{file_id(ref)}.md"
        f.parent.mkdir(exist_ok=True)
        f.write_text(body)
        cmd = ["gh", "pr", "create", "-R", repo, "--head", branch, "--base", cfg.get("default_branch") or "main",
               "--title", f"{ids}: {title}", "--body-file", str(f)]
        for lab in labels:
            cmd += ["--label", lab]
        code, out, err = run(cmd)
        f.unlink()
        if code != 0:
            sys.exit(f"Couldn't open the PR: {(err or out)[:200]}")
        url = out.strip().splitlines()[-1] if out else ""
        num = url.rstrip("/").rsplit("/", 1)[-1]
    # An agent may have pushed between our push and the PR: then the PR isn't what was tested.
    head = pr_head(repo, num)
    if head and head != sha:
        run(["gh", "pr", "edit", num, "-R", repo, "--remove-label", "uat-passed"])
        run(["gh", "pr", "ready", num, "--undo", "-R", repo])      # back to draft: no checks on untested code
        sys.exit(f"{branch} changed while the PR was being opened ({sha[:8]} → {head[:8]}), so it isn't what you tested. "
                 f"Removed uat-passed. Test it again: python3 tools/haam/haam.py checkout-pr {args.issue}")
    linear_steps = []
    for n in issues:
        if board:
            iss = board.issue(n)
            board.set_option(iss, "Status", "In Review")
            run(["gh", "issue", "comment", str(n), "-R", repo, "--body",
                 f"✅ Tested and passed by @{who} at `{sha[:8]}`. PR: {url} (checks running)"])
        else:
            linear_steps.append(f"{show_ref(n)}: status In Review; comment \"✅ Tested and passed by @{who} at "
                                f"{sha[:8]}. PR: {url} (checks running)\"")
    res = {"issue": show_ref(ref), "issues": [show_ref(n) for n in issues], "branch": branch, "commit": sha,
           "pr_url": url, "labels": labels, "tracker_steps": linear_steps}
    if args.json:
        print(json.dumps(res, indent=2))
        return
    print(f"{OK} Pushed {branch} at {sha[:8]} and opened {url}" if not pr else f"{OK} Pushed the tested commit to {url}")
    for s in linear_steps:
        print(f"   Linear (do it with the Linear connection): {s}")
    print("   CI and the reviews run now, once. Then: python3 tools/haam/haam.py ship " + str(args.issue) + " --human")


def cmd_test_failed(args):
    """The owner's test failed: withdraw any earlier pass of that commit (the `uat` status, the PR's uat-passed),
    so neither ship nor the gate can use it. The skills record the failures on the issue."""
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    if not args.human:
        sys.exit("A test result is the human's. Run it only inside /test or /uat-result after they said it failed, with --human.")
    ref = issue_ref(cfg, args.issue)
    repo = cfg["github_repo"]
    sha = tested_sha(root, ref)
    done = []
    if sha:
        code, _, _ = gh_api("POST", f"repos/{repo}/statuses/{sha}", {
            "state": "failure", "context": "uat", "description": f"Failed the owner's test on {time.strftime('%Y-%m-%d')}"})
        if code == 0:      # a commit that never reached GitHub has nothing to withdraw
            done.append(f"marked {sha[:8]} as failed")
    try:
        pr = find_pr(cfg, ref, ("open",))
    except RuntimeError as e:
        sys.exit(str(e))
    if pr and "uat-passed" in [l["name"] for l in pr.get("labels") or []]:
        run(["gh", "pr", "edit", str(pr["number"]), "-R", repo, "--remove-label", "uat-passed"])
        done.append(f"removed uat-passed from PR #{pr['number']}")
    res = {"issue": show_ref(ref), "commit": sha, "pr": pr["number"] if pr else None, "done": done}
    if args.json:
        print(json.dumps(res, indent=2))
        return
    print(f"{OK} {show_ref(ref)}: " + ("; ".join(done) if done else "no earlier pass to withdraw"))


SHIP_NOT_FINISHED = 2   # exit code: nothing went wrong, it just isn't finished; run the same command again
SHIP_WAITING_HUMAN = 3  # exit code: waiting for the human (manual deploy): don't re-run until they say it's live


def checks_grace_seconds():
    """How long a just-opened PR may show no checks before that counts as a problem (they take a moment to start)."""
    try:
        return float(os.environ.get("HAAM_CHECKS_GRACE_SECONDS", "300"))
    except ValueError:
        return 300.0


def pr_checks(repo, num):
    """(passed, pending, failed) check names for a PR, from GitHub; None while no check has started yet."""
    code, out, err = run(["gh", "pr", "checks", str(num), "-R", repo, "--json", "name,bucket"])
    if code != 0 and "no checks reported" in (err or out or "").lower():
        return None
    if code not in (0, 8) or not out:   # gh exits 8 while checks are pending
        raise RuntimeError(f"Couldn't read the PR's checks: {(err or out)[:200]}")
    checks = json.loads(out)
    passed = [c["name"] for c in checks if c["bucket"] in ("pass", "skipping")]
    pending = [c["name"] for c in checks if c["bucket"] == "pending"]
    failed = [c["name"] for c in checks if c["bucket"] in ("fail", "cancel")]
    return passed, pending, failed


def pr_quiet_seconds(repo, num):
    """Seconds since the PR was last updated (opened, marked ready, labelled), or None if unknown."""
    code, out, _ = run(["gh", "pr", "view", str(num), "-R", repo, "--json", "updatedAt"])
    try:
        return time.time() - iso_time(json.loads(out)["updatedAt"]).timestamp() if code == 0 and out else None
    except (KeyError, TypeError, ValueError):
        return None


def pr_head(repo, num):
    code, out, _ = run(["gh", "pr", "view", str(num), "-R", repo, "--json", "headRefOid"])
    return (json.loads(out).get("headRefOid") if code == 0 and out else "") or ""


def cmd_ship(args):
    """After the human passed UAT and said 'ship': merge, approve the production deploy, wait, close the issue.
    Safe to run again: it carries on from wherever the last run stopped.
    Exit codes: 0 live, 2 not finished yet (run again), 3 waiting for the human to deploy by hand, 1 stopped."""
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    if not args.human:
        sys.exit("Shipping is the human's decision. Run it only inside /test (after the human said 'pass' and "
                 "'ship') or /release (with --merged-only), and add --human.")
    if git_paths(root)[2]:
        sys.exit("ship runs only from the owner's own chat in the main project folder, never from an agent's worktree.")
    ref = issue_ref(cfg, args.issue)
    repo = cfg["github_repo"]
    deadline = time.time() + args.wait * 60
    steps = []

    def say(msg):
        steps.append(msg)
        if not args.json:
            print(msg, flush=True)

    def finish(state, code=0, message="", **extra):
        if args.json:
            print(json.dumps({"ok": code == 0, "issue": show_ref(ref), "state": state, "message": message,
                              "steps": steps, **extra}, indent=2))
        elif message:
            print(message, flush=True)
        sys.exit(code)

    def stop(message):
        say(f"{BAD} {message}")
        finish("stopped", 1, "Stopped: this needs the human. " + message)

    def later(state, message):
        finish(state, SHIP_NOT_FINISHED, f"Not finished yet ({state}). {message} Run the same command again.")

    try:
        pr = find_pr(cfg, ref)
    except RuntimeError as e:
        stop(str(e))
    if not pr:
        stop(f"No pull request found for {show_ref(ref)}.")
    num = str(pr["number"])
    labels = [l["name"] for l in pr.get("labels") or []]

    # 1. Merge (only from /test, after pass + ship)
    if pr["state"] == "OPEN":
        if args.merged_only:
            stop(f"PR #{num} isn't merged yet. Use /test, so the human tests it and says 'ship'.")
        if pr.get("isDraft"):
            stop(f"PR #{num} is still a draft.")
        sha = tested_sha(root, ref)
        if "uat-passed" not in labels and "gate-override" not in labels:
            # The gate drops the label when a push races it; the `uat` status on the tested head is the owner's pass.
            if not (sha and pr_head(repo, num) == sha and uat_status_ok(repo, sha)):
                stop(f"PR #{num} hasn't passed UAT (no 'uat-passed' label). Record the human's test result first.")
            run(["gh", "pr", "edit", num, "-R", repo, "--add-label", "uat-passed"])
            labels.append("uat-passed")
            say(f"{INFO} Put back 'uat-passed': the owner's pass is recorded on this exact commit")
        if not sha:
            say(f"{WARN} No record of which commit the human tested (they didn't use checkout-pr); merging the current head")
        said_waiting = False
        started = time.time()
        while True:
            try:
                checks = pr_checks(repo, num)
            except RuntimeError as e:
                stop(str(e))
            passed, pending, failed = checks or ([], [], [])
            # Checks take a moment to start on a just-opened PR, and the gate a moment to re-run after a label
            # change. Measured from the PR's last update, so running ship again doesn't restart the clock.
            age = pr_quiet_seconds(repo, num)
            settling = (time.time() - started if age is None else age) < checks_grace_seconds()
            if settling and "release-gate" in failed and "uat-passed" in labels:
                failed = [c for c in failed if c != "release-gate"]
                pending = pending + ["release-gate (re-checking)"]
            if failed:
                stop(f"Checks failing on PR #{num}: {', '.join(failed)}. Send it back to an agent.")
            if "release-gate" not in passed and "release-gate" not in pending:
                if settling:
                    pending = pending + ["release-gate (starting)"]
                elif checks is None:
                    stop(f"No checks have started on PR #{num}. Check that GitHub Actions is on for this repository.")
                else:
                    stop(f"PR #{num} has no 'release-gate' check. The UAT gate isn't set up (haam.py github --apply).")
            if not pending:
                head = pr_head(repo, num)
                if sha and head and head != sha:
                    stop(f"PR #{num} changed after the human tested it. Test it again with /test.")
                cmd = ["gh", "pr", "merge", num, "-R", repo, "--squash"] + (["--match-head-commit", sha] if sha else [])
                code, out, err = run(cmd)
                if code == 0:
                    say(f"{OK} Merged PR #{num}")
                    break
                msg = (err or out)[:300]
                code2, out2, _ = run(["gh", "pr", "view", num, "-R", repo, "--json", "mergeStateStatus"])
                mstate = (json.loads(out2).get("mergeStateStatus") if code2 == 0 and out2 else "") or ""
                if mstate == "DIRTY":
                    stop(f"PR #{num} has merge conflicts with main. Send it back to an agent to rebase.")
                if mstate not in ("BLOCKED", "UNKNOWN", "UNSTABLE", ""):
                    stop(f"GitHub refused the merge: {msg}")
                if mstate == "BLOCKED" and not pending:
                    stop(f"GitHub is blocking the merge (a required review or another rule): {msg}")
            if time.time() > deadline:
                later("waiting for checks", f"Checks still running on PR #{num}: {', '.join(pending) or 'starting'}.")
            if not said_waiting:
                say(f"{INFO} Waiting for the checks to finish before merging…")
                said_waiting = True
            time.sleep(poll_seconds())
        gh_api("DELETE", f"repos/{repo}/git/refs/heads/{pr['headRefName']}")

    code, out, err = run(["gh", "pr", "view", num, "-R", repo, "--json", "state,mergeCommit,mergedAt,files,url"])
    view = json.loads(out) if code == 0 and out else {}
    sha = (view.get("mergeCommit") or {}).get("oid")
    if view.get("state") != "MERGED" or not sha:
        stop(f"PR #{num} isn't merged (state {view.get('state') or pr['state']}).")
    files = [f.get("path", "") for f in view.get("files") or []]
    docs_only = bool(files) and all(p.startswith("docs/") or p.endswith(".md") for p in files)

    board = None
    if cfg.get("tracker") == "github":
        board = GHProject(cfg)
        board.load()
        iss = board.issue(ref)
        if iss["status"] not in ("Deploying", "Done"):
            board.set_option(iss, "Status", "Deploying")

    # 2. Deploy: approve the production environment and wait
    run_info = None
    manual = cfg.get("deploy") == "manual"
    if args.no_deploy or args.live:
        say(f"{INFO} The human confirmed it's live")
    elif manual:
        say(f"{INFO} Merged. This project deploys by hand")
        finish("deploy by hand", SHIP_WAITING_HUMAN, "Waiting for the human: deploy it your usual way, then say it's live "
               "(the agent runs this again with --live to close the issue).")
    elif docs_only:
        say(f"{INFO} Docs-only change: nothing to deploy")
    else:
        while True:
            code, out, err = run(["gh", "run", "list", "-R", repo, "--workflow", args.workflow, "--commit", sha,
                                  "--json", "databaseId,status,conclusion,url"])
            if code != 0:
                stop(f"Couldn't list the deploy runs: {(err or out)[:200]}")
            runs = json.loads(out or "[]")
            run_info = runs[0] if runs else None
            if run_info and run_info["status"] == "completed":
                if run_info["conclusion"] == "success":
                    say(f"{OK} Deployed: {run_info['url']}")
                    break
                say(f"{BAD} The deploy failed: {run_info['url']}")
                finish("deploy failed", 1, "The deploy failed. Show the human the run; report it as an Urgent bug "
                       "if production is affected.", run=run_info["url"])
            if run_info and run_info["status"] == "waiting":
                code, pend, err = gh_api("GET", f"repos/{repo}/actions/runs/{run_info['databaseId']}/pending_deployments")
                pend = pend if isinstance(pend, list) else []
                mine = [p["environment"]["id"] for p in pend if p.get("current_user_can_approve", True)]
                if pend and not mine:
                    later("waiting for deploy approval", "You can't approve this environment: the approver must "
                          "approve it in GitHub (Actions → the run → Review deployments).")
                if mine:
                    code, _, err = gh_api("POST", f"repos/{repo}/actions/runs/{run_info['databaseId']}/pending_deployments",
                                          {"environment_ids": mine, "state": "approved",
                                           "comment": f"Approved by {gh_login() or 'the product owner'} after UAT (HAAM ship)"})
                    if code != 0:
                        stop(f"Couldn't approve the deploy ({str(err)[:150]}). Approve it in GitHub: Actions → "
                             "the run → Review deployments.")
                    say(f"{OK} Approved the production deploy")
            if time.time() > deadline:
                if run_info:
                    later("deploying", f"Deploy run: {run_info['url']}.")
                merged_at = view.get("mergedAt") or ""
                try:
                    from datetime import datetime, timezone
                    age = (datetime.now(timezone.utc) - datetime.fromisoformat(merged_at.replace("Z", "+00:00"))).total_seconds()
                except ValueError:
                    age = 0
                if age < 600:
                    later("waiting for the deploy to start", f"No '{args.workflow}' run for the merge yet.")
                stop(f"No '{args.workflow}' run started for the merge commit. Ask the human how this project "
                     "deploys; only if they confirm it's live, run again with --no-deploy.")
            time.sleep(poll_seconds())

    # 3. Close the issue(s) (once). A batch PR ('#12 #13: …') closes every issue it names.
    where = f" · deploy run {run_info['url']}" if run_info else ""
    others = [r for r in pr_title_issues(pr) if isinstance(r, type(ref)) and r != ref]
    for extra in others:
        if board:
            e = board.issue(extra)
            if e["state"] == "OPEN":
                board.set_option(e, "Status", "Done")
                run(["gh", "issue", "comment", str(extra), "-R", repo, "--body", f"🚀 Released to production with #{ref}{where}"])
                run(["gh", "issue", "close", str(extra), "-R", repo, "--reason", "completed"])
                say(f"{OK} #{extra} is live and Done (same PR)")
        else:
            say(f"{INFO} Also set {show_ref(extra)} to Done in Linear (same PR)")
    if board:
        iss = board.issue(ref)
        if iss["status"] != "Done" or iss["state"] == "OPEN":
            board.set_option(iss, "Status", "Done")
            run(["gh", "issue", "comment", str(ref), "-R", repo, "--body", f"🚀 Released to production{where}"])
            if iss["state"] == "OPEN":
                run(["gh", "issue", "close", str(ref), "-R", repo, "--reason", "completed"])
        say(f"{OK} {show_ref(ref)} is live and Done")
        if iss.get("parent"):
            _, subs = board.sub_issues(iss["parent"])
            if subs and all(k["state"] == "CLOSED" or k["number"] == ref for k in subs):
                say(f"{INFO} That was the last open issue in epic #{iss['parent']}. Close the epic too if the human agrees: "
                    f"issue close {iss['parent']} --human")
    else:
        say(f"{INFO} Now set {show_ref(ref)} to Done in Linear and comment: Released to production{where}")
    tf = tested_file(root)
    if tf.exists():
        data = json.loads(tf.read_text())
        data.pop(show_ref(ref), None)
        (data.get("branches") or {}).pop(show_ref(ref), None)
        tf.write_text(json.dumps(data, indent=2) + "\n")
    finish("live", 0, f"{show_ref(ref)} is live.", run=run_info["url"] if run_info else None)


def cmd_capacity(args):
    """Whether agents should start new work: open PRs and changes waiting in UAT against the limits in haam.config.json."""
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    max_prs = int(cfg.get("max_open_prs") or DEFAULT_CONFIG["max_open_prs"])
    max_uat = int(cfg.get("max_in_uat") or DEFAULT_CONFIG["max_in_uat"])
    code, out, err = run(["gh", "pr", "list", "-R", cfg.get("github_repo") or "", "--state", "open", "--limit", "200",
                          "--json", "number,title,isDraft,author"])
    if code != 0:
        sys.exit(f"Couldn't count open pull requests: {(err or out)[:200]}")
    # Bots' PRs (Dependabot…) cost CI too, but they shouldn't stop the agents' own work.
    counted = [p for p in json.loads(out or "[]")
               if not ((p.get("author") or {}).get("login", "").endswith("[bot]") or (p.get("author") or {}).get("is_bot"))]
    open_prs = len(counted)
    uat_items = []
    in_uat = args.in_uat     # Linear: the agent counts the UAT items with the Linear connection and passes them
    if in_uat is None and cfg.get("tracker") == "github":
        try:
            board = GHProject(cfg)
            board.load()
            uat_items = [i for i in board.items() if i["status"] == "UAT" and i["state"] == "OPEN"]
            in_uat = len(uat_items)
        except RuntimeError:
            in_uat = None
    reasons = []
    if open_prs >= max_prs:
        reasons.append(f"{open_prs} open PRs (limit {max_prs})")
    if in_uat is not None and in_uat >= max_uat:
        reasons.append(f"{in_uat} changes waiting for the owner to test (limit {max_uat})")
    if in_uat is None:
        reasons_note = "UAT queue not counted (Linear: count the UAT items and pass --in-uat N)"
    else:
        reasons_note = ""
    res = {"hold": bool(reasons), "open_prs": open_prs, "max_open_prs": max_prs, "in_uat": in_uat,
           "max_in_uat": max_uat, "reasons": reasons, "note": reasons_note,
           "counted_prs": [{"number": p["number"], "title": p.get("title", ""), "draft": bool(p.get("isDraft"))}
                           for p in counted],
           "uat_issues": [{"number": i["number"], "title": i.get("title", "")} for i in uat_items]}
    if args.json:
        print(json.dumps(res, indent=2))
        return
    if reasons:
        print(f"{WARN} Hold new work: " + "; ".join(reasons) + ". Rework (uat-failed) and finishing open PRs are still fine.")
    else:
        print(f"{OK} Room for new work: {open_prs}/{max_prs} open PRs" + (f", {in_uat}/{max_uat} in UAT" if in_uat is not None else ""))
    if reasons_note:
        print(f"{INFO} {reasons_note}")
    if args.list or reasons:
        for p in counted:
            print(f"   PR #{p['number']}{' (draft)' if p.get('isDraft') else ''}: {p.get('title', '')}")
        for i in uat_items:
            print(f"   In UAT: #{i['number']} {i.get('title', '')}")
        if reasons:
            print("   To make room: test and ship what's waiting (/test); close PRs that are stale, red or untested "
                  "(test-first works from the branch, so closing loses nothing); or raise the limits: "
                  "haam.py config --max-open-prs N --max-in-uat N")


# ----------------------------------------------------------------------------- CI cost: usage, settings, local review

RUNNER_MULTIPLIER = {"linux": 1, "windows": 2, "macos": 10}   # how GitHub counts minutes of hosted runners


def iso_time(s):
    from datetime import datetime
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def cmd_ci_usage(args):
    """Where the GitHub Actions minutes went over the last N days, by workflow, job, event and day."""
    import math
    from collections import defaultdict
    from datetime import datetime, timedelta, timezone
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    repo = args.repo or cfg.get("github_repo")
    if not repo:
        sys.exit("Set github_repo first: python3 tools/haam/haam.py config --github-repo owner/name")
    since = (datetime.now(timezone.utc) - timedelta(days=args.days)).date().isoformat()
    runs, page = [], 1
    while len(runs) < args.max_runs:
        code, out, err = run(["gh", "api", f"repos/{repo}/actions/runs?created=%3E%3D{since}&per_page=100&page={page}"])
        if code != 0:
            sys.exit(f"Couldn't list workflow runs: {(err or out)[:200]}")
        batch = json.loads(out or "{}").get("workflow_runs") or []
        runs += batch
        if len(batch) < 100:
            break
        page += 1
    runs = runs[:args.max_runs]
    by_wf, by_job, by_event, by_day = defaultdict(int), defaultdict(int), defaultdict(int), defaultdict(int)
    own_runner_min, total, prs = 0, 0, set()
    for r in runs:
        code, out, _ = run(["gh", "api", f"repos/{repo}/actions/runs/{r['id']}/jobs?per_page=100&filter=all"])
        jobs = (json.loads(out or "{}").get("jobs") or []) if code == 0 else []
        for j in jobs:
            if not j.get("started_at") or not j.get("completed_at") or j.get("conclusion") == "skipped":
                continue
            secs = (iso_time(j["completed_at"]) - iso_time(j["started_at"])).total_seconds()
            if secs <= 0:
                continue
            labels = " ".join(j.get("labels") or []).lower()
            mins = math.ceil(secs / 60)                          # GitHub rounds each job up to the minute
            group = j.get("runner_group_name")
            if "self-hosted" in labels or (group and group != "GitHub Actions"):
                own_runner_min += mins
                continue
            mins *= RUNNER_MULTIPLIER["macos" if "mac" in labels else "windows" if "windows" in labels else "linux"]
            total += mins
            by_wf[r.get("name") or "?"] += mins
            by_job[f"{r.get('name') or '?'} / {j.get('name') or '?'}"] += mins
            by_event[r.get("event") or "?"] += mins
            by_day[(r.get("created_at") or "")[:10]] += mins
        for p in r.get("pull_requests") or []:
            prs.add(p.get("number"))
    res = {"repo": repo, "days": args.days, "runs": len(runs), "billable_minutes": total,
           "own_runner_minutes": own_runner_min, "pull_requests": len(prs),
           "minutes_per_pr": round(total / len(prs), 1) if prs else None,
           "by_workflow": dict(sorted(by_wf.items(), key=lambda x: -x[1])),
           "by_job": dict(sorted(by_job.items(), key=lambda x: -x[1])[:15]),
           "by_event": dict(sorted(by_event.items(), key=lambda x: -x[1])), "by_day": dict(sorted(by_day.items()))}
    if args.json:
        print(json.dumps(res, indent=2))
        return
    print(f"{c('1', f'GitHub Actions minutes for {repo}, last {args.days} day(s)')}  ({len(runs)} runs)")
    print(f"  Billable minutes (estimate): {total}" + (f"   ·  on your own runner: {own_runner_min} (not billed as hosted minutes)" if own_runner_min else ""))
    if prs:
        print(f"  Pull requests with runs: {len(prs)}  ·  about {res['minutes_per_pr']} minutes each")
    for title, d in (("By workflow", res["by_workflow"]), ("Biggest jobs", res["by_job"]), ("By trigger", res["by_event"]),
                     ("By day", res["by_day"])):
        if d:
            print(f"\n{c('1', title)}")
            for k, v in d.items():
                print(f"  {v:>6}  {k}")
    print(c("2", "\nEstimate from job durations (rounded up per job; macOS counts 10x, Windows 2x). GitHub's billing page is the exact figure."))


def cmd_ci_settings(args):
    """Where CI runs and where the AI reviews run, set as repository variables the workflows read."""
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    rep = Report()
    rep.section("CI settings")
    if not gh_ready(rep, cfg):
        rep.print(args.json)
        return
    repo = cfg["github_repo"]
    code, out, _ = run(["gh", "variable", "list", "-R", repo, "--json", "name,value"])
    current = {v["name"]: v["value"] for v in json.loads(out or "[]")} if code == 0 else {}
    code, info, _ = gh_api("GET", f"repos/{repo}")
    private = bool(info.get("private")) if code == 0 and isinstance(info, dict) else False   # unknown: assume public
    rep.add("info", f"Runner: {current.get('HAAM_RUNNER') or 'GitHub-hosted (ubuntu-24.04)'}")
    rep.add("info", f"AI reviews: {current.get('HAAM_REVIEW') or 'github'}")
    changes = []
    if args.runner is not None:
        want = "" if args.runner in ("github", "") else args.runner
        if want and not private:
            rep.add("fail", "Own runners only on private repositories" if code == 0 else
                    "Couldn't confirm the repository is private, so the runner wasn't changed",
                    "on a public repository anyone's pull request could run code on your machine")
            want = None
        if want is not None and want != current.get("HAAM_RUNNER", ""):
            changes.append(("HAAM_RUNNER", want))
        if want:
            rep.add("warn", f"Jobs will run on runners labelled '{want}'",
                    "the machine must be on and registered (Settings → Actions → Runners → New self-hosted runner), "
                    "with git, make, Python 3, curl and gitleaks installed, and your project's own tools")
    if args.review is not None:
        if args.review not in ("github", "local"):
            sys.exit("--review must be github or local")
        if args.review != (current.get("HAAM_REVIEW") or "github"):
            changes.append(("HAAM_REVIEW", "" if args.review == "github" else "local"))
        cfg["review"] = args.review
        if args.review == "local":
            rep.add("warn", "AI reviews will run on your computer (haam.py review), not on GitHub's runners",
                    "uses your Claude plan instead of Actions minutes. Trade-off: the result is no longer tamper-proof. "
                    "The agent that built the change starts the review (in fresh, read-only sessions), and anything "
                    "using your login could post a passing result. PRs labelled human-review are always reviewed on GitHub.")
    for name, value in changes:
        if not args.apply:
            rep.add("warn", f"Will set {name} = {value or '(default)'}")
            continue
        cmd = (["gh", "variable", "set", name, "--body", value, "-R", repo] if value
               else ["gh", "variable", "delete", name, "-R", repo])
        c2, _, e2 = run(cmd)
        rep.add("ok" if c2 == 0 or not value else "fail", f"{name} = {value or '(default)'}", (e2 or "")[:120] if c2 else "")
    if args.apply and args.review is not None:
        save_config(root, cfg)
        rep.action(WHO_AGENT, f"Commit {CONFIG_NAME} and get it merged, so every agent knows reviews are {args.review}")
    if changes and not args.apply:
        rep.add("info", "Plan only. Re-run with --apply")
    rep.print(args.json)


REVIEW_DENY = "Bash,Edit,Write,MultiEdit,NotebookEdit,WebFetch,WebSearch,Task,Agent"
MAX_DIFF = 200_000


def review_inputs(root, repo, num, sha):
    """Everything the reviewer needs, gathered by this tool, so the reviewer itself needs no commands.
    The instructions come from origin/main, not from the PR's branch (which the PR's author controls)."""
    base = git_out(root, "merge-base", "origin/main", sha) or "origin/main"
    diff = git_out(root, "diff", f"{base}..{sha}")
    if len(diff) > MAX_DIFF:
        diff = diff[:MAX_DIFF] + "\n\n[diff truncated: read the remaining files directly]"
    rules = git_out(root, "show", "origin/main:.github/review/REVIEWER.md") or "(REVIEWER.md not found on main)"
    code, out, _ = run(["gh", "pr", "view", str(num), "-R", repo, "--json", "title,body"])
    meta = json.loads(out) if code == 0 and out else {}
    spec_note = ""
    for n in pr_title_issues(meta) or []:
        if not isinstance(n, int):
            continue
        c2, o2, _ = run(["gh", "issue", "view", str(n), "-R", repo, "--json", "comments"])
        bodies = [c.get("body", "") for c in (json.loads(o2).get("comments") or [])] if c2 == 0 and o2 else []
        approved = [m.group(1) for b_ in bodies for m in [re.search(r"Spec approved by .*? at ([0-9a-f]{7,40})", b_)] if m]
        if approved:
            changed = git_out(root, "diff", "--stat", f"{approved[-1]}..{sha}", "--", "docs/specs/")
            spec_note += (f"\nIssue #{n}: spec approved at {approved[-1]}. Spec changes since then:\n"
                          f"{changed or '(none)'}\n")
    return meta, diff, rules, spec_note or "\n(No 'spec approved' comment found.)\n"


def review_prompts(repo, num, sha, meta, diff, rules, spec_note):
    head = (f"You are an independent reviewer for pull request #{num} in {repo}, at commit {sha}. You did not write "
            "this code. The folder you're in is a clean checkout of that commit: read any file you need. You can't "
            "run commands and must not change files; everything else you need is below.\n\n"
            f"PR title: {meta.get('title', '')}\nPR description:\n{meta.get('body', '')}\n\n"
            f"Spec approval check:{spec_note}\nThe diff (base...{sha}):\n```diff\n{diff}\n```\n")
    code = (head + "\nFollow these review instructions (from the main branch), but instead of posting a comment or "
            "writing a file, reply with the review comment itself in Markdown, then a last line that is exactly "
            "`VERDICT: APPROVE` or `VERDICT: CHANGES_REQUESTED`.\n\n" + rules)
    security = (head + "\nReview it for security only: real, exploitable problems such as secrets or credentials, "
                "injection, missing authorisation, unsafe handling of personal data, insecure defaults, dangerous "
                "dependencies; and section D of the review instructions below. Report only findings you're confident "
                "about, each with file, line, risk and fix. Reply in Markdown, then a last line that is exactly "
                "`SECURITY_FINDINGS: <number>`.\n\n" + rules)
    return code, security


def run_reviewer(cmd_template, prompt, cwd, timeout_min):
    template = cmd_template or ["claude", "-p", "{prompt}", "--allowedTools", "Read,Glob,Grep",
                                "--disallowedTools", REVIEW_DENY]
    cmd = [prompt if part == "{prompt}" else part for part in template]
    if not shutil.which(cmd[0]):
        raise RuntimeError(f"'{cmd[0]}' isn't installed. Install Claude Code, or set \"review_command\" in "
                           "haam.config.json on main for your tool (with {prompt} where the instructions go).")
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout_min * 60,
                           stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"The reviewer didn't finish within {timeout_min} minutes")
    return p.stdout or ""


def cmd_review(args):
    """Run the two independent reviews on this machine, in fresh agent sessions that can only read a clean
    checkout of the PR's commit, and post them as the PR's comments and ai-review / security-review statuses.
    For projects that chose `ci-settings --review local`."""
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    repo = cfg["github_repo"]
    num = args.pr
    if not num:
        if not args.issue:
            sys.exit("Give the issue (review 12) or the PR (--pr 34)")
        try:
            pr = find_pr(cfg, issue_ref(cfg, args.issue), ("open",))
        except RuntimeError as e:
            sys.exit(str(e))
        if not pr:
            sys.exit(f"No open pull request for {args.issue}")
        num = pr["number"]

    def head():
        code, out, err = run(["gh", "pr", "view", str(num), "-R", repo, "--json", "headRefOid,labels,isDraft,url"])
        if code != 0:
            sys.exit(f"Couldn't read PR #{num}: {err}")
        return json.loads(out)

    pr = head()
    labels = [l["name"] for l in pr.get("labels") or []]
    if "human-review" in labels:
        sys.exit(f"PR #{num} touches a protected area (label human-review): its AI reviews run on GitHub, not here.")
    if pr.get("isDraft"):
        sys.exit(f"PR #{num} is still a draft. Mark it ready first (gh pr ready {num}).")
    sha = pr["headRefOid"]
    run(["git", "fetch", "--quiet", "origin", "main"], cwd=root)
    run(["git", "fetch", "--quiet", "origin", f"+refs/pull/{num}/head:refs/remotes/origin/pr/{num}"], cwd=root)
    # The reviewer runs with the main branch's settings, not anything the PR's branch could change.
    main_cfg = {}
    try:
        main_cfg = json.loads(git_out(root, "show", f"origin/main:{CONFIG_NAME}") or "{}")
    except ValueError:
        pass
    who = gh_login() or "the owner"
    machine = os.uname().nodename if hasattr(os, "uname") else "this computer"

    def post(context, state, desc):
        c2, _, e2 = gh_api("POST", f"repos/{repo}/statuses/{sha}", {"state": state, "context": context,
                                                                   "description": desc[:140]})
        if c2 != 0:
            raise RuntimeError(f"Couldn't post the {context} status: {str(e2)[:160]}")

    _, main_dir, _ = git_paths(root)
    checkout = main_dir / WORKTREE_DIR / f"review-pr-{num}"
    results = {}
    try:
        if checkout.exists():
            run(["git", "worktree", "remove", "--force", str(checkout)], cwd=main_dir)
        code, _, err = run(["git", "worktree", "add", "--quiet", "--detach", str(checkout), sha], cwd=main_dir)
        if code != 0:
            raise RuntimeError(f"Couldn't check out the PR's commit {sha[:8]}: {err}")
        meta, diff, rules, spec_note = review_inputs(root, repo, num, sha)
        code_prompt, sec_prompt = review_prompts(repo, num, sha, meta, diff, rules, spec_note)
        for context, prompt in (("ai-review", code_prompt), ("security-review", sec_prompt)):
            if args.only and args.only != context:
                continue
            post(context, "pending", f"Local review running ({who} on {machine})")
            try:
                text = run_reviewer(main_cfg.get("review_command"), prompt, checkout, args.timeout)
            except RuntimeError as e:
                post(context, "error", f"Local review didn't finish: {e}"[:140])
                raise
            lines = text.strip().splitlines()
            tail = [l.strip().strip("`*") for l in lines[-5:]]
            if context == "ai-review":
                verdict = next((l.split(":", 1)[1].strip() for l in reversed(tail) if l.startswith("VERDICT:")), "")
                state = {"APPROVE": "success", "CHANGES_REQUESTED": "failure"}.get(verdict, "error")
                desc = {"success": "Local AI review approved", "failure": "Changes requested: see PR comment"}.get(
                    state, "Local review gave no verdict: run it again")
                title = "🤖 Independent review (local)"
            else:
                m = next((l for l in reversed(tail) if l.startswith("SECURITY_FINDINGS:")), "")
                n = m.split(":", 1)[1].strip() if m else ""
                state = "success" if n == "0" else "failure" if n.isdigit() else "error"
                desc = {"success": "No security findings (local review)",
                        "failure": f"{n} security finding(s): see PR comment"}.get(state, "Local security review gave no result")
                title = "🔒 Security review (local)"
            if head()["headRefOid"] != sha:
                post(context, "error", "The PR changed during the review: run it again")
                raise RuntimeError(f"PR #{num} changed while it was being reviewed. Run the review again.")
            body = "\n".join(l for l in lines if not l.strip().strip("`*").startswith(("VERDICT:", "SECURITY_FINDINGS:")))
            note = Path(checkout.parent / f"review-pr-{num}-{context}.md")
            note.write_text(f"### {title}\n_Commit {sha[:8]} · run by {who} on {machine} with `haam.py review`._\n\n{body}\n")
            run(["gh", "pr", "comment", str(num), "-R", repo, "--body-file", str(note)])
            note.unlink()
            post(context, state, f"{desc} · {who} on {machine}")
            results[context] = state
    except RuntimeError as e:
        sys.exit(str(e))
    finally:
        if checkout.exists():
            run(["git", "worktree", "remove", "--force", str(checkout)], cwd=main_dir)
    if args.json:
        print(json.dumps({"pr": num, "commit": sha, "results": results}, indent=2))
        return
    for k, v in results.items():
        print(f"{OK if v == 'success' else BAD} {k}: {v}")
    if any(v != "success" for v in results.values()):
        print("Fix the findings (see the PR comments), push once, and run the review again.")

# ----------------------------------------------------------------------------- worktrees (parallel chats)

WORKTREE_DIR = ".claude/worktrees"   # same place Claude Code uses, so both kinds are listed and cleaned together
WORKTREE_INCLUDE = ".worktreeinclude"
WORKTREE_IDLE_HOURS = 24


def git_out(cwd, *a):
    code, out, _ = run(["git", *a], cwd=cwd)
    return out if code == 0 else ""


def git_paths(cwd):
    """(this checkout's top folder, the main checkout's top folder, True if this is a linked worktree)."""
    top = Path(git_out(cwd, "rev-parse", "--show-toplevel") or cwd).resolve()
    gd = git_out(top, "rev-parse", "--git-dir")
    cd = git_out(top, "rev-parse", "--git-common-dir")
    git_dir = (top / gd).resolve() if gd else top / ".git"
    common = (top / cd).resolve() if cd else git_dir
    main = common.parent if common.name == ".git" else top
    return top, main, git_dir != common


def default_base(root):
    ref = git_out(root, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if ref:
        return ref
    if git_out(root, "rev-parse", "--verify", "--quiet", "origin/main"):
        return "origin/main"
    return "HEAD"


def include_patterns(main):
    f = main / WORKTREE_INCLUDE
    if not f.exists():
        return []
    return [l.strip() for l in f.read_text().splitlines() if l.strip() and not l.strip().startswith("#")]


def copy_includes(main, dest):
    """Copy git-ignored local files listed in .worktreeinclude (e.g. .env) from the main folder into a
    worktree. Never overwrites, never copies tracked files, never prints contents. Returns (copied, skipped)."""
    copied, skipped = [], []
    if main.resolve() == dest.resolve():
        return copied, skipped
    for pat in include_patterns(main):
        pat = pat.lstrip("/")
        for src in sorted(main.glob(pat)):
            if not src.is_file() or WORKTREE_DIR in src.relative_to(main).as_posix():
                continue
            rel = src.relative_to(main).as_posix()
            if run(["git", "check-ignore", "-q", rel], cwd=main)[0] != 0:
                skipped.append(rel + " (tracked or not git-ignored)")
                continue
            target = dest / rel
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
            copied.append(rel)
    return copied, skipped


def list_worktrees(root):
    _, main, _ = git_paths(root)
    out, cur = [], {}
    for line in git_out(main, "worktree", "list", "--porcelain").splitlines() + [""]:
        if not line:
            if cur:
                out.append(cur)
            cur = {}
            continue
        key, _, val = line.partition(" ")
        if key == "worktree":
            cur = {"path": val, "branch": "", "detached": False, "locked": False}
        elif key == "branch":
            cur["branch"] = val.replace("refs/heads/", "", 1)
        elif key == "detached":
            cur["detached"] = True
        elif key == "locked":
            cur["locked"] = True
        elif key == "HEAD":
            cur["head"] = val
    for w in out:
        p = Path(w["path"])
        w["main"] = p.resolve() == main.resolve()
        w["haam_area"] = (main / WORKTREE_DIR).resolve() in p.resolve().parents
        w["exists"] = p.exists()
    return out


def worktree_finished(main, w, base):
    """Decide whether a worktree can be removed without losing anything. Returns (ok, reason)."""
    p = Path(w["path"])
    if w["main"]:
        return False, "main folder"
    if not w["haam_area"]:
        return False, f"outside {WORKTREE_DIR} (created by hand; remove it yourself)"
    if w["locked"]:
        return False, "locked (an agent is using it)"
    if not w["exists"]:
        return True, "folder already gone (prune)"
    changes = git_out(p, "status", "--porcelain")
    if changes:
        return False, f"{len(changes.splitlines())} unsaved change(s)"
    unpushed = git_out(p, "rev-list", "--count", "HEAD", "--not", "--remotes") or "0"
    own = git_out(p, "rev-list", "--count", f"{base}..HEAD") or "0"
    pushed_before = bool(w["branch"]) and bool(git_out(p, "config", "--get", f"branch.{w['branch']}.merge"))
    if pushed_before:
        code, out, _ = run(["git", "ls-remote", "--heads", "origin", w["branch"]], cwd=main)
        if code != 0:
            return False, "couldn't reach origin to check the branch"
        if out:
            return False, f"branch {w['branch']} still on origin (PR open?)"
        if unpushed == "0":
            return True, f"branch {w['branch']} is gone from origin (PR merged or closed)"
        code, prs, _ = run(["gh", "pr", "list", "--head", w["branch"], "--state", "all",
                            "--json", "state,headRefOid"], cwd=main)
        try:
            done = any(pr["state"] in ("MERGED", "CLOSED") and pr["headRefOid"] == w.get("head")
                       for pr in json.loads(prs or "[]")) if code == 0 else False
        except ValueError:
            done = False
        if done:
            return True, f"PR for {w['branch']} is merged or closed"
        return False, f"branch gone from origin but {unpushed} commit(s) aren't on GitHub; check before removing"
    if unpushed != "0":
        return False, f"{unpushed} commit(s) not pushed"
    idx = Path(git_out(p, "rev-parse", "--absolute-git-dir") or p) / "index"
    idle = (time.time() - (idx.stat().st_mtime if idx.exists() else 0)) / 3600
    if own == "0" and idle >= WORKTREE_IDLE_HOURS:
        return True, f"nothing of its own and unused for {int(idle)}h"
    return False, "in use or recently created"


def cmd_worktree(args):
    root = find_repo_root(Path.cwd())
    top, main, linked = git_paths(root)
    act = args.action

    if act == "status":
        info = {"in_worktree": linked, "path": str(top), "main_folder": str(main),
                "branch": git_out(top, "branch", "--show-current") or "(detached)",
                "worktrees": len([w for w in list_worktrees(root) if not w["main"]]),
                "worktreeinclude": (main / WORKTREE_INCLUDE).exists()}
        if args.json:
            print(json.dumps(info, indent=2))
            return
        if linked:
            print(f"{OK} This chat has its own worktree: {top}")
        else:
            print(f"{WARN} This is the main folder ({top}).")
            print("   Agent chats that change code should each get their own worktree: run /work,")
            print("   or `python3 tools/haam/haam.py worktree new` and open the folder it prints.")
        print(f"   Branch: {info['branch']} · other worktrees: {info['worktrees']}")
        return

    if act == "new":
        name = args.name or f"agent-{os.urandom(2).hex()}"
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,60}", name):
            sys.exit("Use letters, numbers, dots, dashes or underscores for the name.")
        dest = main / WORKTREE_DIR / name
        if dest.exists():
            sys.exit(f"{dest} already exists. Open it, or pick another name.")
        run(["git", "fetch", "--quiet", "origin"], cwd=main)
        base = args.base or default_base(main)
        code, _, err = run(["git", "worktree", "add", "--quiet", "--detach", str(dest), base], cwd=main)
        if code != 0:
            sys.exit(f"Couldn't create the worktree: {err}")
        copied, skipped = copy_includes(main, dest)
        res = {"path": str(dest), "base": base, "copied": copied, "skipped": skipped}
        if args.json:
            print(json.dumps(res, indent=2))
            return
        print(f"{OK} New worktree: {dest}  (from {base})")
        if copied:
            print(f"{OK} Copied from the main folder: {', '.join(copied)}")
        for s_ in skipped:
            print(f"{WARN} Not copied: {s_}")
        print("Next: open that folder in a new window, start your agent there and run /work"
              " (Codex: $work). Dependencies: run `make setup` there once.")
        return

    if act == "prep":
        copied, skipped = copy_includes(main, top)
        hooks_on = secret_hook_on(top)
        if args.json:
            print(json.dumps({"in_worktree": linked, "copied": copied, "skipped": skipped,
                              "secret_hook_on": hooks_on}, indent=2))
            return
        if not hooks_on:
            print(f"{WARN} The git secret hook is off for this repository: run `make hooks` (once per clone).")
        if not linked:
            print(f"{INFO} This is the main folder; nothing to copy.")
        elif not include_patterns(main):
            print(f"{WARN} No {WORKTREE_INCLUDE} in the main folder, so no local files (like .env) were copied.")
        else:
            print(f"{OK} Local files copied: {', '.join(copied) if copied else 'none needed'}")
        for s_ in skipped:
            print(f"{WARN} Not copied: {s_}")
        return

    base = default_base(main)
    trees = list_worktrees(root)
    if act == "list":
        if args.json:
            print(json.dumps(trees, indent=2))
            return
        for w in trees:
            label = "main folder" if w["main"] else (w["branch"] or "(detached)")
            changes = git_out(Path(w["path"]), "status", "--porcelain") if w["exists"] else ""
            extra = f" · {len(changes.splitlines())} unsaved change(s)" if changes else ""
            extra += " · locked" if w["locked"] else ""
            print(f"  {w['path']}  [{label}]{extra}")
        return

    if act == "clean":
        run(["git", "fetch", "--quiet", "origin"], cwd=main)
        rep = Report()
        rep.section("Worktrees")
        remove = []
        for w in trees:
            if w["main"]:
                continue
            ok, why = worktree_finished(main, w, base)
            rep.add("ok" if ok else "info", f"{'remove' if ok else 'keep'}: {w['path']}", why)
            if ok:
                remove.append(w)
        if not remove:
            rep.add("ok", "Nothing to clean")
        elif not args.apply:
            rep.action(WHO_AGENT, f"Remove {len(remove)} finished worktree(s)",
                       "python3 tools/haam/haam.py worktree clean --apply")
        else:
            for w in remove:
                if Path(w["path"]).exists():
                    code, _, err = run(["git", "worktree", "remove", w["path"]], cwd=main)
                    rep.add("ok" if code == 0 else "warn", f"removed {w['path']}" if code == 0 else
                            f"couldn't remove {w['path']}", err[:160])
            run(["git", "worktree", "prune"], cwd=main)
        rep.print(args.json)
        return


# ----------------------------------------------------------------------------- invite

def cmd_invite(args):
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    rep = Report()
    rep.section(f"Invite {args.github}")
    if gh_ready(rep, cfg):
        repo = cfg["github_repo"]
        code, _, _ = run(["gh", "api", f"repos/{repo}/collaborators/{args.github}"])
        if code == 0:
            rep.add("ok", f"{args.github} already has access to {repo}")
        elif args.apply:
            c2, _, e2 = run(["gh", "api", "-X", "PUT", f"repos/{repo}/collaborators/{args.github}",
                             "-f", "permission=push"])
            rep.add("ok" if c2 == 0 else "fail",
                    f"GitHub invitation sent (write access, not admin)" if c2 == 0 else "GitHub invite failed", e2[:200])
        else:
            rep.add("warn", f"{args.github} has no access", "will invite with write (not admin) access")

    if cfg.get("tracker") == "github" and cfg.get("github_project_number") and have("gh"):
        try:
            board = GHProject(cfg)
            proj = board.load()
            if args.apply:
                code, uid, err = run(["gh", "api", f"users/{args.github}", "--jq", ".node_id"])
                if code != 0 or not uid:
                    raise RuntimeError(f"GitHub user {args.github} not found")
                gql("mutation($p:ID!,$u:ID!){ updateProjectV2Collaborators(input:{projectId:$p,"
                    " collaborators:[{userId:$u, role:WRITER}]}){ collaborators(first:1){ totalCount } } }",
                    {"p": proj["id"], "u": uid})
                rep.add("ok", f"{args.github} can edit the board", proj["url"])
            else:
                rep.add("warn", f"Board #{proj['number']}: will give {args.github} write access")
        except RuntimeError as e:
            rep.add("warn", "Board access not granted automatically", str(e)[:160])
            rep.action(WHO_BROWSER, f"Share the board with {args.github} (board → ⋯ → Settings → Manage access)")

    if args.linear_email and cfg.get("tracker") == "github":
        rep.add("info", "Tracker is GitHub Projects: no Linear invite needed")
    elif args.linear_email:
        key = linear_key(rep)
        if key:
            lin = Linear(key)
            try:
                team = lin.q('query($k:String!){ teams(filter:{key:{eq:$k}}) { nodes { id } } }',
                             {"k": cfg["team_key"]})["teams"]["nodes"]
                if not lin.has_mutation("organizationInviteCreate"):
                    raise RuntimeError("invite API not available")
                fields = lin.input_fields("OrganizationInviteCreateInput")
                inp = {"email": args.linear_email}
                if "teamIds" in fields and team:
                    inp["teamIds"] = [team[0]["id"]]
                if args.apply:
                    lin.q('mutation($i:OrganizationInviteCreateInput!){ organizationInviteCreate(input:$i){ success } }',
                          {"i": inp})
                    rep.add("ok", f"Linear invitation sent to {args.linear_email}",
                            "added to the team" if "teamIds" in inp else "add them to the team after they accept")
                else:
                    rep.add("warn", f"Linear: will invite {args.linear_email}")
            except RuntimeError as e:
                rep.add("warn", "Linear invite not sent automatically", str(e)[:160])
                rep.action(WHO_BROWSER, f"Invite {args.linear_email} in Linear → Settings → Members, "
                           f"then add them to team {cfg['team_key']}")

    rep.section("Send the new developer")
    rep.add("info", "Repository link and docs/ONBOARDING.md")
    rep.add("info", "Test credentials for local .env, via a password manager or one-time link (never chat/email)")
    rep.add("info", "Their first message to their agent: \"Run /haam-onboard\" (Codex: $haam-onboard)")
    if not args.apply:
        rep.add("info", "Plan only. Re-run with --apply to send invitations")
    rep.print(args.json)


# ----------------------------------------------------------------------------- dev

HOOK_MARK = "HAAM secret hook"
CHAINED_HOOK = f"""#!/usr/bin/env bash
# {HOOK_MARK}: runs the shared secret scan (.githooks/pre-commit) when this branch has it.
# Installed by `haam.py hooks --apply` instead of core.hooksPath, so this repository's other hooks keep working.
top=$(git rev-parse --show-toplevel)
if [ -x "$top/.githooks/pre-commit" ]; then "$top/.githooks/pre-commit" || exit $?; fi
"""
CHAIN_LINE = '[ -x "$(git rev-parse --show-toplevel)/.githooks/pre-commit" ] && { "$(git rev-parse --show-toplevel)/.githooks/pre-commit" || exit $?; }'


def git_hooks_dir(root):
    common = git_out(root, "rev-parse", "--git-common-dir") or ".git"
    return (Path(root) / common).resolve() / "hooks"


def own_git_hooks(root):
    """This repository's own hooks in .git/hooks (not git's samples, not ours). core.hooksPath would switch them off."""
    d = git_hooks_dir(root)
    if not d.is_dir():
        return []
    return sorted(f.name for f in d.iterdir() if f.is_file() and not f.name.endswith(".sample")
                  and HOOK_MARK not in f.read_text(errors="ignore"))


def secret_hook_on(root):
    if git_out(root, "config", "core.hooksPath") == ".githooks":
        return True
    pc = git_hooks_dir(root) / "pre-commit"
    return pc.is_file() and os.access(pc, os.X_OK) and ".githooks/pre-commit" in pc.read_text(errors="ignore")


def setup_secret_hook(root, apply, rep):
    """Turn on the commit secret scan without switching off the repository's own git hooks: core.hooksPath when
    .git/hooks holds nothing of its own, otherwise a small pre-commit in .git/hooks that calls .githooks/pre-commit."""
    hp = git_out(root, "config", "core.hooksPath")
    mine = own_git_hooks(root)
    if hp and hp != ".githooks":
        rep.add("ok" if secret_hook_on(root) else "warn", f"Git hooks are managed elsewhere (core.hooksPath = {hp})",
                f"add the secret scan to that hook manager's pre-commit: {CHAIN_LINE}")
        return
    if hp == ".githooks" and not mine:
        rep.add("ok", "Secret-scan commit hook on")
        return
    if hp == ".githooks":
        rep.add("warn", "core.hooksPath = .githooks is switching off this repository's own hooks: " + ", ".join(mine),
                "will chain the secret scan instead, so they run again" if not apply else "")
        if apply:
            run(["git", "config", "--unset", "core.hooksPath"], cwd=root)
    pc = git_hooks_dir(root) / "pre-commit"
    if pc.is_file() and HOOK_MARK not in pc.read_text(errors="ignore"):
        if ".githooks/pre-commit" in pc.read_text(errors="ignore"):
            rep.add("ok", "Secret-scan commit hook on (called from your own pre-commit)")
        else:
            rep.add("warn", "You have your own .git/hooks/pre-commit, so the secret scan isn't on",
                    f"add this line to it (it's yours, so the kit doesn't edit it): {CHAIN_LINE}")
        return
    if not apply:
        if not secret_hook_on(root):
            rep.add("warn", "Secret-scan commit hook off",
                    "will turn on" + (" (chained: your own hooks keep working)" if mine else " (git config core.hooksPath .githooks)"))
        return
    if mine or hp == ".githooks":
        pc.parent.mkdir(parents=True, exist_ok=True)
        pc.write_text(CHAINED_HOOK)
        pc.chmod(0o755)
        rep.add("ok", "Secret-scan commit hook turned on", "chained from .git/hooks/pre-commit; your own hooks keep working")
    else:
        c2, _, e2 = run(["git", "config", "core.hooksPath", ".githooks"], cwd=root)
        rep.add("ok" if c2 == 0 else "fail", "Secret-scan commit hook turned on" if c2 == 0 else "Couldn't set the hook", e2[:160])
    for f in list((root / ".githooks").glob("*")) + list((root / "scripts").glob("*.sh")) + \
            list((root / ".claude/hooks").glob("*.sh")):
        f.chmod(f.stat().st_mode | 0o111)


def cmd_hooks(args):
    root = find_repo_root(Path.cwd())
    rep = Report()
    rep.section("Git hooks on this machine")
    setup_secret_hook(root, args.apply, rep)
    if not args.apply:
        rep.add("info", "Plan only. Re-run with --apply to make changes")
    rep.print(args.json)


def cmd_dev(args):
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    rep = Report()
    rep.section("Tools on this machine")
    for b, why, how in [
        ("git", "version control", "https://git-scm.com"),
        ("gh", "pull requests and checks", "https://cli.github.com, then `gh auth login`"),
        ("make", "project commands", "macOS: xcode-select --install · Linux: build-essential · Windows: use WSL"),
        ("gitleaks", "secret scan before every commit (required)", "macOS: brew install gitleaks · others: github.com/gitleaks/gitleaks/releases"),
    ]:
        if have(b):
            rep.add("ok", b, why)
        else:
            rep.add("fail", f"{b} missing", why)
            rep.action(WHO_TERMINAL, f"Install {b}", how)
    if have("gh"):
        code, _, _ = run(["gh", "auth", "status"])
        rep.add("ok" if code == 0 else "fail", "gh logged in" if code == 0 else "gh not logged in")
        if code != 0:
            rep.action(WHO_TERMINAL, "Log in to GitHub", "gh auth login")
    found = [n for n, bins in (("Claude Code", ["claude"]), ("Cursor", ["cursor", "cursor-agent"]),
                               ("Codex", ["codex"]), ("Grok", ["grok"]), ("Gemini CLI", ["gemini"]))
             if any(have(x) for x in bins)]
    rep.add("info", "Agent tools found: " + (", ".join(found) if found else "none on PATH (IDE apps may still be installed)"))

    rep.section("This copy of the repository")
    if (root / ".githooks/pre-commit").exists():
        setup_secret_hook(root, args.apply, rep)

    env, example = root / ".env", root / ".env.example"
    if env.exists():
        rep.add("ok", ".env exists", "contents not read")
    elif example.exists():
        if args.apply:
            shutil.copy2(example, env)
            rep.add("ok", ".env created from .env.example", "fill in TEST values")
        else:
            rep.add("warn", ".env missing", "will copy from .env.example")
        rep.action(WHO_TERMINAL, "Put the TEST credentials from the product owner into .env "
                   "(agents must not read or write this file)")
    else:
        rep.add("info", "No .env.example in this project")

    for rel in SKILL_LINKS:
        p = root / rel
        rep.add("ok" if p.exists() else "warn", f"{rel} available" if p.exists() else f"{rel} missing",
                "" if p.exists() else "ask the admin to run `haam.py agents --apply` (or links weren't checked out: "
                "on Windows enable git symlinks)")

    if args.run_checks:
        rep.section("Project checks")
        for target in ("setup", "check"):
            c2, out, e2 = run(["make", target], cwd=root)
            rep.add("ok" if c2 == 0 else "fail", f"make {target}", (e2 or out)[-200:] if c2 else "")
            if c2 != 0:
                rep.action(WHO_AGENT, f"Investigate why `make {target}` fails and explain it to the developer")
                break

    rep.section("Accounts and connections")
    if cfg.get("tracker") == "github":
        rep.add("info", f"GitHub access to {cfg.get('github_repo') or '(repo)'} and its project board: "
                        "invitations come from the project admin (`haam.py invite`)")
        if have("gh"):
            _, so, se = run(["gh", "auth", "status"])
            status_text = (so + se).lower()
            if "project" in status_text:
                rep.add("ok", "gh login can use GitHub Projects")
            else:
                rep.add("warn", "gh login may lack the 'project' scope")
                rep.action(WHO_TERMINAL, "Let your GitHub login use Projects", "gh auth refresh -s project")
        rep.action(WHO_AGENT, "Verify the board works: python3 tools/haam/haam.py issue list --status Ready")
    else:
        rep.add("info", f"GitHub access to {cfg.get('github_repo') or '(repo)'} and Linear team {cfg.get('team_key')}: "
                        "invitations come from the project admin (`haam.py invite`)")
        rep.action(WHO_TERMINAL, "Connect your agent tool to Linear (one-time sign-in)",
                   "see docs/setup/AGENTS-SETUP.md for your tool")
        rep.action(WHO_AGENT, "Verify Linear works: list the Ready issues in team " + cfg.get("team_key", ""))
    rep.action(WHO_AGENT, "Walk the developer through docs/ONBOARDING.md §7–9 and suggest a first issue from the Agent queue")
    if not args.apply:
        rep.add("info", "Plan only. Re-run with --apply to make the local changes")
    rep.print(args.json)


# ----------------------------------------------------------------------------- doctor

def cmd_doctor(args):
    root = find_repo_root(Path.cwd())
    cfg = load_config(root)
    rep = Report()
    admin = args.role == "admin"

    rep.section("HAAM files")
    lock = load_lock(root)
    rep.add("ok" if lock.get("kit_version") else "warn", f"Kit version: {lock.get('kit_version') or 'not recorded'}",
            "" if lock.get("kit_version") else f"no {LOCK_NAME}: run `update` from the kit to start tracking versions")
    if getattr(args, "check_updates", False):
        latest = latest_release()
        if latest and lock.get("kit_version") and version_tuple(latest) > version_tuple(lock["kit_version"]):
            rep.add("warn", f"Update available: {latest}", f"{KIT_URL}/releases")
            rep.action(WHO_AGENT, f"Upgrade HAAM to {latest}", "run the /haam-update skill")
        elif latest:
            rep.add("ok", f"Up to date with the latest release ({latest})")
    for rel, what in [("AGENTS.md", "rules for every agent"), ("CLAUDE.md", "Claude pointer"),
                      ("docs/process/LIFECYCLE.md", "methodology"), ("docs/process/GATES.md", "gates"),
                      (".github/workflows/review.yml", "AI review"), (".github/workflows/security.yml", "secret scan"),
                      (".github/workflows/gates.yml", "UAT gate"), (".githooks/pre-commit", "commit hook"),
                      (CONFIG_NAME, "project config"), (LOCK_NAME, "installed kit version")]:
        rep.add("ok" if (root / rel).exists() else "fail", rel, what)
    if not (root / "AGENTS.md").exists():
        rep.action(WHO_AGENT, "HAAM isn't installed here. Install it from the kit",
                   "python3 <kit>/tools/haam/haam.py install --target .")
        rep.print(args.json)
        return
    skills = list((root / ".agents/skills").glob("*/SKILL.md"))
    rep.add("ok" if len(skills) >= 13 else "warn", f"{len(skills)} skills in .agents/skills")
    if (root / ".haam/incoming").exists() and any((root / ".haam/incoming").rglob("*")):
        rep.add("warn", "Unmerged kit files in .haam/incoming")
        rep.action(WHO_AGENT, "Merge the files in .haam/incoming, then delete that folder")

    rep.section("Project configuration")
    rep.add("ok", f"tracker: {cfg.get('tracker')}" + (" (GitHub Projects)" if cfg.get("tracker") == "github" else " (Linear)"))
    for k in ("product_name", "github_repo", "product_owner_github"):
        rep.add("ok" if cfg.get(k) else "fail", f"{k}: {cfg.get(k) or '(not set)'}")
    rep.add("ok" if cfg["team_key"] != PLACEHOLDER_KEY else "warn", f"team_key: {cfg['team_key']}",
            "still the placeholder" if cfg["team_key"] == PLACEHOLDER_KEY else "")
    if cfg["_applied"].get("team_key") != cfg["team_key"]:
        rep.add("fail", "Team key not applied to the files yet")
        rep.action(WHO_AGENT, "Apply the config", "python3 tools/haam/haam.py config")
    if any(not cfg.get(k) for k in ("product_name", "github_repo", "product_owner_github")):
        rep.action(WHO_AGENT, "Ask the human for the missing values and save them",
                   "python3 tools/haam/haam.py config --product ... --team-key ... --github-repo ... --owner ...")
    todos = todo_count(root)
    rep.add("ok" if not todos else "warn", f"{len(todos)} TODO(setup) placeholders left",
            ", ".join(todos[:6]) + (" …" if len(todos) > 6 else ""))
    if todos:
        rep.action(WHO_AGENT, "Fill the TODO(setup) placeholders from the codebase (Makefile commands, workflow "
                   "runtime steps, ARCHITECTURE.md) and ask the human for product facts (PRODUCT.md)",
                   "grep -rn 'TODO(setup)' AGENTS.md Makefile docs .github")

    rep.section("This machine")
    for b in ("git", "gh", "make", "gitleaks"):
        rep.add("ok" if have(b) else "fail", b)
    hook_on = secret_hook_on(root)
    rep.add("ok" if hook_on else "warn", "commit secret hook " + ("on" if hook_on else "off"))
    if git_out(root, "config", "core.hooksPath") == ".githooks" and own_git_hooks(root):
        rep.add("warn", "core.hooksPath = .githooks is switching off this repository's own hooks: "
                + ", ".join(own_git_hooks(root)), "python3 tools/haam/haam.py hooks --apply chains the scan instead")
    for rel in SKILL_LINKS:
        rep.add("ok" if (root / rel).exists() else "warn", rel)

    hidden = ignored_paths(root, sorted((load_lock(root).get("files") or {}).keys()))
    rep.add("ok" if not hidden else "fail", "Kit files committed (not hidden by .gitignore)",
            "" if not hidden else "hidden: " + ", ".join(sorted(hidden)[:6]))
    if hidden:
        rep.action(WHO_AGENT, "Re-include the hidden kit files: re-run the kit's update (it adds .gitignore negations), "
                   "then commit them", "python3 <kit>/tools/haam/haam.py update --target . --apply")

    rep.section("Parallel chats")
    _, main_dir, linked = git_paths(root)
    rep.add("info", "This chat has its own worktree" if linked else "This is the main folder",
            "" if linked else "agent chats that change code: start them with /work")
    rep.add("ok" if (main_dir / WORKTREE_INCLUDE).exists() else "warn", WORKTREE_INCLUDE,
            "lists local files (like .env) to copy into each new worktree")
    ignored = run(["git", "check-ignore", "-q", f"{WORKTREE_DIR}/x"], cwd=main_dir)[0] == 0
    rep.add("ok" if ignored else "warn", f"{WORKTREE_DIR}/ is git-ignored")
    if not ignored:
        rep.action(WHO_AGENT, f"Add `{WORKTREE_DIR}/` to .gitignore")
    others = [w for w in list_worktrees(root) if not w["main"]]
    if others:
        rep.add("info", f"{len(others)} other worktree(s)", "python3 tools/haam/haam.py worktree list")

    if admin and have("gh") and cfg.get("github_repo") and run(["gh", "auth", "status"])[0] == 0:
        repo = cfg["github_repo"]
        rep.section(f"GitHub ({repo})")
        code, out, _ = run(["gh", "label", "list", "-R", repo, "--json", "name", "-L", "200"])
        have_labels = {l["name"] for l in json.loads(out)} if code == 0 and out else set()
        miss = [n for n, _, _ in GITHUB_LABELS if n not in have_labels]
        rep.add("ok" if not miss else "warn", "Labels", "missing: " + ", ".join(miss) if miss else "")
        code, rs, _ = gh_api("GET", f"repos/{repo}/rulesets")
        ok_rs = code == 0 and isinstance(rs, list) and any(r.get("name") == "HAAM main protection" for r in rs)
        rep.add("ok" if ok_rs else "warn", "Branch ruleset with required checks")
        code, _, _ = gh_api("GET", f"repos/{repo}/environments/production")
        rep.add("ok" if code == 0 else "warn", "Production environment")
        code, out, _ = run(["gh", "secret", "list", "-R", repo, "--json", "name"])
        has_key = code == 0 and ("ANTHROPIC_API_KEY" in out or "CLAUDE_CODE_OAUTH_TOKEN" in out)
        rep.add("ok" if has_key else "warn", "Reviewer key (ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN)")
        if miss or not ok_rs or not has_key:
            rep.action(WHO_AGENT, "Show the GitHub plan, get the human's OK, then apply",
                       "python3 tools/haam/haam.py github  →  python3 tools/haam/haam.py github --apply")
    elif admin:
        rep.section("GitHub")
        rep.add("warn", "Not checked", "needs gh logged in and github_repo set")

    if admin and cfg.get("tracker") == "github":
        rep.section("Tracker: GitHub Projects")
        if not cfg.get("github_project_number"):
            rep.add("fail", "No board configured")
            rep.action(WHO_AGENT, "Create and configure the board (show the plan, then apply on the human's OK)",
                       "python3 tools/haam/haam.py github-project  →  --apply")
        elif have("gh") and run(["gh", "auth", "status"])[0] == 0:
            try:
                board = GHProject(cfg)
                proj = board.load()
                st = [o["name"] for o in (board.field("Status") or {}).get("options") or []]
                rep.add("ok", f"Board #{proj['number']}", proj["url"])
                rep.add("ok" if st == [n for n, _, _ in GH_STATUSES] else "warn", "Status field has the 12 HAAM statuses")
                rep.add("ok" if board.field("Priority") else "warn", "Priority field")
            except RuntimeError as e:
                rep.add("warn", "Couldn't read the board", str(e)[:160])
            code, out, _ = run(["gh", "secret", "list", "-R", cfg["github_repo"], "--json", "name"])
            rep.add("ok" if code == 0 and PROJECT_TOKEN_SECRET in out else "warn",
                    f"{PROJECT_TOKEN_SECRET} secret (moves cards on PR open/merge)")
    elif admin:
        rep.section("Linear")
        if os.environ.get("LINEAR_API_KEY"):
            rep.add("info", "Run `haam.py linear` to compare the team setup")
        else:
            rep.add("info", "Not checked from here (needs your Linear API key)")
            rep.action(WHO_TERMINAL, "Check/apply the Linear setup yourself (asks for your key securely)",
                       "python3 tools/haam/haam.py linear  →  then with --apply")
    rep.print(args.json)


# ----------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(prog="haam", description="HAAM setup tool " + VERSION)
    ap.add_argument("--version", action="version", version=VERSION)
    sub = ap.add_subparsers(dest="command", required=True)

    def common(p):
        p.add_argument("--json", action="store_true", help="machine-readable output for agents")
        return p

    p = common(sub.add_parser("install", help="copy the kit into a repository"))
    p.add_argument("--target", required=True)
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_install)

    p = common(sub.add_parser("update", help="upgrade a project to this kit version"))
    p.add_argument("--target", required=True)
    p.add_argument("--apply", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="same as leaving out --apply")
    p.set_defaults(func=cmd_update)

    p = common(sub.add_parser("version", help="show kit versions"))
    p.add_argument("--check", action="store_true", help="also look up the latest release (needs internet)")
    p.set_defaults(func=cmd_version)

    p = common(sub.add_parser("config", help="create/update haam.config.json"))
    p.add_argument("--product")
    p.add_argument("--team-key")
    p.add_argument("--linear-team")
    p.add_argument("--github-repo")
    p.add_argument("--owner", help="product owner's GitHub username")
    p.add_argument("--backup-approvers", help="comma-separated GitHub usernames")
    p.add_argument("--production-url")
    p.add_argument("--agents", help="comma-separated: claude,cursor,codex,grok,gemini")
    p.add_argument("--tracker", help="github (GitHub Projects) or linear")
    p.add_argument("--project-number", help="existing GitHub Projects board number to use")
    p.add_argument("--project-owner", help="GitHub user/org that owns the board (default: repo owner)")
    p.add_argument("--deploy", help="github (deploy.yml on merge, default) or manual (you deploy by hand)")
    p.add_argument("--flow", help="test-first (default: owner tests before the PR) or checks-first")
    p.add_argument("--max-open-prs", type=int, help="agents hold new work at this many open PRs (default 10)")
    p.add_argument("--max-in-uat", type=int, help="...or at this many changes waiting for you to test (default 10)")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_config)

    for name, fn, h in (("agents", cmd_agents, "wire up agent tools"),
                        ("github", cmd_github, "configure GitHub gates"),
                        ("linear", cmd_linear, "configure Linear")):
        p = common(sub.add_parser(name, help=h))
        p.add_argument("--apply", action="store_true")
        if name == "github":
            p.add_argument("--reset", action="store_true", help="replace the HAAM ruleset with HAAM's defaults "
                           "instead of adding only what's missing")
        p.set_defaults(func=fn)

    p = common(sub.add_parser("github-project", help="set up the GitHub Projects board (tracker: github)"))
    p.add_argument("--apply", action="store_true")
    p.add_argument("--force-status", action="store_true", help="replace Status options even if the board has items")
    p.set_defaults(func=cmd_github_project)

    p = common(sub.add_parser("issue", help="work with issues on the GitHub Projects board (for agents)"))
    p.add_argument("action", choices=["list", "create", "view", "add", "claim", "status", "priority", "label",
                                      "comment", "close", "link", "unlink", "children", "edit"])
    p.add_argument("number", nargs="?", help="issue number (#123 or 123)")
    p.add_argument("value", nargs="?", help="new status or priority")
    p.add_argument("--title")
    p.add_argument("--body")
    p.add_argument("--body-file")
    p.add_argument("--stream", choices=["idea", "feature", "bug"], default="idea")
    p.add_argument("--priority", choices=[n for n, _, _ in GH_PRIORITIES])
    p.add_argument("--status", action="append", help="list: filter by status (repeatable); create: initial status")
    p.add_argument("--label", action="append", help="list: must have label; create: extra label (repeatable)")
    p.add_argument("--no-label", action="append", help="list: must not have label (repeatable)")
    p.add_argument("--unassigned", action="store_true")
    p.add_argument("--epic", action="store_true", help="create: make the new issue an epic (label 'epic')")
    p.add_argument("--parent", help="create/link: the epic this issue belongs to; list: only that epic's issues")
    p.add_argument("--no-parent", action="store_true", help="list: only issues that aren't in an epic")
    p.add_argument("--open-only", action="store_true")
    p.add_argument("--add", action="append", help="label: add (repeatable)")
    p.add_argument("--remove", action="append", help="label: remove (repeatable)")
    p.add_argument("--tool", help="claim: agent tool, e.g. 'Claude Code'")
    p.add_argument("--machine", help="claim: which computer, e.g. 'desktop'")
    p.add_argument("--branch", help="claim: branch name")
    p.add_argument("--force", action="store_true", help="claim: allow a non-Ready issue (bugs); status: move an issue "
                   "another chat has claimed (only when the human asked)")
    p.add_argument("--human", action="store_true", help="a human ran the human-only skill for this change")
    p.set_defaults(func=cmd_issue)

    p = sub.add_parser("sync-pr", help=argparse.SUPPRESS)
    p.add_argument("--pr", required=True, type=int)
    p.add_argument("--event", required=True, choices=["opened", "merged"])
    p.set_defaults(func=cmd_sync_pr)

    p = common(sub.add_parser("checkout-pr", help="put an issue's change on this machine to test it (detached)"))
    p.add_argument("issue", nargs="?", help="issue number (#12) or Linear ID (APP-12)")
    p.add_argument("--back", action="store_true", help="return to the main branch after testing")
    p.add_argument("--branch", help="test this branch (no PR yet, and it isn't named after the issue)")
    p.set_defaults(func=cmd_checkout_pr)

    p = common(sub.add_parser("publish", help="test-first: after the owner's pass, push the tested commit and open the PR"))
    p.add_argument("issue", help="issue number (#12) or Linear ID (APP-12)")
    p.add_argument("--human", action="store_true", help="the human said 'pass' in this session")
    p.add_argument("--also", help="batch: the other issues in the same branch, comma-separated")
    p.add_argument("--title", help="PR title after the IDs (default: the issue's title)")
    p.add_argument("--label", action="append", help="extra PR label, e.g. human-review (Linear: when the issue has it)")
    p.set_defaults(func=cmd_publish)

    p = common(sub.add_parser("test-failed", help="the owner's test failed: withdraw any earlier pass of that commit"))
    p.add_argument("issue", help="issue number (#12) or Linear ID (APP-12)")
    p.add_argument("--human", action="store_true", help="the human said it failed in this session")
    p.set_defaults(func=cmd_test_failed)

    p = common(sub.add_parser("ship", help="after UAT passed and the human said ship: merge, deploy, close"))
    p.add_argument("issue", help="issue number (#12) or Linear ID (APP-12)")
    p.add_argument("--human", action="store_true", help="the human said 'ship' in this session")
    p.add_argument("--wait", type=float, default=1.5, help="minutes to wait before handing back (exit 2: run again)")
    p.add_argument("--merged-only", action="store_true", help="/release: never merge, only finish an already-merged PR")
    p.add_argument("--workflow", default="deploy.yml", help="the deploy workflow file")
    p.add_argument("--live", action="store_true", help="the human confirmed it's live (manual deploys)")
    p.add_argument("--no-deploy", action="store_true", help=argparse.SUPPRESS)
    p.set_defaults(func=cmd_ship)

    p = common(sub.add_parser("hooks", help="turn on the commit secret scan without switching off your own git hooks"))
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_hooks)

    p = common(sub.add_parser("capacity", help="should agents start new work? open PRs and UAT queue vs limits"))
    p.add_argument("--in-uat", type=int, help="Linear: how many issues are in UAT (counted with the Linear connection)")
    p.add_argument("--list", action="store_true", help="list the PRs and issues it counted")
    p.set_defaults(func=cmd_capacity)

    p = common(sub.add_parser("ci-usage", help="where the GitHub Actions minutes went"))
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--max-runs", type=int, default=500)
    p.add_argument("--repo", help="owner/name (default: github_repo from haam.config.json)")
    p.set_defaults(func=cmd_ci_usage)

    p = common(sub.add_parser("ci-settings", help="where CI and the AI reviews run (repository variables)"))
    p.add_argument("--runner", help="github (default) or a self-hosted runner label, e.g. self-hosted")
    p.add_argument("--review", help="github (default) or local (haam.py review on this computer)")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_ci_settings)

    p = common(sub.add_parser("review", help="run the AI reviews locally in fresh sessions and post the statuses"))
    p.add_argument("issue", nargs="?", help="issue number (#12) or Linear ID")
    p.add_argument("--pr", type=int, help="the PR number instead of the issue")
    p.add_argument("--only", choices=["ai-review", "security-review"])
    p.add_argument("--timeout", type=float, default=15, help="minutes per review")
    p.set_defaults(func=cmd_review)

    p = common(sub.add_parser("worktree", help="one worktree per agent chat (parallel work on one machine)"))
    p.add_argument("action", choices=["status", "new", "prep", "list", "clean"])
    p.add_argument("name", nargs="?", help="new: worktree name (default: agent-xxxx)")
    p.add_argument("--base", help="new: start from this ref (default: origin's default branch)")
    p.add_argument("--apply", action="store_true", help="clean: actually remove finished worktrees")
    p.set_defaults(func=cmd_worktree)

    p = common(sub.add_parser("invite", help="invite a developer"))
    p.add_argument("--github", required=True, help="their GitHub username")
    p.add_argument("--linear-email")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_invite)

    p = common(sub.add_parser("doctor", help="check setup status"))
    p.add_argument("--role", choices=["admin", "developer"], default="developer")
    p.add_argument("--check-updates", action="store_true", help="look up the latest kit release (needs internet)")
    p.set_defaults(func=cmd_doctor)

    p = common(sub.add_parser("dev", help="developer onboarding on this machine"))
    p.add_argument("--apply", action="store_true")
    p.add_argument("--run-checks", action="store_true", help="also run make setup and make check")
    p.set_defaults(func=cmd_dev)

    args = ap.parse_args()
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # quiet exit when output is piped to `head`
    args.func(args)


if __name__ == "__main__":
    main()
