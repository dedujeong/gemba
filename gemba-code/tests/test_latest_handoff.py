import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "skills", "session-start", "scripts", "latest_handoff.py")


def git(folder, *args):
    subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", *args],
                   cwd=folder, check=True, capture_output=True)


def write(folder, relative, text="# Session\n"):
    path = os.path.join(folder, relative)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def latest(folder):
    result = subprocess.run([sys.executable, SCRIPT], cwd=folder, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr


class LatestHandoff(unittest.TestCase):
    def setUp(self):
        self.project = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(subprocess.run, ["rm", "-rf", self.project])
        git(self.project, "init", "-q")
        git(self.project, "commit", "-q", "--allow-empty", "-m", "Initial commit")

    def test_the_most_recent_handoff_is_the_one_found(self):
        write(self.project, ".gemba/sessions/2026-11-01T09-00-00.md")
        newest = write(self.project, ".gemba/sessions/2026-11-01T17-55-03.md")
        write(self.project, ".gemba/sessions/2026-10-31T23-59-59.md")
        code, out, err = latest(self.project)
        self.assertEqual(code, 0, err)
        self.assertEqual(out, newest)

    def test_a_project_without_handoffs_prints_nothing(self):
        self.assertEqual(latest(self.project)[:2], (0, ""))
        os.makedirs(os.path.join(self.project, ".gemba", "sessions"))
        self.assertEqual(latest(self.project)[:2], (0, ""))

    def test_files_that_are_not_handoffs_are_ignored(self):
        write(self.project, ".gemba/sessions/2026-11-01T17-55-03.txt")
        write(self.project, ".gemba/sessions/notes")
        self.assertEqual(latest(self.project)[:2], (0, ""))

    def test_the_handoff_of_the_main_working_tree_is_found_from_a_linked_worktree(self):
        handoff = write(self.project, ".gemba/sessions/2026-11-01T17-55-03.md")
        worktree = os.path.join(self.project, ".claude", "worktrees", "spike")
        git(self.project, "worktree", "add", "-q", "-b", "spike/x", worktree)
        code, out, err = latest(worktree)
        self.assertEqual(code, 0, err)
        self.assertEqual(out, handoff)

    def test_a_folder_that_is_not_a_repository_still_works(self):
        folder = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(subprocess.run, ["rm", "-rf", folder])
        handoff = write(folder, ".gemba/sessions/2026-11-01T17-55-03.md")
        self.assertEqual(latest(folder)[:2], (0, handoff))


class SessionStartSkill(unittest.TestCase):
    def skill(self):
        with open(os.path.join(ROOT, "skills", "session-start", "SKILL.md"), encoding="utf-8") as f:
            return f.read()

    def test_the_skill_is_named_session_start(self):
        self.assertIn("name: session-start", self.skill())

    def test_the_skill_finds_and_reads_the_latest_handoff(self):
        text = self.skill()
        self.assertIn("scripts/latest_handoff.py", text)
        self.assertIn("Read", text)

    def test_the_skill_checks_the_handoff_against_jira_and_the_code(self):
        text = self.skill()
        self.assertIn("getJiraIssue", text)
        self.assertIn("git status", text)

    def test_the_skill_proposes_the_next_step_as_one_option_and_waits(self):
        text = self.skill()
        self.assertIn("Next step", text)
        self.assertIn("one option", text)
        self.assertIn("wait", text.lower())
        self.assertIn("not an instruction", text)

    def test_without_a_handoff_the_skill_says_so_and_proposes_nothing(self):
        self.assertIn("no handoff", self.skill().lower())


if __name__ == "__main__":
    unittest.main()
