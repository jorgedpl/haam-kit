"""Tests for the HAAM setup tool (template/tools/haam/haam.py).

Run:  python3 -m unittest discover -s tests -v
Uses only the standard library. GitHub and Linear are replaced by local stand-ins (tests/fakes.py).
"""

import json
import sys as _sys
_sys.dont_write_bytecode = True  # keep the kit free of __pycache__
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fakes import GOOD_KEY, FakeLinear, install_fake_gh, install_fake_gh_projects  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "template"
TOOL = KIT / "tools" / "haam" / "haam.py"


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


class ToolTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="haam-test-"))
        self.proj = self.tmp / "project"
        self.proj.mkdir()
        git(self.proj, "init", "-q", "-b", "main")
        git(self.proj, "config", "user.email", "test@example.com")
        git(self.proj, "config", "user.name", "Test")
        git(self.proj, "remote", "add", "origin", "git@github.com:example-org/example-app.git")
        (self.proj / "README.md").write_text("# Example\n")
        git(self.proj, "add", "-A")
        git(self.proj, "commit", "-qm", "init")
        self.env = {**os.environ, "NO_COLOR": "1"}
        self.env.pop("LINEAR_API_KEY", None)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_tool(self, *args, tool=TOOL, cwd=None, env=None, check=True):
        p = subprocess.run([sys.executable, str(tool), *args], cwd=cwd or self.proj, env=env or self.env,
                           capture_output=True, text=True, stdin=subprocess.DEVNULL)
        if check and p.returncode != 0:
            self.fail(f"haam {' '.join(args)} failed ({p.returncode}):\n{p.stdout}\n{p.stderr}")
        return p

    def run_json(self, *args, **kw):
        return json.loads(self.run_tool(*args, "--json", **kw).stdout)

    def installed_tool(self):
        return self.proj / "tools" / "haam" / "haam.py"

    def install(self):
        return self.run_tool("install", "--target", str(self.proj))

    def lock(self):
        return json.loads((self.proj / "haam.lock.json").read_text())


class TestRepository(unittest.TestCase):
    def test_versions_match(self):
        tool_version = re.search(r'^VERSION = "([^"]+)"', TOOL.read_text(), re.M).group(1)
        self.assertEqual((ROOT / "VERSION").read_text().strip(), tool_version)
        self.assertIn(f"## [{tool_version}]", (ROOT / "CHANGELOG.md").read_text())

    def test_template_has_no_project_or_build_leftovers(self):
        for bad in ("haam.config.json", "haam.lock.json", ".haam", "__pycache__", ".env"):
            self.assertFalse(list(KIT.rglob(bad)), f"{bad} must not be in the template")

    def test_every_skill_is_valid_and_human_only_skills_are_marked(self):
        skills = sorted(KIT.glob(".agents/skills/*/SKILL.md"))
        self.assertGreaterEqual(len(skills), 14)
        human_only = {"decide", "uat-result", "override", "release", "haam-setup", "haam-onboard", "haam-update"}
        for s in skills:
            front = s.read_text().split("---")[1]
            name = re.search(r"^name: (.+)$", front, re.M).group(1).strip()
            self.assertEqual(name, s.parent.name)
            self.assertRegex(front, r"(?m)^description: .{20,}")
            if name in human_only:
                self.assertIn("disable-model-invocation: true", front, name)
                self.assertTrue((s.parent / "agents" / "openai.yaml").exists(), f"{name}: Codex policy missing")

    def test_json_configs_parse(self):
        for rel in (".mcp.json", ".cursor/mcp.json", ".gemini/settings.json", ".claude/settings.json"):
            json.loads((KIT / rel).read_text())

    def test_skill_links_point_to_shared_folder(self):
        for rel in (".claude/skills", ".grok/skills"):
            p = KIT / rel
            self.assertTrue(p.is_symlink(), rel)
            self.assertEqual(p.resolve(), (KIT / ".agents/skills").resolve())


