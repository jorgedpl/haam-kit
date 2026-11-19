#!/usr/bin/env python3
"""Tests for `haam.py exclusive` (kit issue #5, Verisia #908): heavy runs take turns in order, and go to another machine when it is free.

Each test makes its own throwaway git repositories under a temporary folder, so it never touches this clone's lock.
The remote runner is faked with an `ssh` on PATH that runs the remote command locally, with HOME set to the
temporary folder, so `git push host:path` and the remote script both land in a local "remote" clone.

Run: python -m unittest discover -s tests
"""
import datetime
import importlib.util
import json
import os
import sys as _sys
_sys.dont_write_bytecode = True  # keep the kit free of __pycache__
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

# HAAM_UNDER_TEST runs these tests against another copy of the tool (to show a new test fails on the old one).
HAAM = Path(os.environ.get("HAAM_UNDER_TEST") or Path(__file__).resolve().parent.parent / "template" / "tools" / "haam" / "haam.py")


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


def run_log(repo):
    common = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    f = common / "haam-exclusive.log.jsonl"
    return [json.loads(line) for line in f.read_text().splitlines()] if f.exists() else []


def stamp(days_ago, clock):
    """A local time with its offset, as the log writes it: `days_ago` days back at `clock` (HH:MM:SS)."""
    day = datetime.date.today() - datetime.timedelta(days=days_ago)
    t = datetime.datetime.combine(day, datetime.time(*map(int, clock.split(":"))))
    return t.astimezone().isoformat(timespec="seconds")


