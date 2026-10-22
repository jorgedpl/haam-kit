#!/usr/bin/env python3
"""Tests for `haam.py exclusive` (kit issue #5): heavy runs take turns in order, and go to another machine when it is free.

Each test makes its own throwaway git repositories under a temporary folder, so it never touches this clone's lock.
The remote runner is faked with an `ssh` on PATH that runs the remote command locally, with HOME set to the
temporary folder, so `git push host:path` and the remote script both land in a local "remote" clone.

Run: python -m unittest discover -s tests
"""
import importlib.util
import os
import sys as _sys
_sys.dont_write_bytecode = True  # keep the kit free of __pycache__
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HAAM = Path(__file__).resolve().parent.parent / "template" / "tools" / "haam" / "haam.py"


def load_haam():
    spec = importlib.util.spec_from_file_location("haam_under_test", HAAM)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def make_repo(path, makefile="setup:\n\t@true\n"):
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "main")
    git(path, "config", "user.email", "test@example.invalid")
    git(path, "config", "user.name", "Test")
    (path / "tools" / "haam").mkdir(parents=True)
    shutil.copy(HAAM, path / "tools" / "haam" / "haam.py")
    (path / "Makefile").write_text(makefile)
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", "start")
    return path


class TakeTurnsInOrder(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="haam-exclusive-test-"))
        self.repo = make_repo(self.tmp / "repo")
        self.env = {k: v for k, v in os.environ.items() if k != "HAAM_REMOTE_RUNNER"}

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def start(self, who, *command):
        return subprocess.Popen([sys.executable, str(HAAM), "exclusive", who, "--quiet", "0", "--", *command],
                                cwd=self.repo, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def test_waiters_get_the_lock_in_the_order_they_came(self):
        """AC1: three waiters started one after another run in that order."""
        order = self.tmp / "order.txt"
        holder = self.start("holder", "sleep", "3")
        time.sleep(0.8)
        waiters = []
        for name in ("first", "second", "third"):
            waiters.append(self.start(name, "sh", "-c", f"echo {name} >> {order}"))
            time.sleep(0.4)
        for p in [holder, *waiters]:
            p.communicate(timeout=60)
            self.assertEqual(p.returncode, 0)
        self.assertEqual(order.read_text().split(), ["first", "second", "third"])

    def test_a_dead_process_ticket_does_not_block(self):
        """AC2: a ticket left by a process that no longer exists is dropped, and the run goes ahead."""
        common = Path(git(self.repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
        queue = common / "haam-exclusive.lock.queue"
        queue.mkdir()
        dead = subprocess.Popen(["true"])
        dead.wait()
        (queue / f"{1:020d}-{dead.pid}").write_text("{}\n")
        p = self.start("after a dead ticket", "true")
        p.communicate(timeout=30)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(list(queue.iterdir()), [])


class OnlyMakeGoesRemote(unittest.TestCase):
    def test_eligible_commands(self):
        """AC5: only plain `make <targets>` may go to another machine."""
        haam = load_haam()
        self.assertTrue(haam.remote_eligible(["make", "check"]))
        self.assertTrue(haam.remote_eligible(["make", "test-kotlin", "CTF_X=1"]))
        self.assertFalse(haam.remote_eligible(["bash", "/private/tmp/run.sh"]))
        self.assertFalse(haam.remote_eligible(["make", "-C", "/Users/x/worktree", "check"]))
        self.assertFalse(haam.remote_eligible(["./gradlew", "check"]))
        self.assertFalse(haam.remote_eligible([]))


FAKE_SSH = """#!/bin/sh
# A stand-in for ssh: drop the options and the host, then run the remote command here.
while [ $# -gt 0 ]; do
  case "$1" in
    -o) shift 2 ;;
    -*) shift ;;
    *) break ;;
  esac
done
shift
cd "$HOME" || exit 255   # a real ssh session starts in the remote home folder
exec sh -c "$*"
"""


@unittest.skipUnless(shutil.which("zsh"), "the remote script runs under zsh")
class RunsOnTheOtherMachineWhenFree(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="haam-exclusive-remote-"))
        makefile = "setup:\n\t@true\ncheck:\n\t@echo ran-on-the-other-machine; exit 3\n"
        self.local = make_repo(self.tmp / "Developer" / "local", makefile)
        self.remote = self.tmp / "Developer" / "remote"
        subprocess.run(["git", "clone", "-q", str(self.local), str(self.remote)], check=True)
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        (bin_dir / "ssh").write_text(FAKE_SSH)
        (bin_dir / "ssh").chmod(0o755)
        self.env = dict(os.environ, PATH=f"{bin_dir}{os.pathsep}{os.environ['PATH']}", HOME=str(self.tmp),
                        HAAM_REMOTE_RUNNER="studio", HAAM_REMOTE_REPO="Developer/remote", ZDOTDIR=str(self.tmp))
        # This machine is busy: a live process holds the local lock for the whole test.
        self.sleeper = subprocess.Popen(["sleep", "120"])
        common = Path(git(self.local, "rev-parse", "--path-format=absolute", "--git-common-dir"))
        (common / "haam-exclusive.lock").mkdir()
        (common / "haam-exclusive.lock" / "owner").write_text(
            '{"who": "someone else", "pid": %d, "host": "%s", "since": "now"}\n' % (self.sleeper.pid, os.uname().nodename))

    def tearDown(self):
        self.sleeper.kill()
        self.sleeper.wait()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_make_runs_there_and_its_exit_code_comes_back(self):
        """AC4: with the remote free, the run happens there, its output and exit code come back, nothing is left."""
        (self.local / "uncommitted.txt").write_text("a change not yet committed\n")
        p = subprocess.run([sys.executable, str(HAAM), "exclusive", "remote test", "--quiet", "0", "--", "make", "check"],
                           cwd=self.local, env=self.env, capture_output=True, text=True, timeout=120)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)   # make exits 2 when a recipe fails, here or there
        self.assertIn("ran-on-the-other-machine", p.stdout)
        self.assertEqual(git(self.remote, "for-each-ref", "refs/haam-remote"), "")
        self.assertEqual(len(git(self.remote, "worktree", "list").splitlines()), 1)
        self.assertEqual(git(self.local, "status", "--porcelain"), "?? uncommitted.txt")   # this tree is untouched

    def test_a_non_make_command_stays_here(self):
        """AC5: a script never goes remote, even with the remote free; here it waits for the local lock."""
        p = subprocess.run([sys.executable, str(HAAM), "exclusive", "script", "--timeout", "0.05", "--quiet", "0", "--",
                            "sh", "-c", "echo should-not-run"], cwd=self.local, env=self.env, capture_output=True,
                           text=True, timeout=60)
        self.assertEqual(p.returncode, 124)
        self.assertNotIn("should-not-run", p.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