class TestInstall(ToolTestCase):
    def test_fresh_install(self):
        out = self.install().stdout
        self.assertIn("files added", out)
        self.assertTrue((self.proj / "AGENTS.md").exists())
        self.assertTrue((self.proj / ".agents/skills/build/SKILL.md").exists())
        self.assertFalse((self.proj / "START-HERE.md").exists())
        self.assertFalse((self.proj / ".gitignore.additions").exists())
        gi = (self.proj / ".gitignore").read_text()
        self.assertIn("# --- HAAM ---", gi)
        self.assertIn("# --- /HAAM ---", gi)
        lock = self.lock()
        self.assertEqual(lock["kit_version"], re.search(r'VERSION = "([^"]+)"', TOOL.read_text()).group(1))
        self.assertIn("AGENTS.md", lock["files"])
        self.assertTrue(os.access(self.installed_tool(), os.X_OK))

    def test_dry_run_writes_nothing(self):
        before = sorted(p.name for p in self.proj.iterdir())
        self.run_tool("install", "--target", str(self.proj), "--dry-run")
        self.assertEqual(before, sorted(p.name for p in self.proj.iterdir()))

    def test_never_overwrites_and_merges_settings(self):
        (self.proj / "CLAUDE.md").write_text("# Old rules\nUse pnpm.\n")
        (self.proj / ".mcp.json").write_text(json.dumps({"mcpServers": {"sentry": {"type": "http", "url": "https://example.com/mcp"}}}))
        (self.proj / ".claude").mkdir()
        (self.proj / ".claude/settings.json").write_text(json.dumps({"permissions": {"allow": ["Bash(pnpm test:*)"]}}))
        out = self.install().stdout
        self.assertEqual((self.proj / "CLAUDE.md").read_text(), "# Old rules\nUse pnpm.\n")
        self.assertTrue((self.proj / ".haam/incoming/CLAUDE.md").exists())
        self.assertIn("Kept your existing CLAUDE.md", out)
        mcp = json.loads((self.proj / ".mcp.json").read_text())["mcpServers"]
        self.assertEqual(set(mcp), {"sentry", "linear"})
        settings = json.loads((self.proj / ".claude/settings.json").read_text())
        self.assertIn("Bash(pnpm test:*)", settings["permissions"]["allow"])
        self.assertIn("Bash(gh pr merge:*)", settings["permissions"]["deny"])
        self.assertIn("PreToolUse", settings["hooks"])

    def test_reinstall_is_idempotent(self):
        self.install()
        self.run_tool("config", "--product", "Acme", "--team-key", "ACM", "--github-repo", "example-org/example-app",
                      "--owner", "octocat", tool=self.installed_tool())
        out = self.install().stdout
        self.assertIn("0 files added", out)
        self.assertNotIn("Kept your existing", out)
        self.assertNotIn("merged automatically", out)


class TestConfig(ToolTestCase):
    def test_config_applies_key_and_product_everywhere(self):
        self.install()
        self.run_tool("config", "--product", "Acme", "--team-key", "ACM", "--github-repo", "example-org/example-app",
                      "--owner", "octocat", tool=self.installed_tool())
        agents = (self.proj / "AGENTS.md").read_text()
        self.assertIn("You are working on **Acme**", agents)
        self.assertIn("`ACM-123", agents)
        self.assertIn("acm-123-short-title", agents)
        self.assertNotRegex(agents, r"\bAPP\b")
        self.assertNotIn("replace with your team key", agents)
        cfg = json.loads((self.proj / "haam.config.json").read_text())
        self.assertEqual(cfg["_applied"]["team_key"], "ACM")

    def test_rejects_bad_team_key(self):
        self.install()
        p = self.run_tool("config", "--team-key", "a b", tool=self.installed_tool(), check=False)
        self.assertNotEqual(p.returncode, 0)

    def test_detects_repo_from_remote(self):
        self.install()
        self.run_tool("config", "--product", "Acme", tool=self.installed_tool())
        cfg = json.loads((self.proj / "haam.config.json").read_text())
        self.assertEqual(cfg["github_repo"], "example-org/example-app")