class EveryRunIsLogged(unittest.TestCase):
    """Is the local queue a bottleneck? Each run leaves one line beside the lock (wait, run time, where it ran), and
    `exclusive --report` adds them up per day."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="haam-exclusive-test-"))
        self.repo = make_repo(self.tmp / "repo")
        self.common = Path(git(self.repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
        self.env = {k: v for k, v in os.environ.items() if k != "HAAM_REMOTE_RUNNER"}
        self.sleeper = None

    def tearDown(self):
        if self.sleeper:
            self.sleeper.kill()
            self.sleeper.wait()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def exclusive(self, *args):
        return subprocess.run([sys.executable, str(HAAM), "exclusive", *args], cwd=self.repo, env=self.env,
                              capture_output=True, text=True, timeout=60)

    def test_a_run_here_writes_one_line(self):
        p = self.exclusive("chat A, #7", "--quiet", "0", "--", "sh", "-c", "sleep 1; exit 3")
        self.assertEqual(p.returncode, 3, p.stderr)
        lines = run_log(self.repo)
        self.assertEqual(len(lines), 1, lines)
        r = lines[0]
        self.assertEqual((r["who"], r["command"], r["branch"], r["head"], r["exit"]),
                         ("chat A, #7", "sh -c sleep 1; exit 3", "main", git(self.repo, "rev-parse", "--short", "HEAD"), 3))
        self.assertEqual(r["machine"], socket.gethostname().split(".")[0])
        self.assertEqual([r[k] for k in ("remote", "fell_back", "stopped", "nested")], [False] * 4)
        asked, started, ended = (datetime.datetime.fromisoformat(r[k]) for k in ("asked", "started", "ended"))
        self.assertLessEqual(asked, started)
        self.assertGreaterEqual((ended - started).total_seconds(), 1)

    def test_a_run_that_gave_up_waiting_is_logged(self):
        self.sleeper = subprocess.Popen(["sleep", "120"])
        hold(self.common, self.sleeper.pid, "someone else", since(0))
        p = self.exclusive("chat B", "--quiet", "0", "--timeout", "0.03", "--", "true")
        self.assertEqual(p.returncode, 124, p.stderr)
        (r,) = run_log(self.repo)
        self.assertEqual((r["exit"], r["started"]), (124, None))
        self.assertIsNotNone(r["ended"])
        self.assertEqual(load_haam().run_log_summary([r])["total"]["gave_up"], 1)

    def test_a_nested_run_is_logged_as_nested_and_not_counted(self):
        p = self.exclusive("outer", "--quiet", "0", "--", sys.executable, str(HAAM), "exclusive", "inner", "--", "true")
        self.assertEqual(p.returncode, 0, p.stderr)
        lines = run_log(self.repo)
        self.assertEqual([(r["who"], r["nested"]) for r in lines], [("inner", True), ("outer", False)])
        total = load_haam().run_log_summary(lines)["total"]
        self.assertEqual((total["runs"], total["nested"]), (1, 1))

    def test_a_log_that_cant_be_written_changes_nothing(self):
        (self.common / "haam-exclusive.log.jsonl").mkdir()     # a folder where the file goes: every write fails
        for code in (0, 3):
            p = self.exclusive("chat C", "--quiet", "0", "--", "sh", "-c", f"exit {code}")
            self.assertEqual(p.returncode, code, p.stderr)
            self.assertNotIn("Traceback", p.stderr)

    def test_the_log_is_kept_short(self):
        haam = load_haam()
        haam.EXCLUSIVE_LOG_MAX_BYTES, haam.EXCLUSIVE_LOG_KEEP = 400, 5
        lock = self.common / "haam-exclusive.lock"
        for i in range(60):
            haam.log_run(lock, {"who": f"run {i}", "asked": "x"})
        lines = (self.common / "haam-exclusive.log.jsonl").read_text().splitlines()
        self.assertLessEqual(len(lines), 15)
        self.assertEqual(json.loads(lines[-1])["who"], "run 59")
        self.assertEqual(sorted(p.name for p in self.common.iterdir() if "trim" in p.name), [])

    def test_the_report_adds_up_the_log(self):
        def run(asked, started, ended, code, head="abc1234", command="make check", **flags):
            rec = {"who": "w", "command": command, "branch": "b", "head": head, "asked": asked, "started": started,
                   "ended": ended, "exit": code, "machine": "here", "remote": False, "fell_back": False,
                   "stopped": False, "nested": False}
            rec.update(flags)
            return json.dumps(rec)
        y, t = (lambda c: stamp(1, c)), (lambda c: stamp(0, c))
        log = [
            run(stamp(10, "10:00:00"), stamp(10, "10:00:00"), stamp(10, "10:05:00"), 0),     # before the window
            # Yesterday: failed on the runner, passed here on the same commit; a give-up; a nested run.
            run(y("10:00:00"), y("10:01:00"), y("10:11:00"), 2, remote=True, machine="studio"),
            run(y("10:21:00"), y("10:21:00"), y("10:22:00"), 0, nested=True),
            run(y("10:12:00"), y("10:20:00"), y("10:30:00"), 0),
            run(y("11:00:00"), None, y("12:00:00"), 124),
            "not json",
            # Today: a run stopped at its ceiling; a failure there whose pass here was another command.
            run(t("09:00:00"), t("09:00:30"), t("12:00:30"), 125, stopped=True),
            run(t("13:00:00"), t("13:00:10"), t("13:05:10"), 1, head="def5678", remote=True, machine="studio"),
            run(t("13:06:00"), t("13:06:05"), t("13:07:05"), 0, head="def5678", command="make lint"),
        ]
        (self.common / "haam-exclusive.log.jsonl").write_text("\n".join(log) + "\n")
        p = self.exclusive("--report", "--days", "3", "--json")
        self.assertEqual(p.returncode, 0, p.stderr)
        rep = json.loads(p.stdout)
        keys = ["runs", "nested", "wait_median_s", "wait_max_s", "run_median_s", "run_max_s", "remote", "gave_up",
                "stopped", "failed_there_passed_here"]
        days = {d["day"]: [d[k] for k in keys] for d in rep["per_day"]}
        self.assertEqual(days, {stamp(1, "00:00:00")[:10]: [3, 1, 270, 480, 600, 600, 1, 1, 0, 1],
                                stamp(0, "00:00:00")[:10]: [3, 0, 10, 30, 300, 10800, 1, 0, 1, 0]})
        self.assertEqual([rep["total"][k] for k in keys], [6, 1, 30, 480, 600, 10800, 2, 1, 1, 1])
        text = self.exclusive("--report", "--days", "3")
        self.assertEqual(text.returncode, 0, text.stderr)
        rows = [line.split() for line in text.stdout.splitlines()]
        self.assertIn(["All", "6", "30s", "8m00s", "10m00s", "3h00m", "2", "1", "1", "1"], rows)
        self.assertIn([stamp(1, "00:00:00")[:10], "3", "4m30s", "8m00s", "10m00s", "10m00s", "1", "1", "0", "1"], rows)
        doctor = [x for x in load_haam().heavy_lock_report(self.repo) if "last 7 days" in x[1]]
        self.assertEqual(len(doctor), 1)
        self.assertIn("last 7 days: 6, median wait 30s", doctor[0][1])

    def test_the_report_needs_no_log(self):
        p = self.exclusive("--report")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("No heavy runs logged here", p.stdout)


class CountsOnlyWhatAProcessItselfRuns(unittest.TestCase):
    """#1039: the queue deadlocked twice (23 and 26 Oct 2026) on shells whose command TEXT named a heavy run: a
    watcher loop reading a log, and a waiter's own wrapper. A shell given a command string runs nothing heavy
    itself; a heavy command it starts is a process of its own, and is counted as one."""

    def test_run_line(self):
        haam = load_haam()
        run_line = haam.run_line
        # A shell given a command string: whatever the string mentions, the shell itself runs nothing heavy.
        self.assertIsNone(run_line("zsh -c while true; do tail -n 3 make-k-check.log; ./gradlew check; sleep 5; done"))
        self.assertIsNone(run_line("/bin/zsh -c -l source /tmp/snapshot.sh && eval 'make check'"))
        self.assertIsNone(run_line("bash -lc python3 $H exclusive me -- make check # scripts/test-db-prepare.sh"))
        self.assertIsNone(run_line("/bin/zsh -o pipefail -c ./gradlew check"))
        self.assertIsNone(run_line("-zsh"))
        # A shell running a script file counts as that script; anything else counts as itself.
        self.assertEqual(run_line("/bin/bash ./scripts/test-db-prepare.sh"), "./scripts/test-db-prepare.sh")
        self.assertEqual(run_line("/bin/sh ./gradlew --no-daemon clean check"), "./gradlew --no-daemon clean check")
        self.assertEqual(run_line("make check"), "make check")
        self.assertEqual(run_line("/usr/bin/java -Dorg.gradle.appname=gradlew -classpath w.jar org.gradle.wrapper.GradleWrapperMain check"),
                         "/usr/bin/java -Dorg.gradle.appname=gradlew -classpath w.jar org.gradle.wrapper.GradleWrapperMain check")
        self.assertIsNone(run_line(""))

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="haam-exclusive-test-"))
        self.repo = make_repo(self.tmp / "repo")
        # A name no other process on this machine has, so a real heavy run here can't decide the outcome.
        self.tool = f"heavy-{os.getpid()}-{time.time_ns()}"
        (self.repo / "haam.config.json").write_text('{"heavy_runs": ["%s.*( check| integrationTest)"]}\n' % self.tool)
        self.env = {k: v for k, v in os.environ.items() if k != "HAAM_REMOTE_RUNNER"}
        self.others = []

    def tearDown(self):
        for p in self.others:
            p.kill()
            p.wait()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def other(self, *command):
        # Its own session, as another chat's run is: the queue never counts its own process group.
        p = subprocess.Popen(list(command), cwd=self.repo, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)
        self.others.append(p)
        time.sleep(0.5)
        return p

    def exclusive(self, *command, timeout_min="0.05"):
        return subprocess.run([sys.executable, str(HAAM), "exclusive", "a test run", "--quiet", "0.5",
                               "--timeout", timeout_min, "--", *command],
                              cwd=self.repo, env=self.env, capture_output=True, text=True, timeout=60)

    def test_a_watcher_loop_whose_text_names_a_heavy_run_does_not_block(self):
        """The 23 Oct deadlock: a background loop that reads a log, its command line naming ./gradlew check."""
        self.other("sh", "-c", f"while :; do sleep 1; done; ./{self.tool} check")
        done = self.exclusive("true")
        self.assertEqual(done.returncode, 0, done.stderr)

    def test_a_heavy_run_still_blocks_and_the_timeout_names_it(self):
        """The queue still waits for a real heavy run that doesn't use the lock, and says which one when it gives up."""
        tool = self.repo / self.tool
        tool.write_text("#!/bin/sh\nsleep 30\n")
        tool.chmod(0o755)
        heavy = self.other("sh", f"./{self.tool}", "check")
        done = self.exclusive("true")
        self.assertEqual(done.returncode, 124, done.stderr)
        gave_up = [line for line in done.stderr.splitlines() if line.startswith("✘ Gave up")]
        self.assertEqual(len(gave_up), 1, done.stderr)
        self.assertIn(f"pid {heavy.pid}", gave_up[0])
        self.assertIn(f"./{self.tool} check", gave_up[0])


