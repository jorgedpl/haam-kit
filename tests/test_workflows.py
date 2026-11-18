"""The release gate and the AI reviews: their JavaScript tests, and the gate's two-step changeover.

Run:  python3 -m unittest discover -s tests -v
The JavaScript tests (tests/js/*.test.mjs) run each workflow's own script against a fake GitHub; they need node, as
the gate does on GitHub, and are skipped without it.
"""

import sys as _sys
_sys.dont_write_bytecode = True  # keep the kit free of __pycache__
import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import test_haam  # noqa: E402  (the module, so its test classes aren't collected twice)

ROOT = Path(__file__).resolve().parents[1]
GATES = ".github/workflows/gates.yml"


def git_out(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


@unittest.skipUnless(shutil.which("node"), "needs node")
class JavaScriptTests(unittest.TestCase):
    def test_gate_and_review_scripts(self):
        """Only the owner's (or a backup approver's) word counts; the gate is main's copy; both reviewers read the
        steering files from the base branch. Each test file says what it covers."""
        files = sorted(str(p) for p in (ROOT / "tests" / "js").glob("*.test.mjs"))
        self.assertEqual(len(files), 2, files)
        p = subprocess.run(["node", "--test", *files], cwd=ROOT, capture_output=True, text=True, timeout=600)
        tail = "\n".join((p.stdout + p.stderr).splitlines()[-60:])
        self.assertEqual(p.returncode, 0, tail)
        self.assertRegex(p.stdout, r"(?m)^ℹ fail 0$|^# fail 0$", tail)


class GateChangeover(test_haam.ToolTestCase):
    """The PR that first brings the gate on pull_request_target is judged before main has it, and main's old copy
    knows no pull_request_target: that PR would get no gate at all. So install and update keep the `haam:changeover`
    lines (a pull_request trigger) until main's copy listens to pull_request_target, and then remove them."""

    def gates(self):
        return (self.proj / GATES).read_text()

    def commit_as_main(self, message="main"):
        git_out(self.proj, "add", "-A")
        git_out(self.proj, "commit", "-qm", message)
        git_out(self.proj, "update-ref", "refs/remotes/origin/main", "HEAD")   # what GitHub runs: main's copy

    def new_kit(self):
        return test_haam.TestUpdate.make_new_kit(self)

    def test_first_install_writes_step_one(self):
        out = self.install().stdout
        text = self.gates()
        self.assertRegex(text, r"(?m)^  pull_request_target:$")
        self.assertRegex(text, r"(?m)^  pull_request:$", "the first PR needs the pull_request run")
        self.assertIn("step 1 of 2", out)

    def test_update_over_an_old_gate_writes_step_one_then_step_two(self):
        self.install()
        old = re.sub(r"(?m)^  pull_request_target:\n    types: .*\n", "", self.gates())     # the kit's old gate
        old = strip_changeover(old)
        (self.proj / GATES).write_text(old)
        lock = self.lock()
        lock["files"][GATES] = sha_text(old)
        (self.proj / "haam.lock.json").write_text(json.dumps(lock, indent=2) + "\n")
        self.commit_as_main("an older kit")

        new = self.new_kit()
        tool = new / "tools/haam/haam.py"
        out = self.run_tool("update", "--target", str(self.proj), "--apply", tool=tool).stdout
        self.assertIn("step 1 of 2", out)
        self.assertRegex(self.gates(), r"(?m)^  pull_request:$")
        # Run again on the same branch, before it merged: main's copy is still the old one, so still step 1.
        self.run_tool("update", "--target", str(self.proj), "--apply", tool=tool)
        self.assertRegex(self.gates(), r"(?m)^  pull_request:$")

        self.commit_as_main("the update merged")                        # main now has step 1
        out = self.run_tool("update", "--target", str(self.proj), "--apply", tool=tool).stdout
        text = self.gates()
        self.assertNotRegex(text, r"(?m)^  pull_request:$")
        self.assertRegex(text, r"(?m)^  pull_request_target:$")
        self.assertNotRegex(text, r"(?m)^\s*(#|//) (>>>|<<<) haam:changeover")
        self.assertNotIn("step 1 of 2", out)
        self.assertEqual(self.lock()["files"][GATES], sha_text(text), "recorded, so the next update sees it untouched")

    def test_changeover_command_finishes_step_two_on_the_same_kit_version(self):
        self.install()
        tool = self.installed_tool()
        refused = self.run_tool("changeover", "--apply", tool=tool, check=False)
        self.assertNotEqual(refused.returncode, 0, "main's copy doesn't listen to pull_request_target yet")
        self.assertIn("Not yet", refused.stderr)

        self.commit_as_main("install merged")
        doctor = self.run_tool("doctor", tool=tool, check=False).stdout
        self.assertIn("changeover is half done", doctor)
        self.assertIn("pull_request:", self.gates())
        self.run_tool("changeover", tool=tool)                            # plan only
        self.assertRegex(self.gates(), r"(?m)^  pull_request:$")
        self.run_tool("changeover", "--apply", tool=tool)
        text = self.gates()
        self.assertNotRegex(text, r"(?m)^  pull_request:$")
        self.assertEqual(self.lock()["files"][GATES], sha_text(text))
        self.assertIn("Nothing to do", self.run_tool("changeover", "--apply", tool=tool).stdout)
        self.commit_as_main("step 2 merged")
        self.assertNotIn("changeover is half done", self.run_tool("doctor", tool=tool, check=False).stdout)


def sha_text(text):
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()


def strip_changeover(text):
    """The changeover lines removed (what update writes once main's copy listens to pull_request_target)."""
    return re.sub(r"(?ms)^[ \t]*(?:#|//) >>> haam:changeover.*?\n.*?^[ \t]*(?:#|//) <<< haam:changeover.*?\n", "", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