class TestUpdate(ToolTestCase):
    def make_new_kit(self, version="9.9.9"):
        """A copy of the kit at a newer version, with typical changes."""
        new = self.tmp / "new-kit" / "template"
        shutil.copytree(KIT, new, symlinks=True)
        tool = new / "tools/haam/haam.py"
        tool.write_text(re.sub(r'^VERSION = "[^"]+"', f'VERSION = "{version}"', tool.read_text(), flags=re.M))
        return new

    def test_three_way_update(self):
        self.install()
        self.run_tool("config", "--product", "Acme", "--team-key", "ACM", "--github-repo", "example-org/example-app",
                      "--owner", "octocat", tool=self.installed_tool())
        new = self.make_new_kit()
        # Kit changed a file the project never touched
        (new / "docs/process/GATES.md").write_text((new / "docs/process/GATES.md").read_text() + "\nNew kit text.\n")
        # Project customised a file the kit didn't change
        prod = self.proj / "docs/product/PRODUCT.md"
        prod.write_text("# Product context\nAcme specifics.\n")
        # Both changed
        (self.proj / "AGENTS.md").write_text((self.proj / "AGENTS.md").read_text() + "\n## Project specifics\nUse pnpm.\n")
        (new / "AGENTS.md").write_text((new / "AGENTS.md").read_text() + "\n## 12. New kit section\n")
        # New file in the kit; file removed from the kit
        (new / "docs/setup/NEW-GUIDE.md").write_text("# New guide for APP\n")
        (new / "docs/templates/adr.md").unlink()

        new_tool = new / "tools/haam/haam.py"
        plan = self.run_tool("update", "--target", str(self.proj), tool=new_tool).stdout
        self.assertIn("Plan only", plan)
        self.assertNotIn("New kit text", (self.proj / "docs/process/GATES.md").read_text())

        self.run_tool("update", "--target", str(self.proj), "--apply", tool=new_tool)
        self.assertIn("New kit text", (self.proj / "docs/process/GATES.md").read_text())          # updated
        self.assertEqual(prod.read_text(), "# Product context\nAcme specifics.\n")                  # kept
        self.assertIn("Use pnpm", (self.proj / "AGENTS.md").read_text())                            # not overwritten
        self.assertIn("New kit section", (self.proj / ".haam/incoming/AGENTS.md").read_text())      # set aside to merge
        self.assertIn("ACM", (self.proj / ".haam/incoming/AGENTS.md").read_text())                  # rendered for project
        self.assertEqual((self.proj / "docs/setup/NEW-GUIDE.md").read_text(), "# New guide for ACM\n")  # added, renamed
        self.assertTrue((self.proj / "docs/templates/adr.md").exists())                              # never deleted
        lock = self.lock()
        self.assertEqual(lock["kit_version"], "9.9.9")
        self.assertNotIn("docs/templates/adr.md", lock["files"])

        # Running the same update again changes nothing
        again = self.run_json("update", "--target", str(self.proj), tool=new_tool)
        texts = [i["text"] for s in again["sections"] for i in s["items"]]
        self.assertIn("0 new files", texts)
        self.assertIn("0 files updated (you hadn't changed them)", texts)
        self.assertFalse([t for t in texts if t.startswith("Needs a merge")])

    def test_refuses_downgrade(self):
        self.install()
        lock = self.lock()
        lock["kit_version"] = "99.0.0"
        (self.proj / "haam.lock.json").write_text(json.dumps(lock))
        p = self.run_tool("update", "--target", str(self.proj), tool=TOOL, check=False)
        self.assertNotEqual(p.returncode, 0)