class AFallbackKeepsItsPlace(unittest.TestCase):
    """#924: a run that went to the other machine and came back waits here from its first place in line, not behind
    everyone who came while it was away. While away it holds no ticket here, so it never holds up this machine."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="haam-exclusive-test-"))
        self.repo = make_repo(self.tmp / "repo")
        self.sleeper = subprocess.Popen(["sleep", "120"])
        common = Path(git(self.repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
        self.queue = common / "haam-exclusive.lock.queue"
        (common / "haam-exclusive.lock").mkdir()
        (common / "haam-exclusive.lock" / "owner").write_text(
            '{"who": "someone else", "pid": %d, "host": "%s", "since": "now"}\n' % (self.sleeper.pid, os.uname().nodename))

    def tearDown(self):
        self.sleeper.kill()
        self.sleeper.wait()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def turn(self, **kw):
        haam = load_haam()
        return haam, haam.MachineTurn("me", [], timeout_min=0.05, quiet_s=0, say=lambda _m: None, cwd=self.repo, **kw)

    def test_a_fallback_waits_ahead_of_those_who_came_later(self):
        haam, away = self.turn(remote_free=lambda: True)
        with self.assertRaises(haam.RemoteTurn) as moved:
            with away:
                pass
        self.assertEqual(list(self.queue.iterdir()), [])     # away: no ticket here
        later = self.queue / f"{time.time_ns():020d}-{self.sleeper.pid}"
        later.write_text("{}\n")
        _, back = self.turn(place=moved.exception.place)
        back._enqueue()
        try:
            self.assertEqual(back._ahead(), [])
            self.assertEqual(sorted(p.name for p in self.queue.iterdir()), sorted([back.ticket.name, later.name]))
        finally:
            back.release()
        self.assertEqual([p.name for p in self.queue.iterdir()], [later.name])


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

    def test_an_unreadable_runner_is_not_free_and_is_said_once(self):
        """Kit #20: on a Mac whose new Xcode licence nobody accepted, python3 fails there like make does, so the probe
        can't read the lock. The run stays here, and the wait says why once, not on every poll."""
        haam = load_haam()
        said = []
        failing = mock.Mock(returncode=69, stdout="", stderr="You have not agreed to the Xcode license agreements.\n")
        with mock.patch.object(haam.subprocess, "run", return_value=failing):
            check = haam.remote_watch("studio", "Developer/repo", {}, Path("/nonexistent/lock"), said.append, tool="make")
            self.assertFalse(check())
            self.assertFalse(check())
        self.assertEqual(len(said), 1, said)
        self.assertIn("Couldn't read studio's lock (You have not agreed to the Xcode license agreements.)", said[0])


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
if [ "$*" = "zsh -l -s" ]; then
  # The run itself (#924): keep the script it was sent, and act out FAKE_SSH_RUN's broken connection.
  [ "${FAKE_SSH_RUN:-}" = refuse ] && exit 255   # the connection never opened: nothing ran there
  cat > "$HOME/remote-script.sh"
  sh -c "$*" < "$HOME/remote-script.sh"
  rc=$?
  [ "${FAKE_SSH_RUN:-}" = drop-after ] && exit 255   # the connection dropped after the run had started
  exit $rc
