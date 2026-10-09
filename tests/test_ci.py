"""Run the workflow's whitespace command against disposable Git histories."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml


class CommittedWhitespaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="router-ci-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Synthetic Test")
        self.git("config", "user.email", "synthetic@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "core.hooksPath", str(self.root / "no-hooks"))
        self.base = self.commit("seed\n")
        workflow = Path(__file__).resolve().parents[1] / ".github/workflows/validate.yml"
        self.command = yaml.safe_load(workflow.read_text())["jobs"]["structure"]["steps"][-1]["run"]

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True,
                                       stderr=subprocess.STDOUT).strip()

    def commit(self, text):
        (self.root / "sample.txt").write_text(text)
        self.git("add", "sample.txt")
        self.git("commit", "-qm", "Synthetic change")
        return self.git("rev-parse", "HEAD")

    def check(self, base, head):
        env = {**os.environ, "ROUTER_BASE_SHA": base, "ROUTER_HEAD_SHA": head}
        return subprocess.run(["bash", "-eo", "pipefail", "-c", self.command],
                              cwd=self.root, env=env, capture_output=True, text=True,
                              timeout=10, check=False)

    def test_clean_committed_range_passes(self):
        run = self.check(self.base, self.commit("clean change\n"))
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_push_range_includes_earlier_commits(self):
        self.commit("trailing spaces  \n")
        self.git("commit", "--allow-empty", "-qm", "Second push commit")
        self.assertEqual(self.git("status", "--porcelain"), "")
        run = self.check(self.base, self.git("rev-parse", "HEAD"))
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("trailing whitespace", run.stdout)

    def test_pr_head_checked_even_if_another_tree_is_checked_out(self):
        head = self.commit("trailing spaces  \n")
        self.git("checkout", "-q", self.base)
        run = self.check(self.base, head)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("trailing whitespace", run.stdout)

    def test_first_push_and_manual_run_check_entire_candidate(self):
        for base in ("0" * 40, ""):
            with self.subTest(base=base):
                clean = self.check(base, self.base)
                self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
                head = self.commit(f"trailing spaces {base}  \n")
                run = self.check(base, head)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn("trailing whitespace", run.stdout)

    def test_unavailable_base_does_not_silently_pass(self):
        run = self.check("f" * 40, self.base)
        self.assertNotEqual(run.returncode, 0)


if __name__ == "__main__":
    unittest.main()