class TestAgentsDoctorDev(ToolTestCase):
    def test_agents_links_and_moves_existing_skills(self):
        (self.proj / ".claude/skills/my-skill").mkdir(parents=True)
        (self.proj / ".claude/skills/my-skill/SKILL.md").write_text("---\nname: my-skill\ndescription: x\n---\n")
        self.install()
        self.run_tool("agents", "--apply", tool=self.installed_tool())
        self.assertTrue((self.proj / ".claude/skills").is_symlink())
        self.assertTrue((self.proj / ".grok/skills").is_symlink())
        self.assertTrue((self.proj / ".agents/skills/my-skill/SKILL.md").exists())

    def test_doctor_reports_missing_config(self):
        self.install()
        report = self.run_json("doctor", tool=self.installed_tool())
        texts = [i["text"] for s in report["sections"] for i in s["items"]]
        self.assertTrue(any(t.startswith("Kit version:") for t in texts))
        self.assertTrue(any("product_name: (not set)" in t for t in texts))
        self.assertTrue(report["next_actions"])

    def test_dev_turns_on_hook_and_env(self):
        (self.proj / ".env.example").write_text("API_URL=http://localhost\n")
        self.install()
        self.run_tool("dev", "--apply", tool=self.installed_tool())
        hooks = subprocess.run(["git", "config", "core.hooksPath"], cwd=self.proj, capture_output=True, text=True).stdout.strip()
        self.assertEqual(hooks, ".githooks")
        self.assertTrue((self.proj / ".env").exists())

    @unittest.skipUnless(shutil.which("gitleaks"), "gitleaks not installed")
    def test_commit_hook_blocks_a_key(self):
        self.install()
        self.run_tool("dev", "--apply", tool=self.installed_tool())
        git(self.proj, "add", "-A")
        git(self.proj, "commit", "-qm", "install haam")
        (self.proj / "leak.py").write_text('key = "AKIA4XN7PQ2LMZ8RT6WB"\n')
        git(self.proj, "add", "leak.py")
        p = subprocess.run(["git", "commit", "-qm", "leak"], cwd=self.proj, capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        # The agent hook blocks too (exit code 2), even for a file added in the same command
        hook_in = json.dumps({"tool_input": {"command": "git add new.py && git commit -m x"}})
        (self.proj / "new.py").write_text('aws_secret_access_key = "9fQx2LmZ7pRt4WvB8nKc3HyJ6sDa1GuE5oTiXqAz"\n')
        h = subprocess.run(["bash", ".claude/hooks/block-secrets.sh"], cwd=self.proj, input=hook_in, text=True,
                           capture_output=True, env={**self.env, "CLAUDE_PROJECT_DIR": str(self.proj)})
        self.assertEqual(h.returncode, 2)


class TestGitHub(ToolTestCase):
    def setUp(self):
        super().setUp()
        bin_dir = self.tmp / "bin"
        install_fake_gh(bin_dir)
        self.log = self.tmp / "gh.log"
        self.env = {**self.env, "PATH": f"{bin_dir}{os.pathsep}{self.env['PATH']}", "FAKE_GH_LOG": str(self.log)}
        self.install()
        self.run_tool("config", "--product", "Acme", "--team-key", "ACM", "--github-repo", "example-org/example-app",
                      "--owner", "octocat", "--production-url", "https://acme.example", tool=self.installed_tool())

    def requests(self):
        if not self.log.exists():
            return []
        return [json.loads(l) for l in self.log.read_text().splitlines()]

    def writes(self):
        out = []
        for r in self.requests():
            a = r["args"]
            if a[:2] in (["label", "create"], ["variable", "set"]):
                out.append(r)
            elif a and a[0] == "api" and "-X" in a and a[a.index("-X") + 1] != "GET":
                out.append(r)
        return out

    def test_plan_changes_nothing(self):
        out = self.run_tool("github", tool=self.installed_tool()).stdout
        self.assertIn("will create", out)
        self.assertEqual(self.writes(), [])

    def test_apply_sends_expected_configuration(self):
        self.run_tool("github", "--apply", tool=self.installed_tool())
        writes = self.writes()
        ruleset = next(json.loads(r["body"]) for r in writes if r["args"][-1] == "-" and "rulesets" in " ".join(r["args"]))
        types = [r["type"] for r in ruleset["rules"]]
        self.assertEqual(types, ["deletion", "non_fast_forward", "pull_request", "required_status_checks"])
        checks = [c["context"] for c in ruleset["rules"][3]["parameters"]["required_status_checks"]]
        self.assertEqual(checks, ["ci", "secrets", "dependencies", "ai-review", "security-review", "release-gate"])
        env = next(json.loads(r["body"]) for r in writes if any(x.endswith("environments/production") for x in r["args"]))
        self.assertEqual(env["reviewers"], [{"type": "User", "id": 583231}])
        created = [r["args"][2] for r in writes if r["args"][:2] == ["label", "create"]]
        self.assertEqual(sorted(created), ["ai-review-overruled", "gate-override", "human-review"])
        # Secrets are never set by the tool
        self.assertFalse([r for r in self.requests() if r["args"][:2] == ["secret", "set"]])


class TestLinear(ToolTestCase):
    def setUp(self):
        super().setUp()
        self.fake = FakeLinear()
        self.env = {**self.env, "HAAM_LINEAR_API": self.fake.url}
        self.install()
        self.run_tool("config", "--product", "Acme", "--team-key", "ACM", "--github-repo", "example-org/example-app",
                      "--owner", "octocat", tool=self.installed_tool())

    def tearDown(self):
        self.fake.close()
        super().tearDown()

    def test_no_key_without_terminal_asks_human(self):
        out = self.run_tool("linear", tool=self.installed_tool()).stdout
        self.assertIn("[YOU, in your terminal]", out)
        self.assertEqual(self.fake.calls, [])

    def test_plan_then_apply_then_idempotent(self):
        env = {**self.env, "LINEAR_API_KEY": GOOD_KEY}
        self.run_tool("linear", tool=self.installed_tool(), env=env)
        self.assertEqual(self.fake.mutations(), [])
        out = self.run_tool("linear", "--apply", tool=self.installed_tool(), env=env).stdout
        self.assertIn("Todo renamed to Ready", out)
        self.assertIn("Triage turned on", out)
        self.assertIn("override-followup created", out)
        names = {s["name"] for s in self.fake.state["team"]["states"]["nodes"]}
        for n in ("Triage", "Discovery", "Decision", "Backlog", "Ready", "In Progress", "In Review", "UAT",
                  "Deploying", "Done", "Parked", "Canceled"):
            self.assertIn(n, names)
        self.assertTrue(all(c["auth"] == GOOD_KEY for c in self.fake.calls))
        before = len(self.fake.mutations())
        self.run_tool("linear", "--apply", tool=self.installed_tool(), env=env)
        self.assertEqual(len(self.fake.mutations()), before)

    def test_bad_key_fails_cleanly(self):
        env = {**self.env, "LINEAR_API_KEY": "wrong"}
        out = self.run_tool("linear", tool=self.installed_tool(), env=env).stdout
        self.assertIn("Authentication required", out)

    def test_linear_api_override_is_local_only(self):
        code = ("import runpy,sys; sys.argv=['haam']; "
                "g=runpy.run_path(sys.argv[0] if False else %r, run_name='not_main'); print(g['LINEAR_API'])" % str(TOOL))
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                             env={**self.env, "HAAM_LINEAR_API": "https://evil.example/graphql"}).stdout.strip()
        self.assertEqual(out, "https://api.linear.app/graphql")