fi
exec sh -c "$*"
"""


class OtherMachine(unittest.TestCase):
    """A "remote" clone reached through the stand-in ssh, while a live process holds this machine's lock."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="haam-exclusive-remote-"))
        # Each run of `check` adds the folder it ran in to runs.txt, so a run repeated here shows.
        makefile = "setup:\n\t@true\ncheck:\n\t@echo ran-on-the-other-machine; echo $(CURDIR) >> $(HOME)/runs.txt; exit 3\n"
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

    def exclusive(self, *options, run=None):
        env = dict(self.env, FAKE_SSH_RUN=run) if run else self.env
        return subprocess.run([sys.executable, str(HAAM), "exclusive", *options, "remote test", "--", "make", "check"],
                              cwd=self.local, env=env, capture_output=True, text=True, timeout=120)

    def runs(self):
        f = self.tmp / "runs.txt"
        return f.read_text().split() if f.exists() else []


@unittest.skipUnless(shutil.which("zsh"), "the remote script runs under zsh")
class RunsOnTheOtherMachineWhenFree(OtherMachine):
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

    def test_a_run_there_is_logged_here_and_there(self):
        """The asking machine logs the run as remote, with the exit code that came back; the runner's own exclusive
        logs it there under its own who."""
        p = self.exclusive("--quiet", "0")
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        (here,) = run_log(self.local)
        self.assertEqual((here["who"], here["exit"], here["machine"], here["remote"], here["fell_back"]),
                         ("remote test", 2, "studio", True, False))
        self.assertIsNotNone(here["started"])
        (there,) = run_log(self.remote)
        self.assertEqual(there["who"], f"remote test (from {socket.gethostname().split('.')[0]})")
        self.assertEqual((there["exit"], there["remote"], there["branch"]), (2, False, None))

    def test_a_run_that_did_not_start_there_is_logged_as_fallen_back(self):
        p = self.exclusive("--timeout", "0.05", "--quiet", "0", run="refuse")
        self.assertEqual(p.returncode, 124, p.stdout + p.stderr)
        (r,) = run_log(self.local)
        self.assertEqual((r["exit"], r["started"], r["remote"], r["fell_back"]), (124, None, False, True))
        self.assertEqual(r["machine"], socket.gethostname().split(".")[0])

    def test_a_connection_that_drops_during_the_run_is_not_run_again_here(self):
        """#924: on 2 Nov the connection to brain timed out 40 minutes into `make check`; exit 255 read as "didn't
        start", and the whole run started again on the laptop. A run that started there is never repeated here."""
        p = self.exclusive("--timeout", "0.05", "--quiet", "0", run="drop-after")
        self.assertEqual(p.returncode, 255, p.stdout + p.stderr)
        self.assertEqual(len(self.runs()), 1, self.runs())
        self.assertIn("haam-remote-", self.runs()[0])
        self.assertIn("dropped during the run", p.stderr)
        self.assertNotIn("staying here", p.stderr)

    def test_a_connection_that_never_opened_still_waits_here(self):
        """#924: nothing ran there, so the run waits for this machine (busy here, so it gives up: 124)."""
        p = self.exclusive("--timeout", "0.05", "--quiet", "0", run="refuse")
        self.assertEqual(p.returncode, 124, p.stdout + p.stderr)
        self.assertIn("didn't start", p.stderr)
        self.assertEqual(self.runs(), [])

    def test_the_wait_there_is_this_run_s_own(self):
        """#924: the other machine's `exclusive` waits as long as this run was told to, not its own 60 minutes."""
        p = self.exclusive("--timeout", "7", "--quiet", "0")
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        sent = (self.tmp / "remote-script.sh").read_text()
        line = [x for x in sent.splitlines() if "haam.py exclusive" in x]
        self.assertEqual(len(line), 1, sent)
        self.assertIn("--timeout 7 --quiet 0", line[0])

    def test_a_run_there_carries_this_machine_s_main(self):
        """#1869: the other clone's origin/main is its own, older one, so a branch's check there diffed against it and
        ran everything. The run carries this machine's main commit (HAAM_BASE_COMMIT), and the commit itself."""
        (self.local / "Makefile").write_text(
            "setup:\n\t@true\ncheck:\n\t@echo base=$$HAAM_BASE_COMMIT; git cat-file -e $$HAAM_BASE_COMMIT^{commit} && echo has-base\n")
        git(self.local, "commit", "-q", "-am", "newer main")
        git(self.local, "update-ref", "refs/remotes/origin/main", "HEAD")   # main here is newer than the other clone's
        main = git(self.local, "rev-parse", "HEAD")
        git(self.local, "commit", "-q", "--allow-empty", "-m", "the branch")
        p = self.exclusive("--timeout", "0.05", "--quiet", "0")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn(f"base={main}", p.stdout)
        self.assertIn("has-base", p.stdout)
        self.assertEqual(git(self.remote, "for-each-ref", "refs/haam-remote"), "")   # both refs are removed

    def test_the_tree_checked_there_holds_only_what_was_sent(self):
        """#1869, measured on the Mac Studio: `make setup`'s log, written into the temporary worktree's root, was an
        untracked file no area map knows, so check-changed planned everything there even with the right base."""
        (self.local / "Makefile").write_text(
            "setup:\n\t@echo setting up\ncheck:\n\t@echo status=[$$(git status --porcelain)]\n")
        git(self.local, "commit", "-q", "-am", "a setup that prints")
        p = self.exclusive("--timeout", "0.05", "--quiet", "0")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("status=[]", p.stdout)

    def test_a_non_make_command_stays_here(self):
        """AC5: a script never goes remote, even with the remote free; here it waits for the local lock."""
        p = subprocess.run([sys.executable, str(HAAM), "exclusive", "script", "--timeout", "0.05", "--quiet", "0", "--",
                            "sh", "-c", "echo should-not-run"], cwd=self.local, env=self.env, capture_output=True,
                           text=True, timeout=60)
        self.assertEqual(p.returncode, 124)
        self.assertNotIn("should-not-run", p.stdout)


