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
import signal
import subprocess
import sys
import tempfile
import time
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


GATE_HARNESS = r"""
const scenario = JSON.parse(process.argv[process.argv.length - 1]);
const calls = { statuses: [], outputs: {}, warnings: [], labels: [] };
const pr = Object.assign({ number: 7, title: '#12: Bump deps', head: { ref: '12-bump', sha: 'abc' }, base: { ref: 'main' },
  draft: false, auto_merge: null, node_id: 'PR_1', labels: [] }, scenario.pr);
const issue = (n) => scenario.issues[n] === undefined ? null : Object.assign({ state: 'open', labels: [] },
  Array.isArray(scenario.issues[n]) ? { labels: scenario.issues[n] } : scenario.issues[n]);
const github = {
  paginate: async (fn) => fn === 'files' ? scenario.files : fn === 'pulls' ? [pr] : fn === 'commits' ? (scenario.commits || []) : [],
  rest: {
    pulls: { get: async () => ({ data: pr }), listFiles: 'files', list: 'pulls', listCommits: 'commits' },
    issues: { get: async ({ issue_number }) => {
                const i = issue(issue_number);
                if (!i) throw new Error('Not Found');
                return { data: Object.assign({}, i, { labels: i.labels.map(n => ({ name: n })) }) };
              },
              listComments: 'comments', removeLabel: async () => {}, createComment: async () => {},
              addLabels: async (x) => calls.labels.push(...x.labels) },
    repos: { getContent: async () => ({ data: { content: Buffer.from(JSON.stringify(Object.assign({ tracker: scenario.tracker },
                 scenario.protected ? { protected_paths: scenario.protected } : {},
                 scenario.uat ? { uat: scenario.uat } : {}))).toString('base64') } }),
             createCommitStatus: async (x) => calls.statuses.push(x), listCommitStatusesForRef: 'statuses' },
  },
};
const context = { repo: { owner: 'o', repo: 'r' }, eventName: scenario.event || 'pull_request',
  payload: scenario.event === 'issues' ? { action: 'unlabeled', issue: { number: 12 } }
                                       : { action: 'labeled', pull_request: { number: 7 } } };
process.env.REVIEW_MODE = scenario.review || '';
process.env.CI_MODE = scenario.ci || '';
const core = { info: () => {}, notice: () => {}, warning: (m) => calls.warnings.push(m),
               setOutput: (k, v) => { calls.outputs[k] = v; } };
(async () => {
  await (async function () { BODY })();
  console.log(JSON.stringify(calls));
})();
"""