class TestGitHubProjects(ToolTestCase):
    def setUp(self):
        super().setUp()
        bin_dir = self.tmp / "bin"
        install_fake_gh_projects(bin_dir)
        self.state = self.tmp / "gh-state.json"
        self.env = {**self.env, "PATH": f"{bin_dir}{os.pathsep}{self.env['PATH']}", "FAKE_GH_STATE": str(self.state)}
        self.install()
        self.run_tool("config", "--product", "Acme", "--tracker", "github", "--team-key", "ACM",
                      "--github-repo", "example-org/example-app", "--owner", "octocat", tool=self.installed_tool())

    def gh_state(self):
        return json.loads(self.state.read_text()) if self.state.exists() else {}

    def tool(self, *args, **kw):
        return self.run_tool(*args, tool=self.installed_tool(), **kw)

    def setup_board(self):
        self.tool("github-project", "--apply")

    def test_plan_changes_nothing(self):
        out = self.tool("github-project").stdout
        self.assertIn("will create", out)
        self.assertEqual(self.gh_state().get("projects", []), [])

    def test_apply_creates_board_statuses_priority_labels(self):
        out = self.tool("github-project", "--apply").stdout
        self.assertIn("created and linked", out)
        st = self.gh_state()
        self.assertEqual(len(st["projects"]), 1)
        fields = {f["name"]: [o["name"] for o in f["options"]] for f in st["projects"][0]["fields"]}
        self.assertEqual(fields["Status"], ["Triage", "Discovery", "Decision", "Backlog", "Ready", "In Progress",
                                            "In Review", "UAT", "Deploying", "Done", "Parked", "Canceled"])
        self.assertEqual(fields["Priority"], ["Urgent", "High", "Medium", "Low"])
        for lab in ("stream:idea", "stream:feature", "stream:bug", "agent-ready", "human-only", "override-followup"):
            self.assertIn(lab, st["labels"])
        cfg = json.loads((self.proj / "haam.config.json").read_text())
        self.assertEqual(cfg["github_project_number"], 1)
        # Second run finds the board and changes nothing
        again = self.tool("github-project", "--apply").stdout
        self.assertIn("Status has the 12 HAAM statuses", again)
        self.assertEqual(len(self.gh_state()["projects"]), 1)

    def test_issue_lifecycle_and_guards(self):
        self.setup_board()
        r = json.loads(self.tool("issue", "create", "--stream", "idea", "--title", "Bulk invite", "--json").stdout)
        self.assertEqual(r["status"], "Triage")
        n = r["number"]
        # Can't claim something that isn't Ready
        p = self.tool("issue", "claim", str(n), check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("not Ready", p.stderr)
        # Human-only moves need --human
        self.tool("issue", "status", str(n), "Decision")
        p = self.tool("issue", "status", str(n), "Backlog", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.tool("issue", "status", str(n), "Backlog", "--human")
        p = self.tool("issue", "label", str(n), "--add", "agent-ready", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.tool("issue", "label", str(n), "--add", "agent-ready", "--add", "stream:feature", "--remove", "stream:idea", "--human")
        self.tool("issue", "status", str(n), "Ready")
        self.tool("issue", "priority", str(n), "High")
        queue = json.loads(self.tool("issue", "list", "--status", "Ready", "--unassigned", "--label", "agent-ready", "--json").stdout)
        self.assertEqual([i["number"] for i in queue["items"]], [n])
        # Claim: assigns, moves, comments; a second claim is refused
        self.tool("issue", "claim", str(n), "--tool", "Claude Code", "--machine", "laptop")
        view = json.loads(self.tool("issue", "view", str(n), "--json").stdout)["issue"]
        self.assertEqual(view["status"], "In Progress")
        self.assertEqual(view["assignees"], ["tester"])
        self.assertEqual(view["priority"], "High")
        self.assertIn("stream:feature", view["labels"])
        self.assertTrue(any("Claimed by @tester via Claude Code on laptop" in c["body"] for c in self.gh_state()["comments"]))
        p = self.tool("issue", "claim", str(n), check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("already claimed", p.stderr)
        # Close only with --human
        self.assertNotEqual(self.tool("issue", "close", str(n), check=False).returncode, 0)
        self.tool("issue", "close", str(n), "--human")
        self.assertEqual(self.gh_state()["issues"][str(n)]["state"], "CLOSED")

    def test_feature_starts_in_backlog_and_bug_priority(self):
        self.setup_board()
        f = json.loads(self.tool("issue", "create", "--stream", "feature", "--title", "Slice 1", "--json").stdout)
        b = json.loads(self.tool("issue", "create", "--stream", "bug", "--title", "Crash", "--priority", "Urgent", "--json").stdout)
        self.assertEqual(f["status"], "Backlog")
        bug = json.loads(self.tool("issue", "view", str(b["number"]), "--json").stdout)["issue"]
        self.assertEqual((bug["status"], bug["priority"]), ("Triage", "Urgent"))

    def test_pr_sync_moves_linked_issues(self):
        self.setup_board()
        n = json.loads(self.tool("issue", "create", "--stream", "feature", "--title", "X", "--status", "In Progress", "--json").stdout)["number"]
        st = self.gh_state()
        st["prs"] = {"5": {"title": f"#{n}: Do X", "body": f"Refs #{n}", "headRefName": f"{n}-do-x", "isDraft": False},
                     "6": {"title": "Draft", "body": f"Refs #{n}", "headRefName": "x", "isDraft": True}}
        self.state.write_text(json.dumps(st))
        self.tool("sync-pr", "--pr", "6", "--event", "opened")
        self.assertEqual(json.loads(self.tool("issue", "view", str(n), "--json").stdout)["issue"]["status"], "In Progress")
        self.tool("sync-pr", "--pr", "5", "--event", "opened")
        self.assertEqual(json.loads(self.tool("issue", "view", str(n), "--json").stdout)["issue"]["status"], "In Review")
        self.tool("issue", "status", str(n), "UAT")
        self.tool("sync-pr", "--pr", "5", "--event", "opened")  # reopen must not move it back
        self.assertEqual(json.loads(self.tool("issue", "view", str(n), "--json").stdout)["issue"]["status"], "UAT")
        self.tool("sync-pr", "--pr", "5", "--event", "merged")
        self.assertEqual(json.loads(self.tool("issue", "view", str(n), "--json").stdout)["issue"]["status"], "Deploying")

    def test_issue_command_refuses_on_linear_projects(self):
        self.tool("config", "--tracker", "linear")
        p = self.tool("issue", "list", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("Linear", p.stdout + p.stderr)


class TestLinkedIssues(unittest.TestCase):
    def test_parsing(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("haam_mod", TOOL)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        f = mod.linked_issue_numbers
        self.assertEqual(f({"title": "#12: Add x", "body": "", "headRefName": "feature"}), [12])
        self.assertEqual(f({"title": "Add x", "body": "Refs #7\nalso fixes #9", "headRefName": "x"}), [7, 9])
        self.assertEqual(f({"title": "Add x", "body": "", "headRefName": "33-add-x"}), [33])
        self.assertEqual(f({"title": "Bump #2 deps", "body": "see issue #4", "headRefName": "dependabot/x"}), [])

class TestWorktrees(ToolTestCase):
    def setUp(self):
        super().setUp()
        self.origin = self.tmp / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.origin)], check=True)
        git(self.proj, "remote", "set-url", "origin", str(self.origin))
        self.install()
        git(self.proj, "add", "-A")
        git(self.proj, "commit", "-qm", "adopt HAAM")
        git(self.proj, "push", "-q", "-u", "origin", "main")
        (self.proj / ".env").write_text("APP_MODE=local\n")

    def wt(self, *args, cwd=None, check=True):
        return self.run_tool("worktree", *args, tool=self.installed_tool(), cwd=cwd, check=check)

    def test_new_copies_local_files_and_status_knows_where_it_is(self):
        res = json.loads(self.wt("new", "w1", "--json").stdout)
        w1 = Path(res["path"])
        self.assertEqual(w1, (self.proj / ".claude/worktrees/w1").resolve())
        self.assertEqual(res["copied"], [".env"])
        self.assertEqual((w1 / ".env").read_text(), "APP_MODE=local\n")
        self.assertTrue((w1 / "AGENTS.md").exists())
        self.assertNotIn(".claude/worktrees", git_status(self.proj))
        self.assertTrue(json.loads(self.wt("status", "--json", cwd=w1).stdout)["in_worktree"])
        self.assertFalse(json.loads(self.wt("status", "--json").stdout)["in_worktree"])
        (w1 / ".env").unlink()
        self.assertEqual(json.loads(self.wt("prep", "--json", cwd=w1).stdout)["copied"], [".env"])
        self.assertEqual(json.loads(self.wt("prep", "--json", cwd=w1).stdout)["copied"], [])
        self.assertNotEqual(self.wt("new", "w1", check=False).returncode, 0)

    def test_tracked_files_are_never_copied(self):
        (self.proj / ".worktreeinclude").write_text("README.md\n.env\n")
        res = json.loads(self.wt("new", "w2", "--json").stdout)
        self.assertEqual(res["copied"], [".env"])
        self.assertTrue(any("README.md" in s for s in res["skipped"]))

    def test_clean_removes_only_finished_worktrees(self):
        done = Path(json.loads(self.wt("new", "done", "--json").stdout)["path"])
        git(done, "switch", "-q", "-c", "5-fix")
        (done / "fix.txt").write_text("fixed\n")
        git(done, "add", "fix.txt")
        git(done, "commit", "-qm", "#5: fix")
        git(done, "push", "-q", "-u", "origin", "5-fix")
        git(self.origin, "branch", "-D", "5-fix")                         # PR merged, GitHub deleted the branch
        busy = Path(json.loads(self.wt("new", "busy", "--json").stdout)["path"])
        (busy / "wip.txt").write_text("not saved\n")
        fresh = Path(json.loads(self.wt("new", "fresh", "--json").stdout)["path"])
        git(fresh, "switch", "-q", "-c", "6-start")                       # agent just started, nothing pushed
        plan = json.loads(self.wt("clean", "--json").stdout)
        items = {i["text"]: i["detail"] for s in plan["sections"] for i in s["items"]}
        self.assertIn(f"remove: {done}", items)
        self.assertIn(f"keep: {busy}", items)
        self.assertIn(f"keep: {fresh}", items)
        self.assertTrue(done.exists())                                      # plan only
        self.wt("clean", "--apply")
        self.assertFalse(done.exists())
        self.assertTrue(busy.exists() and fresh.exists())

    def test_doctor_reports_parallel_chat_setup(self):
        out = json.loads(self.run_tool("doctor", "--json", tool=self.installed_tool()).stdout)
        sec = next(s for s in out["sections"] if s["title"] == "Parallel chats")
        status = {i["text"]: i["status"] for i in sec["items"]}
        self.assertEqual(status[".worktreeinclude"], "ok")
        self.assertEqual(status[".claude/worktrees/ is git-ignored"], "ok")


def git_status(cwd):
    return subprocess.run(["git", "status", "--porcelain"], cwd=cwd, capture_output=True, text=True).stdout


if __name__ == "__main__":
    unittest.main()