# A make that refuses `--version` on the "other machine" (the fake ssh runs it with cwd $HOME), as a new Xcode with no
# accepted licence does, and is the real make everywhere else.
FAKE_MAKE = """#!/bin/sh
if [ "$1" = "--version" ] && [ -f "$HOME/make-broken" ]; then
  echo "You have not agreed to the Xcode license agreements." >&2
  exit 69
fi
exec %s "$@"
"""


@unittest.skipUnless(shutil.which("zsh") and shutil.which("make"), "the remote script runs under zsh")
class StaysHereWhenTheOtherMachineCannotRunTheTool(RunsOnTheOtherMachineWhenFree):
    def setUp(self):
        real_make = shutil.which("make")
        super().setUp()
        fake = self.tmp / "runner-bin"
        fake.mkdir()
        (fake / "make").write_text(FAKE_MAKE % real_make)
        (fake / "make").chmod(0o755)
        # The runner's own login shell finds it first, as a login zsh there would (macOS's /etc/zprofile rebuilds
        # PATH before the user's .zprofile runs, so a PATH passed in from outside is not enough).
        (self.tmp / ".zprofile").write_text(f'export PATH="{fake}:$PATH"\n')

    def test_a_runner_whose_make_fails_is_never_handed_the_run(self):
        """#20 AC1, AC2: a runner whose `make --version` fails is not free: the run stays here and waits for this
        machine's lock (here it times out, so nothing ran anywhere), and the warning names the error once."""
        (self.tmp / "make-broken").write_text("")
        p = subprocess.run([sys.executable, str(HAAM), "exclusive", "remote test", "--timeout", "0.05", "--quiet", "0",
                            "--", "make", "check"], cwd=self.local, env=self.env, capture_output=True, text=True,
                           timeout=120)
        self.assertEqual(p.returncode, 124, p.stdout + p.stderr)
        self.assertNotIn("ran-on-the-other-machine", p.stdout)
        self.assertEqual(p.stderr.count("can't run make"), 1, p.stderr)
        self.assertIn("You have not agreed to the Xcode license agreements.", p.stderr)
        self.assertEqual(git(self.remote, "for-each-ref", "refs/haam-remote"), "")

    def test_a_runner_whose_make_works_still_gets_the_run(self):
        """#20 AC3: the probe passes on a healthy runner, and the run goes there as before."""
        p = subprocess.run([sys.executable, str(HAAM), "exclusive", "remote test", "--quiet", "0", "--", "make", "check"],
                           cwd=self.local, env=self.env, capture_output=True, text=True, timeout=120)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("ran-on-the-other-machine", p.stdout)
        self.assertNotIn("can't run make", p.stderr)

    # The parent's own tests run here too, with the fake make: they must not change.