class TestRepository(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "needs node")
    def test_gate_no_uat_lane(self):
        """Run gates.yml's script against fake GitHub data: the lane needs the owner's uat:skip on every issue."""
        gates = (KIT / ".github/workflows/gates.yml").read_text()
        script = re.search(r"script: \|\n(.*?)\n\s*- name: ", gates, re.S).group(1)
        body = "\n".join(l[12:] for l in script.splitlines())
        code = GATE_HARNESS.replace("BODY", body)

        def gate(**sc):
            sc.setdefault("files", [{"filename": "src/app.py"}])
            sc.setdefault("tracker", "github")
            sc.setdefault("issues", {})
            sc.setdefault("pr", {})
            sc["pr"]["labels"] = [{"name": n} for n in sc["pr"].get("labels", [])]
            p = subprocess.run(["node", "-e", code, json.dumps(sc)], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            calls = json.loads(p.stdout)
            return calls["statuses"][-1]["state"], calls["statuses"][-1]["description"], calls

        st, desc, calls = gate(pr={"labels": ["uat:skip"]}, issues={12: ["uat:skip"]})
        self.assertEqual(st, "success")
        self.assertEqual(calls["outputs"], {"enable": "7", "disable": ""})           # auto-merge turned on
        st, desc, _ = gate(pr={"labels": ["uat:skip"]}, issues={12: []})          # the owner didn't mark the issue
        self.assertEqual(st, "failure")
        self.assertIn("marked uat:skip", desc)
        st, desc, _ = gate(pr={"title": "#12 #13: Batch", "labels": ["uat:skip"]}, issues={12: ["uat:skip"], 13: []})
        self.assertEqual(st, "failure")                                             # every issue in a batch
        st, desc, _ = gate(pr={"title": "#7: x", "head": {"ref": "x", "sha": "a"}, "labels": ["uat:skip"]},
                           issues={7: {"labels": ["uat:skip"], "pull_request": {}}})
        self.assertEqual(st, "failure")                                             # its own label isn't the owner's
        st, desc, _ = gate(pr={"labels": ["uat:skip"]}, issues={12: {"labels": ["uat:skip"], "state": "closed"}})
        self.assertEqual(st, "failure")                                             # a closed issue doesn't count
        st, desc, calls = gate(pr={"labels": ["uat:skip", "human-review"], "auto_merge": {"x": 1}},
                               issues={12: ["uat:skip"]})
        self.assertEqual(st, "failure")                                             # never for protected areas
        self.assertEqual(calls["outputs"]["disable"], "7")                          # ...and auto-merge goes off
        st, desc, calls = gate(pr={"labels": ["uat:skip"]}, tracker="linear")
        self.assertEqual(st, "success")
        self.assertEqual(calls["outputs"]["enable"], "")                            # Linear: the owner ships it
        st, desc, _ = gate(pr={"labels": []}, issues={12: ["uat:skip"]})
        self.assertEqual(st, "failure")                                             # the PR must carry it too
        st, desc, calls = gate(pr={"labels": ["uat:skip"], "draft": True}, issues={12: ["uat:skip"]})
        self.assertEqual(calls["outputs"]["enable"], "")                            # drafts never auto-merge
        st, desc, calls = gate(pr={"labels": ["uat:skip"]}, issues={12: ["uat:skip"]}, review="local")
        self.assertEqual(st, "success")
        self.assertEqual(calls["outputs"]["enable"], "")                            # local reviews: the owner ships
        # Protected areas come from the changed files, whatever the labels say
        st, desc, calls = gate(pr={"labels": ["uat:skip"]}, issues={12: ["uat:skip"]},
                               files=[{"filename": "src/app.py"}, {"filename": ".github/workflows/deploy.yml"}])
        self.assertEqual(st, "failure")
        self.assertIn("protected areas", desc)
        self.assertEqual(calls["labels"], ["human-review"])                         # labelled for a human review
        st, desc, calls = gate(pr={"labels": ["uat:skip"]}, issues={12: ["uat:skip"]}, protected=["src/auth/**"],
                               files=[{"filename": "src/auth/login.py"}])
        self.assertEqual(st, "failure")                                             # the project's own areas too
        st, desc, calls = gate(pr={"labels": ["uat:skip"]}, issues={12: ["uat:skip"]}, protected=["src/auth/**"],
                               files=[{"filename": "src/login.py", "previous_filename": "src/auth/login.py"}])
        self.assertEqual(st, "failure")                                             # moved out of a protected folder
        st, desc, calls = gate(pr={"labels": ["uat:skip"]}, issues={12: ["uat:skip"]}, protected=["src/auth/**"],
                               files=[{"filename": "src/billing.py"}])
        self.assertEqual(st, "success")
        self.assertEqual(calls["labels"], [])
        # A spike never merges, whatever its labels, even docs-only
        for labels, files in ((["uat-passed"], [{"filename": "src/app.py"}]), (["gate-override"], [{"filename": "src/a.py"}]),
                              ([], [{"filename": "docs/notes.md"}])):
            st, desc, calls = gate(pr={"title": "#12: Prototype", "head": {"ref": "spike/12-try", "sha": "s"},
                                       "labels": labels}, issues={12: ["uat:skip"]}, files=files)
            self.assertEqual(st, "failure", labels)
            self.assertIn("Spike branch", desc)
        st, desc, _ = gate(pr={"title": "#12: P", "head": {"ref": "SPIKE/12-try", "sha": "s"}, "labels": ["uat-passed"]})
        self.assertEqual(st, "failure")                                             # any case
        st, desc, _ = gate(pr={"labels": ["uat-passed"]}, files=[{"filename": "prototypes/voice/app.py"}])
        self.assertEqual(st, "failure")                                             # prototypes/ never merges
        self.assertIn("prototypes/", desc)
        st, desc, calls = gate(pr={"labels": ["uat:skip"]}, issues={12: ["uat:skip"]},
                               commits=[{"commit": {"message": "#12: spike: try voice notes"}}])
        self.assertEqual(st, "failure")                                             # kept prototype code: no lane
        self.assertIn("prototype", desc)
        self.assertEqual(calls["outputs"]["enable"], "")
        # The uat setting: always (no lane at all) and bugs-skip (a bug counts as marked)
        st, desc, calls = gate(pr={"labels": ["uat:skip"]}, issues={12: ["uat:skip"]}, uat="always")
        self.assertEqual(st, "failure")
        self.assertIn("every change", desc)
        st, desc, calls = gate(pr={"labels": ["uat:skip"]}, issues={12: ["stream:bug"]}, uat="bugs-skip")
        self.assertEqual(st, "failure")                 # a stream label isn't the owner's mark (anyone sets it)
        st, desc, calls = gate(pr={"labels": ["uat:skip"]}, issues={12: ["stream:bug", "uat:skip"]}, uat="bugs-skip")
        self.assertEqual(st, "success")
        # Auto-merge only when CI and both AI reviews really run on GitHub
        for review, ci in (("protected-only", ""), ("off", ""), ("", "off"), ("", "local")):
            st, desc, calls = gate(pr={"labels": ["uat:skip"]}, issues={12: ["uat:skip"]}, review=review, ci=ci)
            self.assertEqual((st, calls["outputs"]["enable"]), ("success", ""), (review, ci))
        # The owner takes uat:skip off the issue: its open PR is re-checked and loses auto-merge
        st, desc, calls = gate(event="issues", pr={"labels": ["uat:skip"], "auto_merge": {"x": 1}}, issues={12: []})
        self.assertEqual(st, "failure")
        self.assertEqual(calls["outputs"]["disable"], "7")

    def test_protected_path_patterns(self):
        """haam.py's patterns match exactly what the gate's do (the gate decides; the tool tells agents early)."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("haam_mod", TOOL)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        pats = mod.DEFAULT_CONFIG["protected_paths"] + ["src/**/auth/*.py", "db/migrations/**", "./payments/",
                                                         "billing", "/infra/"]
        files = [".github/workflows/ci.yml", "AGENTS.md", "docs/AGENTS.md", "src/app/auth/login.py", "src/auth/login.py",
                 "src/app/auth/deep/x.py", "db/migrations/0001.sql", "Makefile", "src/Makefile", "tools/haam/haam.py",
                 ".gitleaks.toml", "README.md", "payments/charge.py", "billing/invoice.py", "billing.md", "infra/a/b.tf"]
        py = mod.protected_matches(pats, files)
        self.assertEqual(py, [".github/workflows/ci.yml", "AGENTS.md", "src/app/auth/login.py", "src/auth/login.py",
                              "db/migrations/0001.sql", "Makefile", "tools/haam/haam.py", ".gitleaks.toml",
                              "payments/charge.py", "billing/invoice.py", "infra/a/b.tf"])
        gates = (KIT / ".github/workflows/gates.yml").read_text()
        js_defaults = re.search(r"let protectedPaths = (\[.*?\]);", gates, re.S).group(1)
        self.assertEqual(json.loads(js_defaults.replace("'", '"')), mod.DEFAULT_CONFIG["protected_paths"])
        if shutil.which("node"):
            fn = re.search(r"(const globRe = .*?\n\s*\};)", gates, re.S).group(1)
            js = fn + "\nconst pats = " + json.dumps(pats) + ", files = " + json.dumps(files) + ";\n" \
                "console.log(JSON.stringify(files.filter(f => pats.map(globRe).some(r => r.test(f)))));"
            p = subprocess.run(["node", "-e", js], capture_output=True, text=True)
            self.assertEqual(json.loads(p.stdout), py, p.stderr)

    def test_override_comment_satisfies_the_gate(self):
        """The comment /override posts must be one gates.yml accepts, and one that starts a gate run."""
        gates = (KIT / ".github/workflows/gates.yml").read_text()
        js = re.search(r"comments\.find\(c =>\s*/(.+?)/\.test\(c\.body\)\)", gates).group(1)
        accepts = re.compile(js.replace("\\/", "/"))
        triggers = re.findall(r"startsWith\(github\.event\.comment\.body, '([^']+)'\)", gates)
        skill = (KIT / ".agents/skills/override/SKILL.md").read_text()
        body = re.search(r'gh pr comment <pr> --body "([^"]+)"', skill).group(1)
        posted = body.replace("<reason>", "Hotfix for login outage").replace("<user>", "octocat")
        self.assertTrue(accepts.search(posted), posted)
        self.assertTrue(any(posted.lower().startswith(t.lower()) for t in triggers), (triggers, posted))
        self.assertTrue(accepts.search("OVERRIDE (Level 1, skip UAT) by octocat: old wording"))
        self.assertFalse(accepts.search("Override is not justified here: wait for UAT"))
        self.assertFalse(accepts.search("Override the default timeout: see config.py"))
        self.assertTrue(accepts.search("OVERRIDE: urgent fix"))
        self.assertTrue(accepts.search("EMERGENCY BYPASS: CI broken"))
        self.assertFalse(accepts.search("Please don't OVERRIDE: this"))     # must start the comment
        self.assertFalse(accepts.search("OVERRIDE:"))                       # needs a reason

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
        human_only = {"triage", "decide", "uat-result", "override", "release", "haam-setup", "haam-onboard", "haam-update",
                      "haam-settings", "test", "epic"}
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

    def test_kit_files_hidden_by_project_gitignore_are_reincluded(self):
        (self.proj / ".gitignore").write_text("**/build/\n")
        (self.proj / "scripts").mkdir()
        (self.proj / "scripts/lab-x.sh").write_text("echo lab\n")
        self.install()
        gi = (self.proj / ".gitignore").read_text()
        self.assertIn("!/.agents/skills/build/", gi)
        p = subprocess.run(["git", "check-ignore", "-q", ".agents/skills/build/SKILL.md"], cwd=self.proj)
        self.assertEqual(p.returncode, 1)                       # no longer ignored
        self.assertFalse(os.access(self.proj / "scripts/lab-x.sh", os.X_OK))   # the project's own file untouched
        self.assertTrue(os.access(self.proj / "scripts/scan-secrets.sh", os.X_OK))
        # A second install keeps the negation, even when the project adds rules after the HAAM block
        with open(self.proj / ".gitignore", "a") as f:
            f.write("\n**/build/\n")
        self.install()
        gi = (self.proj / ".gitignore").read_text()
        self.assertTrue(gi.rstrip().endswith("# <<< HAAM re-include"))
        self.assertEqual(gi.count("!/.agents/skills/build/"), 1)
        p = subprocess.run(["git", "check-ignore", "-q", ".agents/skills/build/SKILL.md"], cwd=self.proj)
        self.assertEqual(p.returncode, 1)

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

    def test_github_tracker_never_gets_the_linear_connection(self):
        self.install()
        settings = self.proj / ".claude/settings.json"
        self.assertIn("linear", json.loads(settings.read_text()).get("enabledMcpjsonServers", []))
        self.run_tool("config", "--product", "Acme", "--tracker", "github", "--team-key", "ACM",
                      "--github-repo", "example-org/example-app", "--owner", "octocat", tool=self.installed_tool())
        self.assertNotIn("linear", json.loads(settings.read_text()).get("enabledMcpjsonServers", []))
        self.assertFalse((self.proj / ".mcp.json").exists())          # it held only the Linear connection
        self.assertFalse((self.proj / ".cursor/mcp.json").exists())
        # The project's own MCP server is kept, and updates never bring Linear back
        (self.proj / ".mcp.json").write_text(json.dumps({"mcpServers": {"db": {"command": "db-mcp"}}}))
        new = self.make_new_kit()
        new_tool = new / "tools/haam/haam.py"
        self.run_tool("update", "--target", str(self.proj), "--apply", tool=new_tool)
        self.run_tool("update", "--target", str(self.proj), "--apply", tool=new_tool)
        self.assertNotIn("linear", json.loads(settings.read_text()).get("enabledMcpjsonServers", []))
        self.assertEqual(json.loads((self.proj / ".mcp.json").read_text()), {"mcpServers": {"db": {"command": "db-mcp"}}})
        self.assertFalse((self.proj / ".cursor/mcp.json").exists())
        self.assertIn("hooks", json.loads(settings.read_text()))      # the rest of the settings still merge
        out = self.run_tool("agents", tool=new_tool).stdout
        self.assertNotIn("declares Linear", out)
        # Updates that change nothing say so
        again = self.run_json("update", "--target", str(self.proj), "--apply", tool=new_tool)
        texts = [i["text"] for sec in again["sections"] for i in sec["items"]]
        self.assertFalse([t for t in texts if "merged" in t or "Linear connection taken out" in t], texts)
        # A project's own server called "linear" stays on
        (self.proj / ".mcp.json").write_text(json.dumps({"mcpServers": {"linear": {"command": "my-linear-proxy"}}}))
        st = json.loads(settings.read_text())
        st["enabledMcpjsonServers"] = ["linear"]
        settings.write_text(json.dumps(st))
        self.run_tool("agents", "--apply", tool=new_tool)
        self.assertEqual(json.loads(settings.read_text())["enabledMcpjsonServers"], ["linear"])
        self.assertIn("linear", json.loads((self.proj / ".mcp.json").read_text())["mcpServers"])

    def test_removed_mcp_json_is_not_switched_back_on(self):
        self.install()
        self.run_tool("config", "--product", "Acme", "--tracker", "linear", "--team-key", "ACM",
                      "--github-repo", "example-org/example-app", "--owner", "octocat", tool=self.installed_tool())
        (self.proj / ".mcp.json").unlink()
        settings = self.proj / ".claude/settings.json"
        st = json.loads(settings.read_text())
        st["enabledMcpjsonServers"] = []
        settings.write_text(json.dumps(st))
        new_tool = self.make_new_kit() / "tools/haam/haam.py"
        self.run_tool("update", "--target", str(self.proj), "--apply", tool=new_tool)
        self.assertFalse((self.proj / ".mcp.json").exists())
        self.assertEqual(json.loads(settings.read_text())["enabledMcpjsonServers"], [])

    def test_switching_back_to_linear_restores_the_connection(self):
        self.install()
        tool = self.installed_tool()
        args = ["--product", "Acme", "--team-key", "ACM", "--github-repo", "example-org/example-app", "--owner", "octocat"]
        self.run_tool("config", "--tracker", "github", *args, tool=tool)
        self.assertFalse((self.proj / ".mcp.json").exists())
        self.run_tool("config", "--tracker", "linear", *args, tool=tool)
        new_tool = self.make_new_kit() / "tools/haam/haam.py"
        self.run_tool("update", "--target", str(self.proj), "--apply", tool=new_tool)
        self.assertIn("linear", json.loads((self.proj / ".mcp.json").read_text())["mcpServers"])
        self.assertTrue((self.proj / ".cursor/mcp.json").exists())
        self.assertIn("linear", json.loads((self.proj / ".claude/settings.json").read_text())["enabledMcpjsonServers"])

    def test_linear_tracker_keeps_the_linear_connection(self):
        self.install()
        self.run_tool("config", "--product", "Acme", "--tracker", "linear", "--team-key", "ACM",
                      "--github-repo", "example-org/example-app", "--owner", "octocat", tool=self.installed_tool())
        self.assertIn("linear", json.loads((self.proj / ".mcp.json").read_text())["mcpServers"])
        self.assertIn("linear", json.loads((self.proj / ".claude/settings.json").read_text())["enabledMcpjsonServers"])

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

    def test_protected_lists_changed_protected_files(self):
        self.install()
        git(self.proj, "add", "-A")
        git(self.proj, "commit", "-qm", "kit")
        tool = self.installed_tool()
        self.run_tool("config", "--protected", "src/auth", "--human", tool=tool)            # plain folder name: everything inside
        (self.proj / "src/auth").mkdir(parents=True)
        (self.proj / "src/auth/login.py").write_text("x = 1\n")
        git(self.proj, "add", "-A")
        git(self.proj, "commit", "-qm", "auth")
        git(self.proj, "switch", "-q", "-c", "12-move")
        git(self.proj, "mv", "src/auth/login.py", "src/login.py")             # moving it out still counts
        git(self.proj, "commit", "-qm", "move")
        res = json.loads(self.run_tool("protected", "--base", "main", "--json", tool=tool).stdout)
        self.assertIn("src/auth/login.py", res["protected"])
        self.assertEqual(self.run_tool("protected", "--base", "main", "--check", tool=tool, check=False).returncode, 1)
        p = self.run_tool("protected", "--base", "nosuch", "--check", tool=tool, check=False)
        self.assertNotEqual(p.returncode, 0)                                     # a failed comparison isn't "clean"
        self.assertIn("Couldn't compare", p.stderr)

    def test_settings_show_set_and_validate(self):
        self.install()
        tool = self.installed_tool()
        res = json.loads(self.run_tool("settings", "--json", tool=tool).stdout)
        keys = {r["key"]: r for r in res["settings"]}
        for k in ("flow", "uat", "grouping", "ci", "nightly", "review", "runner", "deploy", "deploy_approval",
                  "max_open_prs", "max_in_uat", "max_review_rounds", "max_pr_lines", "worktree_cleanup"):
            self.assertIn(k, keys)
            self.assertTrue(keys[k]["what"])
            for o in keys[k]["options"]:
                self.assertTrue(keys[k]["options_help"].get(o), f"{k}={o} has no explanation")
        self.assertEqual(res["required_checks"], ["ci", "secrets", "dependencies", "ai-review", "security-review",
                                                  "release-gate"])
        self.assertNotEqual(self.run_tool("settings", "--set", "ci=off", tool=tool, check=False).returncode, 0)  # owner only
        res = json.loads(self.run_tool("settings", "--set", "ci=local", "--set", "review=protected-only",
                                       "--set", "max-in-uat=4", "--human", "--json", tool=tool).stdout)
        self.assertEqual(res["required_checks"][0], "ci-local")
        self.assertEqual(res["github_variables"]["HAAM_CI"], "local")
        self.assertEqual(res["github_variables"]["HAAM_REVIEW"], "protected-only")
        cfg = json.loads((self.proj / "haam.config.json").read_text())
        self.assertEqual((cfg["ci"], cfg["max_in_uat"]), ("local", 4))
        res = json.loads(self.run_tool("settings", "--set", "ci=off", "--human", "--json", tool=tool).stdout)
        self.assertNotIn("ci", res["required_checks"])
        for bad in ("ci=sometimes", "max_in_uat=0", "nosuch=1"):
            self.assertNotEqual(self.run_tool("settings", "--set", bad, "--human", tool=tool, check=False).returncode, 0, bad)
        self.assertNotEqual(self.run_tool("settings", "--set", "grouping=release", "--set", "flow=checks-first",
                                          "--human", tool=tool, check=False).returncode, 0)
        # The older ci-settings command still works
        self.run_tool("ci-settings", "--review", "github", "--human", tool=tool)
        self.assertEqual(json.loads((self.proj / "haam.config.json").read_text())["review"], "github")

    def test_dev_keeps_the_repositorys_own_git_hooks(self):
        self.install()
        hooks = self.proj / ".git/hooks"
        (hooks / "pre-push").write_text("#!/bin/sh\necho own guard\n")
        (hooks / "pre-push").chmod(0o755)
        hooks_path = lambda: subprocess.run(["git", "config", "core.hooksPath"], cwd=self.proj, capture_output=True,
                                            text=True).stdout.strip()
        # Already switched on the old way: the tool moves to the chained hook so pre-push runs again
        git(self.proj, "config", "core.hooksPath", ".githooks")
        self.assertIn("switching off this repository's own hooks",
                      self.run_tool("doctor", tool=self.installed_tool(), check=False).stdout)
        self.run_tool("dev", "--apply", tool=self.installed_tool())
        self.assertEqual(hooks_path(), "")
        self.assertIn(".githooks/pre-commit", (hooks / "pre-commit").read_text())
        self.assertEqual((hooks / "pre-push").read_text(), "#!/bin/sh\necho own guard\n")   # untouched
        self.assertIn("commit secret hook on", self.run_tool("doctor", tool=self.installed_tool(), check=False).stdout)
        # Running it again changes nothing
        self.run_tool("hooks", "--apply", tool=self.installed_tool())
        self.assertEqual(hooks_path(), "")
        # The project's own pre-commit is never edited: the tool says what line to add
        (hooks / "pre-commit").write_text("#!/bin/sh\necho own pre-commit\n")
        out = self.run_tool("hooks", "--apply", tool=self.installed_tool()).stdout
        self.assertIn("add this line", out)
        self.assertEqual((hooks / "pre-commit").read_text(), "#!/bin/sh\necho own pre-commit\n")
        # ...and a scan that's on through core.hooksPath is never switched off on the way
        git(self.proj, "config", "core.hooksPath", ".githooks")
        self.run_tool("hooks", "--apply", tool=self.installed_tool())
        self.assertEqual(hooks_path(), ".githooks")
        # The line it suggests must not fail commits on a branch without the kit
        line = re.search(r"add this line to .*?: (t=\$\(.+?fi)", out).group(1)
        (hooks / "pre-commit").write_text("#!/bin/sh\n" + line + "\n")
        (hooks / "pre-commit").chmod(0o755)
        git(self.proj, "config", "--unset", "core.hooksPath")
        git(self.proj, "switch", "-q", "--orphan", "bare")
        (self.proj / "x.txt").write_text("x\n")
        git(self.proj, "add", "x.txt")
        git(self.proj, "commit", "-qm", "no kit here")                    # succeeds

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
        # Agents work under the owner's (admin) login: admins bypass only via a PR, and no "up to date" re-runs
        self.assertEqual(ruleset["bypass_actors"][0]["bypass_mode"], "pull_request")
        self.assertFalse(ruleset["rules"][3]["parameters"]["strict_required_status_checks_policy"])
        env = next(json.loads(r["body"]) for r in writes if any(x.endswith("environments/production") for x in r["args"]))
        self.assertEqual(env["reviewers"], [{"type": "User", "id": 583231}])
        created = [r["args"][2] for r in writes if r["args"][:2] == ["label", "create"]]
        self.assertEqual(sorted(created), ["ai-review-overruled", "epic-build", "gate-override", "human-review", "uat:skip"])
        patch = [json.loads(r["body"]) for r in writes if "PATCH" in r["args"] and r["body"] and "allow_auto_merge" in r["body"]]
        self.assertEqual(patch, [{"allow_auto_merge": True}])           # the no-UAT lane's auto-merge
        # Secrets are never set by the tool
        self.assertFalse([r for r in self.requests() if r["args"][:2] == ["secret", "set"]])

    def test_settings_apply_syncs_github(self):
        rs = self.tmp / "ruleset.json"
        rs.write_text(json.dumps({"id": 1, "name": "HAAM main protection", "target": "branch", "enforcement": "active",
                                  "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
                                  "bypass_actors": [], "rules": [{"type": "required_status_checks", "parameters": {
                                      "required_status_checks": [{"context": c} for c in
                                                                 ["ci", "secrets", "my-check", "release-gate"]]}}]}))
        self.env = {**self.env, "FAKE_GH_RULESET": str(rs)}
        self.run_tool("settings", "--set", "ci=local", "--set", "nightly=off", "--apply", "--human", tool=self.installed_tool())
        put = next(json.loads(r["body"]) for r in self.writes() if "rulesets/1" in " ".join(r["args"]))
        checks = [c["context"] for c in put["rules"][0]["parameters"]["required_status_checks"]]
        self.assertIn("my-check", checks)                                     # the project's own check stays
        self.assertIn("ci-local", checks)
        self.assertNotIn("ci", checks)
        sets = [r["args"][2:5] for r in self.requests() if r["args"][:2] == ["variable", "set"]]
        self.assertIn(["HAAM_CI", "--body", "local"], sets)
        self.assertIn(["HAAM_NIGHTLY", "--body", "off"], sets)

    def test_existing_ruleset_is_merged_not_overwritten(self):
        rs = self.tmp / "ruleset.json"
        rs.write_text(json.dumps({"id": 1, "name": "HAAM main protection", "target": "branch", "enforcement": "active",
                                  "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
                                  "bypass_actors": [{"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"}],
                                  "rules": [{"type": "deletion"},
                                            {"type": "pull_request", "parameters": {"required_approving_review_count": 2}},
                                            {"type": "required_status_checks", "parameters": {
                                                "strict_required_status_checks_policy": True,
                                                "required_status_checks": [{"context": "ci"}, {"context": "my-check"}]}}]}))
        self.env = {**self.env, "FAKE_GH_RULESET": str(rs)}
        out = self.run_tool("github", tool=self.installed_tool()).stdout
        self.assertIn("push straight to main", out)
        self.assertIn("up to date before merging", out)
        self.assertFalse([w for w in self.writes() if "rulesets" in " ".join(w["args"])])
        self.run_tool("github", "--apply", tool=self.installed_tool())
        put = next(json.loads(r["body"]) for r in self.writes() if "rulesets/1" in " ".join(r["args"]))
        rules = {r["type"]: r for r in put["rules"]}
        self.assertIn("non_fast_forward", rules)                                            # added
        self.assertEqual(rules["pull_request"]["parameters"]["required_approving_review_count"], 2)  # kept
        checks = [c["context"] for c in rules["required_status_checks"]["parameters"]["required_status_checks"]]
        self.assertIn("my-check", checks)
        self.assertIn("release-gate", checks)
        self.assertEqual(put["bypass_actors"][0]["bypass_mode"], "always")                 # the project's choice
        # --reset replaces it with the defaults
        self.log.unlink()
        self.run_tool("github", "--apply", "--reset", tool=self.installed_tool())
        put = next(json.loads(r["body"]) for r in self.writes() if "rulesets/1" in " ".join(r["args"]))
        self.assertEqual(put["bypass_actors"][0]["bypass_mode"], "pull_request")

    def test_environment_without_reviewers_when_the_plan_refuses(self):
        self.env = {**self.env, "FAKE_GH_ENV_422": "1", "FAKE_GH_PRIVATE": "1"}
        out = self.run_tool("github", "--apply", tool=self.installed_tool()).stdout
        self.assertIn("without a required approver", out)
        envs = [json.loads(r["body"]) for r in self.writes() if any(x.endswith("environments/production") for x in r["args"])]
        self.assertEqual(envs[-1]["reviewers"], [])
        policies = [r for r in self.writes() if any(x.endswith("deployment-branch-policies") for x in r["args"])]
        self.assertTrue(policies)                                   # still deploys only from main


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

    def test_assess_and_spec_claims_block_other_chats(self):
        self.setup_board()
        n = json.loads(self.tool("issue", "create", "--stream", "idea", "--title", "Bulk invite", "--json").stdout)["number"]
        # Chat A claims the assessment; chat B (same GitHub user) is refused
        r = json.loads(self.tool("issue", "claim", str(n), "--for", "assess", "--tool", "Claude Code", "--json").stdout)
        token = r["claim"]
        view = json.loads(self.tool("issue", "view", str(n), "--json").stdout)["issue"]
        self.assertEqual(view["status"], "Discovery")
        self.assertIn("claimed", view["labels"])
        p = self.tool("issue", "claim", str(n), "--for", "assess", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("already claimed", p.stderr)
        # B can't move it or release it; A can, with its claim id
        self.assertNotEqual(self.tool("issue", "status", str(n), "Decision", check=False).returncode, 0)
        p = self.tool("issue", "release", str(n), "--status", "Decision", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("another chat", p.stderr)
        self.tool("issue", "release", str(n), "--claim", token, "--status", "Decision")
        view = json.loads(self.tool("issue", "view", str(n), "--json").stdout)["issue"]
        self.assertEqual(view["status"], "Decision")
        self.assertNotIn("claimed", view["labels"])
        self.assertEqual(view["assignees"], [])
        # Spec: only from Backlog; the claim keeps the build away until it's released
        self.assertNotEqual(self.tool("issue", "claim", str(n), "--for", "spec", check=False).returncode, 0)
        self.tool("issue", "status", str(n), "Backlog", "--human")
        token = json.loads(self.tool("issue", "claim", str(n), "--for", "spec", "--json").stdout)["claim"]
        self.tool("issue", "label", str(n), "--add", "agent-ready", "--human")
        self.tool("issue", "status", str(n), "Ready", "--claim", token)
        p = self.tool("issue", "claim", str(n), check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("already claimed", p.stderr)
        self.tool("issue", "release", str(n), "--claim", token)
        self.tool("issue", "claim", str(n))                                    # now it can be built
        # A race: another chat's claim lands just before ours, so ours withdraws
        m = json.loads(self.tool("issue", "create", "--stream", "idea", "--title", "Dark mode", "--json").stdout)["number"]
        st = self.gh_state()
        st["race_claim"] = "🤖 Claimed by @tester via Cursor to assess it · claim abcdef"
        self.state.write_text(json.dumps(st))
        p = self.tool("issue", "claim", str(m), "--for", "assess", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("a moment earlier", p.stderr)
        self.assertTrue(any("withdrawn" in c["body"] for c in self.gh_state()["comments"]))

    def test_custom_board_fields(self):
        self.setup_board()
        st = self.gh_state()
        today = __import__("datetime").date.today()
        st["projects"][0]["fields"] += [
            {"id": "F_area", "name": "Area", "options": [{"id": "O_b", "name": "Billing"}, {"id": "O_w", "name": "Wallet"}]},
            {"id": "F_est", "name": "Estimate", "type": "NUMBER"},
            {"id": "F_due", "name": "Due", "type": "DATE"},
            {"id": "F_note", "name": "Customer", "type": "TEXT"},
            {"id": "F_spr", "name": "Sprint", "type": "ITERATION", "iterations": [
                {"id": "I1", "title": "Sprint 1", "startDate": str(today - __import__("datetime").timedelta(days=3)), "duration": 14},
                {"id": "I2", "title": "Sprint 2", "startDate": str(today + __import__("datetime").timedelta(days=11)), "duration": 14}]},
            {"id": "F_rev", "name": "Reviewers", "type": "REVIEWERS"}]
        self.state.write_text(json.dumps(st))
        fields = json.loads(self.tool("issue", "fields", "--json").stdout)["fields"]
        self.assertEqual([f["name"] for f in fields], ["Area", "Estimate", "Due", "Customer", "Sprint"])
        self.assertEqual(fields[0]["options"], ["Billing", "Wallet"])
        r = json.loads(self.tool("issue", "create", "--stream", "bug", "--title", "Refund rounding", "--field", "area=billing",
                                 "--field", "Estimate=3", "--field", "Due=2026-11-30", "--field", "Customer=Acme Ltd",
                                 "--field", "Sprint=@current", "--json").stdout)
        self.assertEqual(r["fields"], {"Area": "Billing", "Estimate": "3", "Due": "2026-11-30", "Customer": "Acme Ltd",
                                       "Sprint": "Sprint 1"})
        view = json.loads(self.tool("issue", "view", str(r["number"]), "--json").stdout)["issue"]
        self.assertEqual(view["fields"], {"Area": "Billing", "Estimate": 3, "Due": "2026-11-30", "Customer": "Acme Ltd",
                                          "Sprint": "Sprint 1"})
        self.assertEqual(view["status"], "Triage")
        # A wrong value is refused before anything is created
        before = len(self.gh_state()["issues"])
        for bad, msg in (("Area=Payments", "options: Billing, Wallet"), ("Estimate=lots", "takes a number"),
                         ("Due=30/11", "YYYY-MM-DD"), ("Colour=red", "no field 'Colour'"), ("Status=Done", "issue status"),
                         ("Reviewers=me", "filled in by GitHub"), ("Area", "NAME=VALUE"), ("Sprint=Sprint 9", "Sprint 1, Sprint 2")):
            p = self.tool("issue", "create", "--title", "x", "--field", bad, check=False)
            self.assertNotEqual(p.returncode, 0, bad)
            self.assertIn(msg, p.stderr, bad)
        self.assertEqual(len(self.gh_state()["issues"]), before)
        # Edit and clear; list filters by a field
        self.tool("issue", "edit", str(r["number"]), "--field", "Area=Wallet", "--field", "Customer=")
        view = json.loads(self.tool("issue", "view", str(r["number"]), "--json").stdout)["issue"]
        self.assertEqual(view["fields"].get("Area"), "Wallet")
        self.assertNotIn("Customer", view["fields"])
        other = json.loads(self.tool("issue", "create", "--title", "Other", "--json").stdout)["number"]
        listed = json.loads(self.tool("issue", "list", "--field", "Area=wallet", "--json").stdout)["items"]
        self.assertEqual([i["number"] for i in listed], [r["number"]])
        self.assertNotIn(other, [i["number"] for i in listed])

    def test_spike_claims_and_owner_mode_labels(self):
        self.setup_board()
        n = json.loads(self.tool("issue", "create", "--stream", "idea", "--title", "Voice notes", "--json").stdout)["number"]
        p = self.tool("issue", "label", str(n), "--add", "mode:prototype", check=False)
        self.assertNotEqual(p.returncode, 0)                                   # the owner's decision
        self.tool("issue", "label", str(n), "--add", "mode:prototype", "--human")
        r = json.loads(self.tool("issue", "claim", str(n), "--for", "spike", "--json").stdout)
        self.assertEqual(r["phase"], "spike")
        view = json.loads(self.tool("issue", "view", str(n), "--json").stdout)["issue"]
        self.assertEqual(view["status"], "Discovery")
        self.assertIn("claimed", view["labels"])
        self.assertTrue(any("to build a prototype" in c["body"] for c in self.gh_state()["comments"]))
        self.assertNotEqual(self.tool("issue", "claim", str(n), "--for", "assess", check=False).returncode, 0)
        self.tool("issue", "release", str(n), "--claim", r["claim"])
        self.tool("issue", "status", str(n), "Ready")
        self.assertNotEqual(self.tool("issue", "claim", str(n), "--for", "spike", check=False).returncode, 0)

    def test_epics_group_issues_and_cant_be_built(self):
        self.setup_board()
        mk = lambda *a: json.loads(self.tool("issue", "create", *a, "--json").stdout)
        a = mk("--stream", "idea", "--title", "Export to CSV")["number"]
        b = mk("--stream", "bug", "--title", "Export button missing on mobile")["number"]
        loose = mk("--stream", "idea", "--title", "Dark mode")["number"]
        # Only epics can be parents
        self.assertNotEqual(self.tool("issue", "link", str(a), "--parent", str(loose), check=False).returncode, 0)
        epic = mk("--stream", "idea", "--epic", "--title", "Reporting")["number"]
        self.assertIn("epic", self.gh_state()["issues"][str(epic)]["labels"])
        self.tool("issue", "link", str(a), "--parent", str(epic))
        self.tool("issue", "link", str(b), "--parent", str(epic))
        c = mk("--stream", "feature", "--title", "Scheduled reports", "--parent", str(epic))
        self.assertEqual(c["parent"], epic)
        kids = json.loads(self.tool("issue", "children", str(epic), "--json").stdout)
        self.assertEqual(sorted(k["number"] for k in kids["children"]), sorted([a, b, c["number"]]))
        self.assertEqual(kids["done"], 0)
        loose_items = json.loads(self.tool("issue", "list", "--no-parent", "--no-label", "epic", "--json").stdout)["items"]
        self.assertEqual([i["number"] for i in loose_items], [loose])
        self.assertEqual(json.loads(self.tool("issue", "view", str(a), "--json").stdout)["issue"]["parent"], epic)
        # Epics are never built themselves, and don't nest
        self.tool("issue", "status", str(epic), "Ready")
        p = self.tool("issue", "claim", str(epic), check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("is an epic", p.stderr)
        other = mk("--stream", "idea", "--epic", "--title", "Other")["number"]
        self.assertNotEqual(self.tool("issue", "link", str(other), "--parent", str(epic), check=False).returncode, 0)
        self.assertNotEqual(self.tool("issue", "create", "--epic", "--parent", str(epic), "--title", "Nested",
                                      check=False).returncode, 0)
        # Sub-issues added in GitHub's own UI (not on the board) still count
        st = self.gh_state()
        st["issues"][str(st["next_issue"])] = {"id": "I_web", "title": "Added in the browser", "body": "", "state": "OPEN",
                                               "url": "u", "labels": [], "assignees": [], "created": "2026-01-02T00:00:00Z",
                                               "parent": epic}
        st["next_issue"] += 1
        Path(self.env["FAKE_GH_STATE"]).write_text(json.dumps(st))
        kids = json.loads(self.tool("issue", "children", str(epic), "--json").stdout)
        self.assertEqual(len(kids["children"]), 4)
        self.assertTrue(any(k.get("not_on_board") for k in kids["children"]))
        # Rewrite and move out
        self.tool("issue", "edit", str(a), "--title", "Export reports to CSV", "--body", "Part of epic")
        self.assertEqual(self.gh_state()["issues"][str(a)]["title"], "Export reports to CSV")
        self.tool("issue", "unlink", str(b))
        self.assertIsNone(json.loads(self.tool("issue", "view", str(b), "--json").stdout)["issue"]["parent"])

    def test_ship_merges_approves_deploy_and_closes(self):
        self.setup_board()
        n = json.loads(self.tool("issue", "create", "--stream", "bug", "--title", "Export broken", "--status", "UAT",
                                 "--json").stdout)["number"]
        st = self.gh_state()
        st["prs"] = {"5": {"title": f"#{n}: Fix export", "body": f"Refs #{n}", "headRefName": f"{n}-fix-export",
                           "isDraft": False, "state": "OPEN", "labels": [], "url": "https://pr/5", "headRefOid": "t1"},
                     "6": {"title": "Unrelated", "body": f"Refs #{n}", "headRefName": "other-thing", "isDraft": False,
                           "state": "OPEN", "labels": [{"name": "uat-passed"}], "url": "https://pr/6", "headRefOid": "o1"}}
        st["checks_pending"] = 1
        self.state.write_text(json.dumps(st))
        env = {**self.env, "HAAM_POLL_SECONDS": "0"}
        # Only with --human, and only after UAT passed
        self.assertNotEqual(self.tool("ship", str(n), env=env, check=False).returncode, 0)
        p = self.tool("ship", str(n), "--human", env=env, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("hasn't passed UAT", p.stdout + p.stderr)
        st = self.gh_state()
        st["prs"]["5"]["labels"] = [{"name": "uat-passed"}]
        self.state.write_text(json.dumps(st))
        # /release never merges
        p = self.tool("ship", str(n), "--human", "--merged-only", env=env, check=False)
        self.assertEqual(p.returncode, 1)
        self.assertEqual(self.gh_state()["prs"]["5"]["state"], "OPEN")
        # The PR changed after the human tested it: refuse
        tested = self.proj / ".haam" / "tested.json"
        tested.parent.mkdir(exist_ok=True)
        tested.write_text(json.dumps({f"#{n}": "old"}))
        p = self.tool("ship", str(n), "--human", env=env, check=False)
        self.assertEqual(p.returncode, 1)
        self.assertIn("changed after the human tested it", p.stdout + p.stderr)
        tested.write_text(json.dumps({f"#{n}": "t1"}))
        # Not finished in time: exit 2 with a clear message, then a re-run finishes
        st = self.gh_state(); st["checks_pending"] = 1; self.state.write_text(json.dumps(st))
        p = self.tool("ship", str(n), "--human", "--wait", "0", env=env, check=False)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("Run the same command again", p.stdout)
        res = json.loads(self.tool("ship", str(n), "--human", "--json", env=env).stdout)
        self.assertEqual(res["state"], "live", res)
        self.assertEqual(self.gh_state()["prs"]["6"]["state"], "OPEN")   # only the issue's own PR
        st = self.gh_state()
        self.assertEqual(st["prs"]["5"]["state"], "MERGED")
        self.assertEqual(st["approved"]["state"], "approved")
        self.assertEqual(st["issues"][str(n)]["state"], "CLOSED")
        self.assertIn(f"repos/example-org/example-app/git/refs/heads/{n}-fix-export", st["deleted_refs"])
        self.assertEqual(json.loads(self.tool("issue", "view", str(n), "--json").stdout)["issue"]["status"], "Done")
        self.assertTrue(any("Released to production" in c["body"] for c in st["comments"]))
        # Running it again is harmless and doesn't post twice
        self.assertEqual(json.loads(self.tool("ship", str(n), "--human", "--json", env=env).stdout)["state"], "live")
        self.assertEqual(sum("Released to production" in c["body"] for c in self.gh_state()["comments"]), 1)

    def test_status_refuses_to_move_another_chats_claim(self):
        self.setup_board()
        n = json.loads(self.tool("issue", "create", "--stream", "bug", "--title", "Crash", "--status", "Ready",
                                 "--json").stdout)["number"]
        self.tool("issue", "claim", str(n))
        p = self.tool("issue", "status", str(n), "Ready", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("claimed", p.stderr)
        git(self.proj, "switch", "-q", "-c", f"{n}-crash")      # the chat working on it is on its branch
        self.tool("issue", "status", str(n), "In Review")
        git(self.proj, "switch", "-q", "main")
        self.tool("issue", "status", str(n), "Ready", "--force")
        # A batch: the second bug is claimed with the first one's branch
        m = json.loads(self.tool("issue", "create", "--stream", "bug", "--title", "Crash 2", "--status", "Ready",
                                 "--json").stdout)["number"]
        self.tool("issue", "claim", str(m), "--branch", f"{n}-crash")
        git(self.proj, "switch", "-q", f"{n}-crash")
        self.tool("issue", "status", str(m), "In Review")
        git(self.proj, "switch", "-q", "main")

    def test_capacity_holds_new_work(self):
        self.setup_board()
        st = self.gh_state()
        st["prs"] = {str(k): {"title": f"PR {k}", "headRefName": f"b{k}", "state": "OPEN", "labels": [], "url": "u",
                              "isDraft": False} for k in range(1, 11)}
        self.state.write_text(json.dumps(st))
        res = json.loads(self.tool("capacity", "--json").stdout)
        self.assertTrue(res["hold"])
        self.assertEqual(res["open_prs"], 10)
        self.assertEqual(len(res["counted_prs"]), 10)                      # it says which PRs it counted
        self.assertIn("PR #3: PR 3", self.tool("capacity").stdout)
        self.tool("config", "--max-open-prs", "20", "--human")
        self.assertFalse(json.loads(self.tool("capacity", "--json").stdout)["hold"])

    def test_capacity_counts_ready_prs_and_the_uat_queue_with_a_batch_window(self):
        self.setup_board()
        st = self.gh_state()
        pr = lambda k, **kw: {"title": f"PR {k}", "headRefName": f"b{k}", "state": "OPEN", "labels": [], "url": "u",
                              "isDraft": False, "files": [{"path": f"src/f{k}.py"}], **kw}
        st["prs"] = {"1": pr(1), "2": pr(2, isDraft=True),
                     "3": pr(3, files=[{"path": "docs/specs/GH-3-x.md"}, {"path": "docs/epics/GH-3.md"}]),
                     "4": pr(4, isDraft=True, files=[{"path": "README.md"}])}
        self.state.write_text(json.dumps(st))
        self.tool("config", "--max-open-prs", "2", "--max-in-uat", "2", "--human")
        res = json.loads(self.tool("capacity", "--json").stdout)
        self.assertEqual(res["open_prs"], 1)                                # only the ready code PR counts
        self.assertEqual([p["number"] for p in res["draft_prs"]], [2])
        self.assertEqual(sorted(p["number"] for p in res["docs_prs"]), [3, 4])
        self.assertFalse(res["hold"])
        for t in ("A", "B"):
            self.tool("issue", "create", "--stream", "bug", "--title", t, "--status", "UAT")
        res = json.loads(self.tool("capacity", "--json").stdout)
        self.assertTrue(res["hold"])
        self.assertIn("2 changes waiting for the owner to test", res["reasons"][0])
        # A batch window raises the UAT limit until its last day, then the normal limit is back by itself
        future = str(__import__("datetime").date.today() + __import__("datetime").timedelta(days=3))
        self.assertNotEqual(self.tool("config", "--max-in-uat", "30", "--until", future, check=False).returncode, 0)
        self.tool("config", "--max-in-uat", "30", "--until", future, "--human")
        cfg = json.loads((self.proj / "haam.config.json").read_text())
        self.assertEqual((cfg["max_in_uat"], cfg["batch_window"]), (2, {"until": future, "max_in_uat": 30}))
        res = json.loads(self.tool("capacity", "--json").stdout)
        self.assertEqual(res["max_in_uat"], 30)
        self.assertFalse(res["hold"])
        self.assertIn(f"Batch window until {future}", self.tool("capacity").stdout)
        cfg["batch_window"]["until"] = "2020-01-01"
        (self.proj / "haam.config.json").write_text(json.dumps(cfg))
        self.assertTrue(json.loads(self.tool("capacity", "--json").stdout)["hold"])
        self.assertNotEqual(self.tool("config", "--max-in-uat", "30", "--until", "2020-01-01", "--human",
                                      check=False).returncode, 0)        # not in the past
        self.tool("settings", "--set", "max_in_uat=12", "--until", future, "--human")
        self.assertEqual(json.loads(self.tool("capacity", "--json").stdout)["max_in_uat"], 12)
        self.tool("config", "--end-batch-window", "--human")
        self.assertNotIn("batch_window", json.loads((self.proj / "haam.config.json").read_text()))

    def test_settings_recommend_sizes_the_limits(self):
        r = json.loads(self.tool("settings", "--recommend", "--builders", "2", "--chats", "3", "--testing-hours", "5",
                                 "--sittings", "5", "--json").stdout)
        self.assertEqual((r["max_in_uat"], r["max_open_prs"]), (10, 12))       # 60 min a sitting / 6 min a test
        self.assertEqual(r["agents_per_week"], 60)
        self.assertTrue(any("can produce about 60" in n for n in r["notes"]))  # more than 50 testable a week
        self.assertIn("--set max_in_uat=10 --set max_open_prs=12 --human", r["command"])
        r = json.loads(self.tool("settings", "--recommend", "--testing-hours", "2", "--sittings", "1",
                                 "--chats", "1", "--json").stdout)
        self.assertEqual(r["max_in_uat"], 20)
        self.assertTrue(any("batch window" in n for n in r["notes"]))
        r = json.loads(self.tool("settings", "--recommend", "--chats", "1", "--flow", "checks-first", "--json").stdout)
        self.assertEqual((r["max_in_uat"], r["max_open_prs"]), (10, 11))       # every waiting change is a ready PR
        for bad in (("--sittings", "0"), ("--minutes-per-test", "0"), ("--testing-hours", "-3"),
                    ("--testing-hours", "nan"), ("--testing-hours", "inf"), ("--builders", "0")):
            p = self.tool("settings", "--recommend", *bad, check=False)
            self.assertNotEqual(p.returncode, 0, bad)
            self.assertIn(bad[0], p.stderr)
        self.assertNotEqual(self.tool("settings", "--recommend", "--set", "max_in_uat=9", "--human",
                                      check=False).returncode, 0)
        before = (self.proj / "haam.config.json").read_text()
        self.assertIn("max_in_uat", self.tool("settings", "--recommend").stdout)   # no --human needed: changes nothing
        self.assertEqual((self.proj / "haam.config.json").read_text(), before)

    def test_agents_cant_mark_issues_themselves(self):
        self.setup_board()
        for lab in ("uat:skip", "agent-ready"):
            p = self.tool("issue", "create", "--stream", "bug", "--title", "x", "--label", lab, check=False)
            self.assertNotEqual(p.returncode, 0, lab)
            self.assertIn("decided", p.stdout + p.stderr)

    def test_issue_create_survives_the_boards_auto_add(self):
        self.setup_board()
        st = self.gh_state()
        st["auto_add_races"] = True
        self.state.write_text(json.dumps(st))
        res = json.loads(self.tool("issue", "create", "--stream", "bug", "--title", "Raced", "--status", "Ready",
                                   "--priority", "High", "--json", env={**self.env, "HAAM_POLL_SECONDS": "0"}).stdout)
        view = json.loads(self.tool("issue", "view", str(res["number"]), "--json").stdout)["issue"]
        self.assertEqual((view["status"], view["priority"]), ("Ready", "High"))

    def test_ship_carries_a_lane_change_waiting_to_deploy(self):
        self.setup_board()
        mk = lambda t, status: json.loads(self.tool("issue", "create", "--stream", "bug", "--title", t, "--status",
                                                    status, "--json").stdout)["number"]
        lane, a = mk("Bump deps", "Deploying"), mk("Fix A", "UAT")
        st = self.gh_state()
        st["prs"] = {"5": {"title": f"#{lane}: bump", "headRefName": f"{lane}-bump", "state": "MERGED",
                           "labels": [{"name": "uat:skip"}], "url": "https://pr/5", "mergeCommit": {"oid": "merge5"}},
                     "6": {"title": f"#{a}: fix", "headRefName": f"{a}-fix", "state": "OPEN", "isDraft": False,
                           "labels": [{"name": "uat-passed"}], "url": "https://pr/6"}}
        st["runs"] = [{"databaseId": 3, "status": "waiting", "conclusion": "", "url": "https://run/3", "headSha": "merge5"}]
        self.state.write_text(json.dumps(st))
        env = {**self.env, "HAAM_POLL_SECONDS": "0"}
        res = json.loads(self.tool("ship", str(a), "--human", "--json", env=env).stdout)
        self.assertEqual(res["state"], "live", res)
        st = self.gh_state()
        self.assertEqual(st["cancelled"], ["3"])                     # the lane's waiting run: the new one includes it
        self.assertEqual(len(st["approvals"]), 1)
        self.assertEqual(st["issues"][str(lane)]["state"], "CLOSED")   # it went out in the same deploy

    def test_ship_several_with_one_deploy(self):
        self.setup_board()
        mk = lambda t: json.loads(self.tool("issue", "create", "--stream", "bug", "--title", t, "--status", "UAT",
                                            "--json").stdout)["number"]
        a, b, c = mk("Fix A"), mk("Fix B"), mk("Bump deps")
        st = self.gh_state()
        pr = lambda n, labels: {"title": f"#{n}: x", "body": f"Refs #{n}", "headRefName": f"{n}-x", "isDraft": False,
                                "state": "OPEN", "labels": [{"name": l} for l in labels], "url": f"https://pr/{n}"}
        st["prs"] = {"5": pr(a, ["uat-passed"]), "6": pr(b, ["uat-passed"]), "7": pr(c, ["uat:skip"]),
                     "8": {**pr(99, []), "title": "Untested"}}
        self.state.write_text(json.dumps(st))
        env = {**self.env, "HAAM_POLL_SECONDS": "0"}
        res = json.loads(self.tool("ship", "--all", "--human", "--json", env=env).stdout)
        self.assertEqual(res["state"], "live", res)
        self.assertEqual(sorted(res["merged"]), sorted([f"#{a}", f"#{b}", f"#{c}"]))   # passed + the no-UAT lane
        st = self.gh_state()
        self.assertEqual(st["prs"]["8"]["state"], "OPEN")                              # untested stays
        self.assertEqual(len(st["approvals"]), 1)                                      # one deploy for all three
        self.assertEqual(len(st["cancelled"]), 2)                                      # the older runs
        for n in (a, b, c):
            self.assertEqual(st["issues"][str(n)]["state"], "CLOSED")
        # A lane PR is refused by plain ship while it's labelled human-review (protected areas)
        st["prs"]["9"] = pr(77, ["uat:skip", "human-review"])
        self.state.write_text(json.dumps(st))
        p = self.tool("ship", "77", "--human", env=env, check=False)
        self.assertIn("hasn't passed UAT", p.stdout + p.stderr)

    def test_manual_deploy_and_batch_pr(self):
        self.setup_board()
        self.tool("config", "--deploy", "manual", "--human")
        mk = lambda t: json.loads(self.tool("issue", "create", "--stream", "bug", "--title", t, "--status", "UAT",
                                            "--json").stdout)["number"]
        a, b = mk("Export crash"), mk("Export button")
        st = self.gh_state()
        st["prs"] = {"5": {"title": f"#{a} #{b}: Fix export bugs (epic #9)", "body": "", "headRefName": f"{a}-export-bugs",
                           "isDraft": False, "state": "OPEN", "labels": [{"name": "uat-passed"}], "url": "https://pr/5",
                           "headRefOid": "t1"}}
        self.state.write_text(json.dumps(st))
        env = {**self.env, "HAAM_POLL_SECONDS": "0"}
        p = self.tool("ship", str(b), "--human", env=env, check=False)       # found through the batch title
        self.assertEqual(p.returncode, 3, p.stdout + p.stderr)                # waiting for the human, not "run again"
        self.assertIn("deploys by hand", p.stdout)
        self.assertEqual(self.gh_state()["prs"]["5"]["state"], "MERGED")
        self.assertEqual(self.gh_state()["issues"][str(a)]["state"], "OPEN")
        self.tool("ship", str(b), "--human", "--live", env=env)
        st = self.gh_state()
        self.assertEqual((st["issues"][str(a)]["state"], st["issues"][str(b)]["state"]), ("CLOSED", "CLOSED"))
        self.assertNotIn("approved", st)                                     # nothing to approve on manual deploys

    def test_ci_usage_adds_up_minutes(self):
        self.setup_board()
        st = self.gh_state()
        st["runs_api"] = [
            {"id": 1, "name": "Review", "event": "pull_request", "created_at": "2026-10-17T10:00:00Z", "pull_requests": [{"number": 5}]},
            {"id": 2, "name": "CI", "event": "pull_request", "created_at": "2026-10-17T11:00:00Z", "pull_requests": [{"number": 5}]},
            {"id": 3, "name": "CI", "event": "schedule", "created_at": "2026-10-18T03:00:00Z", "pull_requests": []}]
        job = lambda name, a, b, labels=("ubuntu-24.04",), concl="success": {
            "name": name, "started_at": a, "completed_at": b, "labels": list(labels), "conclusion": concl}
        st["jobs_api"] = {
            "1": [job("ai review runner", "2026-10-17T10:00:00Z", "2026-10-17T10:09:10Z"),     # 10 min (rounded up)
                  job("review scope", "2026-10-17T10:00:00Z", "2026-10-17T10:00:05Z")],        # 1
            "2": [job("ci", "2026-10-17T11:00:00Z", "2026-10-17T11:02:00Z", ("macos-15",)),       # 2 x 10
                  job("skipped", "2026-10-17T11:00:00Z", "2026-10-17T11:05:00Z", concl="skipped")],
            "3": [job("ci", "2026-10-18T03:00:00Z", "2026-10-18T03:30:00Z", ("self-hosted",))]}   # not billed
        self.state.write_text(json.dumps(st))
        res = json.loads(self.tool("ci-usage", "--json").stdout)
        self.assertEqual(res["billable_minutes"], 31)
        self.assertEqual(res["by_workflow"], {"CI": 20, "Review": 11})
        self.assertEqual(res["own_runner_minutes"], 30)
        self.assertEqual(res["pull_requests"], 1)

    def test_settings_keep_an_existing_own_runner(self):
        self.setup_board()
        st = self.gh_state()
        st["variables"] = {"HAAM_RUNNER": "my-mac"}
        self.state.write_text(json.dumps(st))
        cfg_file = self.proj / "haam.config.json"
        cfg = json.loads(cfg_file.read_text())
        cfg.pop("runner", None)
        cfg_file.write_text(json.dumps(cfg))
        self.tool("settings", "--set", "nightly=off", "--apply", "--human")
        self.assertEqual(self.gh_state()["variables"], {"HAAM_RUNNER": "my-mac", "HAAM_NIGHTLY": "off"})
        cfg = json.loads(cfg_file.read_text())
        self.assertEqual((cfg["runner"], cfg["runner_label"]), ("self-hosted", "my-mac"))

    def test_ci_settings_and_local_review(self):
        self.setup_board()
        self.tool("ci-settings", "--review", "local", "--runner", "self-hosted", "--human")             # plan only
        self.assertEqual(self.gh_state().get("variables", {}), {})
        self.tool("ci-settings", "--review", "local", "--runner", "self-hosted", "--apply", "--human")
        self.assertEqual(self.gh_state()["variables"], {"HAAM_REVIEW": "local"})     # no own runner on a public repo
        self.env = {**self.env, "FAKE_GH_PRIVATE": "1"}
        self.tool("ci-settings", "--runner", "self-hosted", "--apply", "--human")
        self.assertEqual(self.gh_state()["variables"], {"HAAM_REVIEW": "local", "HAAM_RUNNER": "self-hosted"})
        self.tool("ci-settings", "--runner", "github", "--apply", "--human")
        self.assertEqual(self.gh_state()["variables"], {"HAAM_REVIEW": "local"})
        # A fake reviewer agent: approves the code, finds nothing in security
        bin_dir = self.tmp / "bin"
        (bin_dir / "claude").write_text("#!/bin/sh\ncase \"$2\" in *'for security only'*) echo 'SECURITY_FINDINGS: 0';; "
                                        "*) printf 'Looks fine.\\nVERDICT: APPROVE\\n';; esac\n")
        (bin_dir / "claude").chmod(0o755)
        origin = self.tmp / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
        git(self.proj, "remote", "set-url", "origin", str(origin))
        git(self.proj, "add", "-A")
        git(self.proj, "commit", "-qm", "kit")
        git(self.proj, "push", "-q", "origin", "main")
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.proj, capture_output=True, text=True).stdout.strip()
        st = self.gh_state()
        st["prs"] = {"5": {"title": "#12: Fix", "body": "Refs #12", "headRefName": "12-fix", "state": "OPEN", "labels": [],
                           "url": "u", "isDraft": False, "headRefOid": head}}
        self.state.write_text(json.dumps(st))
        res = json.loads(self.tool("review", "12", "--json").stdout)
        self.assertEqual(res["results"], {"ai-review": "success", "security-review": "success"})
        final = {s["context"]: s["state"] for s in self.gh_state()["statuses"]}
        self.assertEqual(final, {"ai-review": "success", "security-review": "success"})
        self.assertFalse((self.proj / ".claude/worktrees/review-pr-5").exists())     # the clean checkout is removed
        # Protected areas are reviewed on GitHub
        st = self.gh_state(); st["prs"]["5"]["labels"] = [{"name": "human-review"}]; self.state.write_text(json.dumps(st))
        p = self.tool("review", "12", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("protected area", p.stderr)

    def test_triage_reject_closes_as_not_planned_and_needs_human(self):
        self.setup_board()
        n = json.loads(self.tool("issue", "create", "--stream", "idea", "--title", "Dark mode", "--json").stdout)["number"]
        self.assertNotEqual(self.tool("issue", "status", str(n), "Canceled", check=False).returncode, 0)
        self.assertEqual(self.gh_state()["issues"][str(n)]["state"], "OPEN")
        self.tool("issue", "status", str(n), "Canceled", "--human")
        self.assertEqual(self.gh_state()["issues"][str(n)]["state"], "CLOSED")
        m = json.loads(self.tool("issue", "create", "--stream", "idea", "--title", "Later", "--json").stdout)["number"]
        self.tool("issue", "status", str(m), "Parked", "--human")
        self.assertEqual(self.gh_state()["issues"][str(m)]["state"], "OPEN")
        self.tool("issue", "status", str(m), "Discovery")

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

    def test_pr_sync_leaves_epics_mentions_docs_and_spikes_alone(self):
        self.setup_board()
        mk = lambda *a: json.loads(self.tool("issue", "create", *a, "--json").stdout)["number"]
        epic = mk("--stream", "feature", "--epic", "--title", "Reporting", "--status", "In Progress")
        a = mk("--stream", "feature", "--title", "Slice A", "--status", "In Progress", "--parent", str(epic))
        b = mk("--stream", "feature", "--title", "Slice B", "--status", "Backlog", "--parent", str(epic))
        ctx = mk("--stream", "feature", "--title", "Related", "--status", "Ready")
        st = self.gh_state()
        code = [{"path": "src/report.py"}]
        st["prs"] = {
            "5": {"title": f"#{a}: Slice A (epic #{epic})", "body": f"Refs #{a}\nRefs #{epic}\nSee also refs #{ctx}",
                  "headRefName": f"{a}-slice-a", "isDraft": False, "files": code},
            "6": {"title": f"#{epic}: Brief", "body": f"Refs #{epic}\nRefs #{b}", "headRefName": f"docs/{epic}-epic",
                  "isDraft": False, "files": [{"path": "docs/epics/GH-1-reporting.md"}]},
            "7": {"title": f"#{b}: Prototype", "body": f"Refs #{b}", "headRefName": f"spike/{b}-try", "isDraft": False,
                  "files": code}}
        self.state.write_text(json.dumps(st))
        status = lambda n: json.loads(self.tool("issue", "view", str(n), "--json").stdout)["issue"]["status"]
        out = self.tool("sync-pr", "--pr", "5", "--event", "opened").stdout
        self.assertEqual((status(a), status(epic), status(ctx)), ("In Review", "In Progress", "Ready"))
        self.assertIn("an epic", out)
        self.tool("sync-pr", "--pr", "5", "--event", "merged")
        self.assertEqual((status(a), status(epic), status(ctx)), ("Deploying", "In Progress", "Ready"))
        for pr_ in ("6", "7"):                                              # docs-only, and a spike
            for ev in ("opened", "merged"):
                self.tool("sync-pr", "--pr", pr_, "--event", ev)
        self.assertEqual((status(epic), status(b)), ("In Progress", "Backlog"))

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
        pat = mod.branch_pattern
        self.assertTrue(pat(12).search("12-fix"))
        self.assertFalse(pat(12).search("120-other"))
        self.assertFalse(pat(12).search("spike/12-try"))
        self.assertTrue(pat("APP-12").search("app-12-fix"))
        self.assertTrue(pat("APP-12").search("jorge/app-12-fix"))
        self.assertFalse(pat("APP-12").search("spike/app-12-try"))
        self.assertFalse(pat("APP-12").search("app-120-fix"))
        self.assertEqual(mod.branch_issue("jorge/app-12-fix", "APP-1"), "APP-12")
        self.assertEqual(mod.branch_issue("12-epic-x", 13), 12)
        self.assertIsNone(mod.branch_issue("spike/12-x", 13))

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

    def test_clean_keeps_a_worktree_a_program_is_running_in(self):
        idle = Path(json.loads(self.wt("new", "idle", "--json").stdout)["path"])
        idx = Path(subprocess.run(["git", "rev-parse", "--absolute-git-dir"], cwd=idle, capture_output=True,
                                  text=True).stdout.strip()) / "index"
        old = time.time() - 3 * 86400
        os.utime(idx, (old, old))                                           # untouched for 3 days
        chat = subprocess.Popen(["sleep", "30"], cwd=idle)                  # a chat still open in it
        try:
            items = {i["text"]: i["detail"] for s in json.loads(self.wt("clean", "--json").stdout)["sections"]
                     for i in s["items"]}
            if not (Path("/proc/self/cwd").exists() or shutil.which("lsof")):
                self.skipTest("can't see working directories here")
            self.assertIn("a program is running in it", items.get(f"keep: {idle}", ""))
        finally:
            chat.kill()
            chat.wait()
        os.utime(idx, (old, old))                                           # the first clean's git status touched it
        items = {i["text"] for s in json.loads(self.wt("clean", "--json").stdout)["sections"] for i in s["items"]}
        self.assertIn(f"remove: {idle}", items)

    def test_checkout_pr_detaches_the_branch_and_comes_back(self):
        bin_dir = self.tmp / "bin"
        install_fake_gh_projects(bin_dir)
        state = self.tmp / "gh-state.json"
        env = {**self.env, "PATH": f"{bin_dir}{os.pathsep}{self.env['PATH']}", "FAKE_GH_STATE": str(state)}
        self.run_tool("config", "--tracker", "github", "--github-repo", "example-org/example-app", "--team-key", "ACM",
                      tool=self.installed_tool(), env=env)
        git(self.proj, "add", "-A")
        git(self.proj, "commit", "-qm", "config")
        git(self.proj, "push", "-q", "origin", "main")
        git(self.proj, "switch", "-q", "-c", "12-fix-export")
        (self.proj / "docs/uat").mkdir(parents=True, exist_ok=True)
        (self.proj / "docs/uat/GH-12-fix-export.md").write_text("# UAT plan\n")
        git(self.proj, "add", "-A")
        git(self.proj, "commit", "-qm", "#12: fix")
        git(self.proj, "push", "-q", "origin", "12-fix-export")
        git(self.proj, "switch", "-q", "main")
        git(self.proj, "branch", "-D", "12-fix-export")
        state.write_text(json.dumps({"me": "tester", "projects": [], "issues": {}, "items": [], "next_issue": 1,
                                     "next_id": 1, "comments": [], "labels": [], "secrets": [], "prs": {
            "5": {"title": "#12: Fix export", "body": "Refs #12", "headRefName": "12-fix-export", "isDraft": False,
                  "state": "OPEN", "labels": [], "url": "https://pr/5"}}}))
        res = json.loads(self.run_tool("checkout-pr", "12", "--json", tool=self.installed_tool(), env=env).stdout)
        self.assertEqual(res["pr"], 5)
        self.assertEqual(res["uat_plan"], "docs/uat/GH-12-fix-export.md")
        self.assertTrue((self.proj / "docs/uat/GH-12-fix-export.md").exists())
        self.run_tool("checkout-pr", "--back", tool=self.installed_tool(), env=env)
        self.assertEqual(subprocess.run(["git", "branch", "--show-current"], cwd=self.proj, capture_output=True,
                                        text=True).stdout.strip(), "main")
        # Refuses to switch over unsaved work
        (self.proj / "README.md").write_text("changed\n")
        p = self.run_tool("checkout-pr", "12", tool=self.installed_tool(), env=env, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("unsaved changes", p.stderr)

    @unittest.skipUnless(shutil.which("gitleaks"), "needs gitleaks")
    def test_secret_hook_scans_the_worktree_being_committed(self):
        wt = Path(json.loads(self.wt("new", "w1", "--json").stdout)["path"])
        hook = str(self.proj / ".claude/hooks/block-secrets.sh")
        env = {**self.env, "CLAUDE_PROJECT_DIR": str(self.proj)}
        def run_hook(cwd_field, command="git commit -m x"):
            return subprocess.run(["bash", hook], cwd=self.proj, text=True, capture_output=True, env=env,
                                  input=json.dumps({"cwd": str(cwd_field), "tool_input": {"command": command}})).returncode
        # A secret in the worktree is caught, even though the main folder is clean
        (wt / "leak.py").write_text('key = "AKIA4XN7PQ2LMZ8RT6WB"\n')
        self.assertEqual(run_hook(wt), 2)
        self.assertEqual(run_hook(self.proj, f"git -C {wt} commit -m x"), 2)
        self.assertEqual(run_hook(self.proj, f"cd {wt} && git commit -m x"), 2)
        self.assertEqual(run_hook(self.proj, f'cd "{wt}" && echo "done" && git commit -m "x"'), 2)
        self.assertEqual(run_hook(self.proj, f"git -c user.name=x -C {wt} commit -m x"), 2)
        self.assertEqual(run_hook(wt, "WT=/nowhere; cd $WT && git commit -m x"), 2)      # unknown dir → session folder
        self.assertEqual(run_hook(wt, "git status"), 0)                                 # not a commit
        # Unrelated changes in the main folder don't block a clean worktree's commit
        (wt / "leak.py").unlink()
        (self.proj / "other.py").write_text('key = "AKIA4XN7PQ2LMZ8RT6WB"\n')
        self.assertEqual(run_hook(wt), 0)
        self.assertEqual(run_hook(self.proj), 2)

    def test_test_first_local_branch_then_publish(self):
        bin_dir = self.tmp / "bin"
        install_fake_gh_projects(bin_dir)
        state = self.tmp / "gh-state.json"
        env = {**self.env, "PATH": f"{bin_dir}{os.pathsep}{self.env['PATH']}", "FAKE_GH_STATE": str(state),
               "FAKE_GH_ORIGIN": str(self.origin)}
        tool = lambda *a, **kw: self.run_tool(*a, tool=self.installed_tool(), env=env, **kw)
        tool("config", "--tracker", "github", "--github-repo", "example-org/example-app", "--team-key", "ACM")
        tool("github-project", "--apply")
        git(self.proj, "add", "-A")
        git(self.proj, "commit", "-qm", "config")
        git(self.proj, "push", "-q", "origin", "main")
        n = json.loads(tool("issue", "create", "--stream", "bug", "--title", "Export crash", "--status", "UAT",
                            "--json").stdout)["number"]
        # The agent built it in its worktree: a local branch, no PR
        wt = Path(json.loads(tool("worktree", "new", "agent", "--json").stdout)["path"])
        git(wt, "switch", "-q", "-c", f"{n}-export-crash")
        (wt / "fix.txt").write_text("fixed\n")
        git(wt, "add", "fix.txt")
        git(wt, "commit", "-qm", f"#{n}: fix")
        res = json.loads(tool("checkout-pr", str(n), "--json").stdout)
        self.assertIsNone(res["pr"])
        self.assertEqual(res["branch"], f"{n}-export-crash")
        self.assertFalse(res["pushed"])
        self.assertTrue((self.proj / "fix.txt").exists())                       # the owner is testing it locally
        tool("checkout-pr", "--back")
        # publish needs the human's pass, the owner's folder, and exactly the tested commit
        self.assertNotEqual(tool("publish", str(n), check=False).returncode, 0)
        p = tool("publish", str(n), "--human", cwd=wt, check=False)
        self.assertIn("never from an agent's worktree", p.stderr)
        res = json.loads(tool("publish", str(n), "--human", "--json").stdout)
        st = json.loads(state.read_text())
        pr = next(p for p in st["prs"].values())
        self.assertEqual(pr["title"], f"#{n}: Export crash")
        self.assertIn({"name": "uat-passed"}, pr["labels"])
        self.assertIn(f"Refs #{n}", pr["body"])
        remote = subprocess.run(["git", "rev-parse", f"{n}-export-crash"], cwd=self.origin, capture_output=True,
                                text=True).stdout.strip()
        self.assertEqual(remote, res["commit"])                                 # the tested commit was pushed
        self.assertEqual(json.loads(tool("issue", "view", str(n), "--json").stdout)["issue"]["status"], "In Review")
        # The pass is recorded on exactly that commit, for the gate
        self.assertIn({"state": "success", "context": "uat", "sha": res["commit"]},
                      [{k: x[k] for k in ("state", "context", "sha")} for x in st["statuses"]])
        # A later failed test of the same commit withdraws the pass: ship can't bring the label back
        out = json.loads(tool("test-failed", str(n), "--human", "--json").stdout)
        self.assertTrue(any("removed uat-passed" in d for d in out["done"]))
        p = tool("ship", str(n), "--human", "--no-deploy", check=False)
        self.assertEqual(p.returncode, 1)
        self.assertIn("hasn't passed UAT", p.stdout + p.stderr)
        # A change pushed after the test is refused (unpushed local commits aren't the hand-over)
        (wt / "fix.txt").write_text("changed again\n")
        git(wt, "commit", "-qam", "more")
        git(wt, "push", "-q", "origin", f"{n}-export-crash")
        p = tool("publish", str(n), "--human", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("changed since it was tested", p.stderr)

    def test_test_first_batch_and_races(self):
        bin_dir = self.tmp / "bin"
        install_fake_gh_projects(bin_dir)
        state = self.tmp / "gh-state.json"
        env = {**self.env, "PATH": f"{bin_dir}{os.pathsep}{self.env['PATH']}", "FAKE_GH_STATE": str(state),
               "FAKE_GH_ORIGIN": str(self.origin), "HAAM_POLL_SECONDS": "0", "HAAM_CHECKS_GRACE_SECONDS": "30"}
        tool = lambda *a, **kw: self.run_tool(*a, tool=self.installed_tool(), env=env, **kw)
        tool("config", "--tracker", "github", "--github-repo", "example-org/example-app", "--team-key", "ACM")
        tool("github-project", "--apply")
        git(self.proj, "add", "-A")
        git(self.proj, "commit", "-qm", "config")
        git(self.proj, "push", "-q", "origin", "main")
        a = json.loads(tool("issue", "create", "--stream", "bug", "--title", "Crash A", "--json").stdout)["number"]
        b = json.loads(tool("issue", "create", "--stream", "bug", "--title", "Crash B", "--status", "Ready",
                            "--json").stdout)["number"]
        # One batch branch, named after the first issue; the second issue's claim comment names it.
        branch = f"{a}-epic-crashes"
        tool("issue", "claim", str(b), "--tool", "test", "--branch", branch)
        wt = Path(json.loads(tool("worktree", "new", "agent", "--json").stdout)["path"])
        git(wt, "switch", "-q", "-c", branch)
        (wt / "fix.txt").write_text("fixed\n")
        git(wt, "add", "fix.txt")
        git(wt, "commit", "-qm", f"#{a} #{b}: fix")
        git(wt, "push", "-q", "-u", "origin", branch)
        git(wt, "commit", "-q", "--allow-empty", "-m", "not pushed yet")      # local differs from GitHub
        git(self.proj, "branch", "-q", f"spike/{a}-try")                       # spikes never count
        git(self.proj, "branch", "-q", f"{a}-old-attempt")                     # a leftover only on this computer
        res = json.loads(tool("checkout-pr", str(b), "--json").stdout)
        self.assertEqual(res["branch"], branch)
        self.assertTrue(res["pushed"])                                          # GitHub's copy is the hand-over
        self.assertIn("differs from GitHub", res["note"])
        tool("checkout-pr", "--back")
        res = json.loads(tool("checkout-pr", str(a), "--json").stdout)          # the lead: GitHub's branch wins
        self.assertEqual(res["branch"], branch)
        self.assertIn(f"Ignoring {a}-old-attempt", res["note"])
        tool("checkout-pr", "--back")
        # A bad --also stops before anything is pushed or opened
        p = tool("publish", str(b), "--human", "--also", "x1", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse(json.loads(state.read_text()).get("prs"))
        res = json.loads(tool("publish", str(b), "--human", "--json").stdout)
        self.assertEqual(res["issues"], [f"#{a}", f"#{b}"])                    # the whole batch, lead first
        st = json.loads(state.read_text())
        num, pr = next(iter(st["prs"].items()))
        self.assertEqual(pr["title"], f"#{a} #{b}: Crash A")
        # A stale release-gate failure right after a label change is the gate re-running, not a failed check
        st["prs"][num]["checks"] = [{"name": "ci", "bucket": "pass"}, {"name": "release-gate", "bucket": "fail"}]
        state.write_text(json.dumps(st))
        p = tool("ship", str(b), "--human", "--no-deploy", "--wait", "0.01", check=False)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        st = json.loads(state.read_text())
        del st["prs"][num]["checks"]
        # ship on a just-opened PR waits for the checks to start instead of stopping; and if the gate dropped
        # uat-passed in a race, ship puts it back, because the tested head carries the owner's `uat` status
        st["no_checks"] = 1
        st["prs"][num]["labels"] = []
        state.write_text(json.dumps(st))
        p = tool("ship", str(b), "--human", "--no-deploy", check=False)
        self.assertNotIn("No checks have started", p.stdout + p.stderr)
        self.assertIn("Put back 'uat-passed'", p.stdout + p.stderr)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        # An agent push after the test: no `uat` status on the new head, so ship refuses
        tool("checkout-pr", str(b), "--branch", branch)
        tool("checkout-pr", "--back")
        st = json.loads(state.read_text())
        st["prs"][num].update(labels=[], state="OPEN")
        state.write_text(json.dumps(st))
        git(wt, "push", "-q", "origin", branch)
        p = tool("ship", str(b), "--human", "--no-deploy", check=False)
        self.assertEqual(p.returncode, 1)
        self.assertIn("hasn't passed UAT", p.stdout + p.stderr)

    def test_release_grouping_one_pr_for_everything_passed(self):
        bin_dir = self.tmp / "bin"
        install_fake_gh_projects(bin_dir)
        state = self.tmp / "gh-state.json"
        env = {**self.env, "PATH": f"{bin_dir}{os.pathsep}{self.env['PATH']}", "FAKE_GH_STATE": str(state),
               "FAKE_GH_ORIGIN": str(self.origin), "HAAM_POLL_SECONDS": "0"}
        tool = lambda *a, **kw: self.run_tool(*a, tool=self.installed_tool(), env=env, **kw)
        tool("config", "--tracker", "github", "--github-repo", "example-org/example-app", "--team-key", "ACM")
        tool("settings", "--set", "grouping=release", "--set", "worktree_cleanup=manual", "--human")
        tool("github-project", "--apply")
        git(self.proj, "add", "-A")
        git(self.proj, "commit", "-qm", "config")
        git(self.proj, "push", "-q", "origin", "main")
        nums = []
        for title, fname in (("Fix A", "a.txt"), ("Fix B", "b.txt")):
            n = json.loads(tool("issue", "create", "--stream", "bug", "--title", title, "--status", "UAT",
                                "--json").stdout)["number"]
            nums.append(n)
            git(self.proj, "switch", "-q", "-c", f"{n}-fix", "main")
            (self.proj / fname).write_text(title + "\n")
            git(self.proj, "add", fname)
            git(self.proj, "commit", "-qm", f"#{n}: fix")
            git(self.proj, "push", "-q", "-u", "origin", f"{n}-fix")
            git(self.proj, "switch", "-q", "main")
            tool("checkout-pr", str(n))
            tool("checkout-pr", "--back")
            res = json.loads(tool("publish", str(n), "--human", "--json").stdout)
            self.assertTrue(res["release"])                                    # no PR per change
        self.assertFalse(json.loads(state.read_text()).get("prs"))
        st = json.loads(state.read_text())
        st["checks_pending"] = 3
        state.write_text(json.dumps(st))
        res = tool("ship", "--all", "--human", "--wait", "0", check=False)       # checks still running: run again
        self.assertEqual(res.returncode, 2, res.stdout + res.stderr)
        st = json.loads(state.read_text())
        st["checks_pending"] = 3
        state.write_text(json.dumps(st))
        res = tool("ship", "--all", "--human", "--wait", "0", check=False)       # same release, not a second one
        self.assertEqual(res.returncode, 2, res.stdout + res.stderr)
        self.assertIn("Carrying on with release PR", res.stdout)
        self.assertEqual(len(json.loads(state.read_text())["prs"]), 1)
        st = json.loads(state.read_text())
        st["checks_pending"] = 0
        state.write_text(json.dumps(st))
        res = tool("ship", "--all", "--human", "--abandon-release", check=False)  # drop it, build a fresh one
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("dropped (you asked to abandon it)", res.stdout)
        st = json.loads(state.read_text())
        self.assertEqual(sorted(p["state"] for p in st["prs"].values()), ["CLOSED", "MERGED"])
        rel = [p for p in st["prs"].values() if p["state"] == "MERGED"]
        self.assertEqual(len(rel), 1)                                          # one release PR shipped
        self.assertTrue(rel[0]["headRefName"].startswith("release/"))
        self.assertEqual(rel[0]["title"].split(":")[0], f"#{nums[0]} #{nums[1]}")
        self.assertEqual(rel[0]["state"], "MERGED")
        self.assertEqual(len(st["approvals"]), 1)                              # one deploy
        for n in nums:
            self.assertEqual(st["issues"][str(n)]["state"], "CLOSED")
            self.assertIn(f"repos/example-org/example-app/git/refs/heads/{n}-fix", st["deleted_refs"])
        tested = json.loads((self.proj / ".haam/tested.json").read_text())
        self.assertFalse(tested.get("passed"))
        # Both changes are in the release branch that was merged
        files = subprocess.run(["git", "ls-tree", "--name-only", rel[0]["headRefName"]], cwd=self.origin,
                               capture_output=True, text=True).stdout.split()
        self.assertTrue({"a.txt", "b.txt"} <= set(files))

    def test_config_owner_flags_need_human(self):
        tool = self.installed_tool()
        self.run_tool("config", "--product", "Acme", "--team-key", "ACM", "--github-repo", "example-org/example-app",
                      tool=tool)
        p = self.run_tool("config", "--deploy", "manual", tool=tool, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--human", p.stderr)
        self.run_tool("config", "--product", "Acme 2", tool=tool)               # ordinary fields are fine
        self.run_tool("config", "--deploy", "manual", "--human", tool=tool)
        self.assertEqual(json.loads((self.proj / "haam.config.json").read_text())["deploy"], "manual")
        wt = Path(json.loads(self.wt("new", "w2", "--json").stdout)["path"])
        p = self.run_tool("config", "--max-in-uat", "50", "--human", tool=tool, cwd=wt, check=False)
        self.assertNotEqual(p.returncode, 0)

    def test_overlap_finds_waiting_branches_with_the_same_files(self):
        bin_dir = self.tmp / "bin"
        install_fake_gh_projects(bin_dir)
        state = self.tmp / "gh-state.json"
        env = {**self.env, "PATH": f"{bin_dir}{os.pathsep}{self.env['PATH']}", "FAKE_GH_STATE": str(state)}
        tool = lambda *a, **kw: self.run_tool(*a, tool=self.installed_tool(), env=env, **kw)
        tool("config", "--tracker", "github", "--github-repo", "example-org/example-app", "--team-key", "ACM")
        tool("github-project", "--apply")
        git(self.proj, "add", "-A")
        git(self.proj, "commit", "-qm", "config")
        git(self.proj, "push", "-q", "origin", "main")
        for title, path in (("Login fix", "src/auth/login.py"), ("Report fix", "src/reports/pdf.py")):
            n = json.loads(tool("issue", "create", "--stream", "bug", "--title", title, "--status", "UAT",
                                "--json").stdout)["number"]
            git(self.proj, "switch", "-q", "-c", f"{n}-fix", "main")
            (self.proj / path).parent.mkdir(parents=True, exist_ok=True)
            (self.proj / path).write_text("x\n")
            git(self.proj, "add", path)
            git(self.proj, "commit", "-qm", f"#{n}: fix")
            git(self.proj, "push", "-q", "-u", "origin", f"{n}-fix")
            git(self.proj, "switch", "-q", "main")
        res = json.loads(tool("overlap", "--files", "src/auth/,docs/x.md", "--json").stdout)
        self.assertEqual(len(res["waiting"]), 2)
        self.assertEqual(len(res["overlapping"]), 1)
        self.assertTrue(res["overlapping"][0].endswith("-fix"))
        hit = next(w for w in res["waiting"] if w["overlap"])
        self.assertEqual(hit["overlap"], ["src/auth/login.py"])
        self.assertIn("No overlap", tool("overlap", "--files", "src/billing/**").stdout)
        res = json.loads(tool("overlap", "--files", "src/reports/pdf.py", "--branch", res["overlapping"][0],
                              "--json").stdout)
        self.assertEqual(res["overlapping"], [])                             # only the branch given is compared

    def test_production_lists_production_code_changes(self):
        tool = self.installed_tool()
        self.run_tool("config", "--product", "Acme", "--team-key", "ACM", "--github-repo", "example-org/example-app", tool=tool)
        git(self.proj, "add", "-A")
        git(self.proj, "commit", "-qm", "config")
        git(self.proj, "push", "-q", "origin", "main")
        git(self.proj, "switch", "-q", "-c", "spike/7-voice", "main")
        for f in ("prototypes/voice/app.py", "tests/test_voice.py", "docs/notes.md", "src/voice.py"):
            (self.proj / f).parent.mkdir(parents=True, exist_ok=True)
            (self.proj / f).write_text("x\n")
        git(self.proj, "add", "-A")
        git(self.proj, "commit", "-qm", "spike")
        res = json.loads(self.run_tool("production", "--json", tool=tool).stdout)
        self.assertEqual(res["production"], ["src/voice.py"])
        self.assertTrue(res["spike"])
        self.assertIn("can't ship as it is", self.run_tool("production", tool=tool).stdout)
        self.assertEqual(self.run_tool("production", "--check", tool=tool, check=False).returncode, 1)
        # The project narrows production code to src/; changing it later needs the owner
        git(self.proj, "switch", "-q", "main")
        p = self.run_tool("config", "--production", "lib/**", tool=tool, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.run_tool("config", "--production", "src/**", "--not-production", "src/fixtures/**", "--human", tool=tool)
        cfg = json.loads((self.proj / "haam.config.json").read_text())
        self.assertEqual(cfg["production_paths"], ["src/**"])
        self.assertIn("src/fixtures/**", cfg["non_production_paths"])
        self.assertIn("prototypes/**", cfg["non_production_paths"])
        self.assertNotEqual(self.run_tool("config", "--not-production", "x/**", tool=tool, check=False).returncode, 0)
        self.run_tool("config", "--remove-not-production", "docs/**", "--human", tool=tool)
        self.assertNotIn("docs/**", json.loads((self.proj / "haam.config.json").read_text())["non_production_paths"])
        # publish refuses a spike the owner tried
        git(self.proj, "add", "-A")
        git(self.proj, "commit", "-qm", "settings")
        self.run_tool("checkout-pr", "APP-7", "--branch", "spike/7-voice", tool=tool)
        p = self.run_tool("publish", "APP-7", "--human", tool=tool, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("prototype", p.stdout + p.stderr)

    def test_ship_refuses_in_an_agents_worktree(self):
        wt = Path(json.loads(self.wt("new", "w1", "--json").stdout)["path"])
        p = self.run_tool("ship", "12", "--human", tool=self.installed_tool(), cwd=wt, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("never from an agent's worktree", p.stderr)

    def test_doctor_reports_parallel_chat_setup(self):
        out = json.loads(self.run_tool("doctor", "--json", tool=self.installed_tool()).stdout)
        sec = next(s for s in out["sections"] if s["title"] == "Parallel chats")
        status = {i["text"]: i["status"] for i in sec["items"]}
        self.assertEqual(status[".worktreeinclude"], "ok")
        self.assertEqual(status[".claude/worktrees/ is git-ignored"], "ok")


class TestExclusive(ToolTestCase):
    """haam.py exclusive: one heavy run at a time on this machine, shared by every worktree."""

    def setUp(self):
        super().setUp()
        (self.proj / "haam.config.json").write_text(json.dumps({"heavy_runs": ["heavy-marker"]}))
        self.lock_dir = self.proj / ".git" / "haam-exclusive.lock"

    def ex(self, who, *cmd, quiet="0.3", cwd=None, check=False):
        return self.run_tool("exclusive", who, "--quiet", quiet, "--", *cmd, cwd=cwd, check=check)

    def py(self, code):
        return [sys.executable, "-c", code]

    def test_lock_released_after_success_and_failure(self):
        p = self.ex("chat A", *self.py("import os,sys; print(os.path.isdir(sys.argv[1]))"), str(self.lock_dir),
                    check=True)
        self.assertEqual(p.stdout.strip(), "True")                           # held while the command runs
        self.assertFalse(self.lock_dir.exists())
        p = self.ex("chat A", *self.py("import sys; sys.exit(3)"))
        self.assertEqual(p.returncode, 3)                                    # the command's own exit code
        self.assertFalse(self.lock_dir.exists())

    def test_lock_released_when_interrupted(self):
        pidfile = self.tmp / "child.pid"
        a = subprocess.Popen([sys.executable, str(TOOL), "exclusive", "chat A", "--quiet", "0.2", "--",
                              *self.py("import os,sys,time; open(sys.argv[1],'w').write(str(os.getpid())); time.sleep(60)"),
                              str(pidfile)], cwd=self.proj, env=self.env, stderr=subprocess.DEVNULL)
        for _ in range(100):
            if pidfile.exists() and pidfile.read_text():
                break
            time.sleep(0.1)
        self.assertTrue(self.lock_dir.exists())
        a.send_signal(signal.SIGTERM)
        a.wait(timeout=20)
        self.assertFalse(self.lock_dir.exists())
        child = int(pidfile.read_text())
        for _ in range(50):
            try:
                os.kill(child, 0)
            except ProcessLookupError:
                break
            time.sleep(0.1)
        else:
            self.fail("the command was left running")

    def test_second_caller_waits_for_the_first_even_from_another_worktree(self):
        wt = self.tmp / "wt"
        git(self.proj, "worktree", "add", "-q", "--detach", str(wt))
        (wt / "haam.config.json").write_text(json.dumps({"heavy_runs": ["heavy-marker"]}))
        marks = self.tmp / "marks"
        a = subprocess.Popen([sys.executable, str(TOOL), "exclusive", "chat A", "--quiet", "0.2", "--",
                              *self.py("import sys,time; time.sleep(1.5); open(sys.argv[1],'a').write('A-end %f\\n' % time.time())"),
                              str(marks)], cwd=self.proj, env=self.env, stderr=subprocess.DEVNULL)
        for _ in range(100):
            if self.lock_dir.exists():
                break
            time.sleep(0.05)
        p = self.ex("chat B", *self.py("import sys,time; open(sys.argv[1],'a').write('B-start %f\\n' % time.time())"),
                    str(marks), cwd=wt, check=True)
        a.wait(timeout=20)
        self.assertIn("Waiting for chat A", p.stderr)
        t = dict(line.split() for line in marks.read_text().splitlines())
        self.assertGreaterEqual(float(t["B-start"]), float(t["A-end"]))

    def test_never_waits_for_itself(self):
        start = time.time()
        # Its own command line, and the shell around it, both match the heavy-run pattern
        p = subprocess.run(["bash", "-c", f"'{sys.executable}' '{TOOL}' exclusive me --quiet 0.3 -- "
                                          f"bash -c 'echo heavy-marker; sleep 0.5'"],
                           cwd=self.proj, env=self.env, capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertLess(time.time() - start, 8)
        self.assertNotIn("Waiting", p.stderr)

    def test_waits_for_a_heavy_run_that_skips_the_lock(self):
        other = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(2)", "heavy-marker"],
                                 start_new_session=True)
        try:
            p = self.ex("chat B", *self.py("import time; print(time.time())"), check=True)
            self.assertIn("other heavy run", p.stderr)
            self.assertIsNotNone(other.poll())                               # it ran only after the other finished
        finally:
            other.kill()

    def test_takes_over_a_lock_whose_owner_died(self):
        self.lock_dir.mkdir()
        (self.lock_dir / "owner").write_text(json.dumps({"who": "a crashed chat", "pid": 999999,
                                                         "host": os.uname().nodename, "since": "earlier"}))
        p = self.ex("chat A", "true", check=True)
        self.assertIn("a crashed chat", p.stderr)
        self.assertFalse(self.lock_dir.exists())

    def test_gives_up_after_the_timeout(self):
        self.lock_dir.mkdir()
        (self.lock_dir / "owner").write_text(json.dumps({"who": "chat A", "pid": os.getpid(),
                                                         "host": os.uname().nodename, "since": "now"}))
        p = self.run_tool("exclusive", "chat B", "--timeout", "0.02", "--", "true", check=False)
        self.assertEqual(p.returncode, 124)
        self.assertTrue(self.lock_dir.exists())                              # someone else's lock is left alone

    def test_config_adds_heavy_runs(self):
        (self.proj / "haam.config.json").unlink()
        self.run_tool("config", "--product", "Acme", "--heavy-run", "make (check|test-integration)")
        self.assertEqual(json.loads((self.proj / "haam.config.json").read_text())["heavy_runs"],
                         ["make (check|test-integration)"])
        self.run_tool("config", "--clear-heavy-runs")
        self.assertEqual(json.loads((self.proj / "haam.config.json").read_text())["heavy_runs"], [])


def git_status(cwd):
    return subprocess.run(["git", "status", "--porcelain"], cwd=cwd, capture_output=True, text=True).stdout


if __name__ == "__main__":
    unittest.main()