FAKE_GH = """#!/bin/sh
# A stand-in for gh: write down what was asked, never reach GitHub.
echo "$*" >> "$FAKE_GH_LOG"
"""


def since(hours_ago):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - hours_ago * 3600))


def hold(common, pid, who, started):
    (common / "haam-exclusive.lock").mkdir()
    (common / "haam-exclusive.lock" / "owner").write_text(
        '{"who": "%s", "pid": %d, "host": "%s", "since": "%s"}\n' % (who, pid, os.uname().nodename, started))


@unittest.skipUnless(shutil.which("zsh"), "the remote script runs under zsh")
class DeadEntriesOnTheOtherMachineDontCount(OtherMachine):
    """#1807: on 13 Nov 2026 a dropped ssh connection left a ticket on the Mac Studio, beside a dead holder's lock, and
    for about an hour every run on the laptop saw that machine as busy though nothing ran there."""

    def setUp(self):
        super().setUp()
        self.remote_common = Path(git(self.remote, "rev-parse", "--path-format=absolute", "--git-common-dir"))

    def dead_pid(self):
        p = subprocess.Popen(["true"])
        p.wait()
        return p.pid

    def test_a_dead_holder_and_a_dead_ticket_there_count_as_free(self):
        hold(self.remote_common, self.dead_pid(), "a run whose connection dropped", since(1))
        (self.remote_common / "haam-exclusive.lock.queue").mkdir()
        (self.remote_common / "haam-exclusive.lock.queue" / f"{1:020d}-{self.dead_pid()}").write_text("{}\n")
        p = self.exclusive("--timeout", "0.05", "--quiet", "0")
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("ran-on-the-other-machine", p.stdout)

    def test_a_live_waiter_there_still_counts(self):
        (self.remote_common / "haam-exclusive.lock.queue").mkdir()
        (self.remote_common / "haam-exclusive.lock.queue" / f"{1:020d}-{self.sleeper.pid}").write_text("{}\n")
        p = self.exclusive("--timeout", "0.05", "--quiet", "0")
        self.assertEqual(p.returncode, 124, p.stdout + p.stderr)
        self.assertEqual(self.runs(), [])


class Noticing(unittest.TestCase):
    """Shared set-up for #1796: a GitHub tracker whose gh is a stand-in that only writes down its calls."""

    def gh_setup(self, env):
        bin_dir = self.tmp / "gh-bin"
        bin_dir.mkdir()
        (bin_dir / "gh").write_text(FAKE_GH)
        (bin_dir / "gh").chmod(0o755)
        self.gh_log = self.tmp / "gh.log"
        return dict(env, PATH=f"{bin_dir}{os.pathsep}{env['PATH']}", FAKE_GH_LOG=str(self.gh_log))

    def comments(self):
        lines = self.gh_log.read_text().splitlines() if self.gh_log.exists() else []
        return [line.split(" -R ")[0] for line in lines]


class AStuckRunHereIsNoticedAndEnded(Noticing):
    """#1796: a run that makes no end is stopped at its ceiling, and a lock held for days is said and told once."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="haam-exclusive-test-"))
        self.repo = make_repo(self.tmp / "repo")
        (self.repo / "haam.config.json").write_text('{"tracker": "github", "github_repo": "example-org/not-a-repo"}\n')
        self.common = Path(git(self.repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
        self.env = self.gh_setup({k: v for k, v in os.environ.items() if k != "HAAM_REMOTE_RUNNER"})
        self.sleeper = None

    def tearDown(self):
        if self.sleeper:
            self.sleeper.kill()
            self.sleeper.wait()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def exclusive(self, *args):
        return subprocess.run([sys.executable, str(HAAM), "exclusive", *args], cwd=self.repo, env=self.env,
                              capture_output=True, text=True, timeout=90)

    def test_a_run_past_its_ceiling_is_ended_with_all_it_started(self):
        pidfile = self.tmp / "grandchild.pid"
        p = self.exclusive("a test, #4242", "--quiet", "0", "--max-run", "0.03", "--",
                           "sh", "-c", f"sleep 300 & echo $! > {pidfile}; wait")
        self.assertEqual(p.returncode, 125, p.stderr)
        self.assertIn("stopped after", p.stderr)
        grandchild = int(pidfile.read_text())
        time.sleep(0.2)
        self.assertFalse(load_haam().pid_alive(grandchild), "the command's own child is left running")
        self.assertFalse((self.common / "haam-exclusive.lock").exists())
        self.assertTrue((self.common / "haam-exclusive.stopped").exists())
        self.assertEqual(self.comments(), ["issue comment 4242"])

    def test_a_run_inside_its_ceiling_is_untouched(self):
        p = self.exclusive("a test, #4242", "--quiet", "0", "--max-run", "1", "--", "sh", "-c", "exit 7")
        self.assertEqual(p.returncode, 7, p.stderr)
        self.assertEqual(self.comments(), [])

    def test_a_lock_held_for_days_is_said_and_told_once(self):
        self.sleeper = subprocess.Popen(["sleep", "120"])
        hold(self.common, self.sleeper.pid, "chat-c, #1307", since(48))
        for _ in range(2):
            p = self.exclusive("me, #4242", "--quiet", "0", "--timeout", "0.03", "--", "true")
            self.assertEqual(p.returncode, 124, p.stderr)
            self.assertIn("far longer than any check takes", p.stderr)
        self.assertEqual(self.comments(), ["issue comment 1307"])

    def test_a_lock_held_an_hour_is_just_waited_for(self):
        self.sleeper = subprocess.Popen(["sleep", "120"])
        hold(self.common, self.sleeper.pid, "chat-c, #1307", since(1))
        p = self.exclusive("me, #4242", "--quiet", "0", "--timeout", "0.03", "--", "true")
        self.assertEqual(p.returncode, 124, p.stderr)
        self.assertNotIn("far longer", p.stderr)
        self.assertEqual(self.comments(), [])


@unittest.skipUnless(shutil.which("zsh"), "the remote script runs under zsh")
class AStuckRunThereIsNoticedAndEnded(OtherMachine, Noticing):
    """#1796: the Mac Studio's lock was held from 4 Nov to 13 Nov by a run with under a second of CPU, so no run went
    there for nine days and nobody was told."""

    def setUp(self):
        super().setUp()
        (self.local / "Makefile").write_text("setup:\n\t@true\ncheck:\n\t@exit 3\nhang:\n\tsleep 300\n")
        (self.local / "haam.config.json").write_text('{"tracker": "github", "github_repo": "example-org/not-a-repo"}\n')
        git(self.local, "add", "-A")
        git(self.local, "commit", "-q", "-m", "hang")
        self.remote_common = Path(git(self.remote, "rev-parse", "--path-format=absolute", "--git-common-dir"))
        self.env = self.gh_setup(self.env)
        self.holder = None

    def tearDown(self):
        if self.holder:
            self.holder.kill()
            self.holder.wait()
        super().tearDown()

    def run_there(self, who, target, *options):
        return subprocess.run([sys.executable, str(HAAM), "exclusive", *options, who, "--", "make", target],
                              cwd=self.local, env=self.env, capture_output=True, text=True, timeout=120)

    def test_a_run_sent_there_has_a_ceiling_by_default(self):
        p = self.run_there("me, #4242", "check", "--timeout", "7", "--quiet", "0")
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        line = [x for x in (self.tmp / "remote-script.sh").read_text().splitlines() if "haam.py exclusive" in x]
        self.assertIn("--max-run 180", line[0])
        self.assertIn("HAAM_EXCLUSIVE_NOTICE=off", line[0])

    def test_a_run_there_past_its_ceiling_is_ended_and_told_once_from_here(self):
        p = self.run_there("me, #4242", "hang", "--timeout", "1", "--quiet", "0", "--max-run", "0.03")
        self.assertEqual(p.returncode, 125, p.stdout + p.stderr)
        self.assertFalse((self.remote_common / "haam-exclusive.lock").exists())
        self.assertEqual(self.comments(), ["issue comment 4242"])
        p = self.run_there("me again, #4243", "check", "--timeout", "0.05", "--quiet", "0")   # reads the stop again
        self.assertEqual(self.comments(), ["issue comment 4242"])

    def test_a_lock_held_there_for_days_is_said_and_told_once(self):
        self.holder = subprocess.Popen(["sleep", "120"])
        hold(self.remote_common, self.holder.pid, "chat-c, #1307 (from laptop)", since(48))
        for _ in range(2):
            p = self.run_there("me, #4242", "check", "--timeout", "0.03", "--quiet", "0")
            self.assertEqual(p.returncode, 124, p.stdout + p.stderr)
            self.assertIn("studio's lock has been held since", p.stderr)
        self.assertEqual(self.comments(), ["issue comment 1307"])

    def test_doctor_reads_both_locks(self):
        self.holder = subprocess.Popen(["sleep", "120"])
        hold(self.remote_common, self.holder.pid, "chat-c, #1307 (from laptop)", since(48))
        with mock.patch.dict(os.environ, {k: self.env[k] for k in ("PATH", "HOME", "HAAM_REMOTE_RUNNER", "HAAM_REMOTE_REPO")}):
            lines = load_haam().heavy_lock_report(self.local)
        here = [x for x in lines if "here" in x[1]]
        there = [x for x in lines if "studio" in x[1]]
        self.assertEqual(here[0][0], "info", lines)          # held by the test's sleeper for minutes: just busy
        self.assertEqual(there[0][0], "warn", lines)
        self.assertIn("far longer than any check takes", there[0][1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
