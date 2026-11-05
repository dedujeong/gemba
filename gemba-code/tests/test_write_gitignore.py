import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "skills", "setup", "scripts", "write_gitignore.py")

PERSONAL = "# Personal Claude Code files, one set per developer\n.claude/settings.local.json\nCLAUDE.local.md\n"
WORKTREES = "# Claude Code worktrees, used for Spikes\n.claude/worktrees/\n"
SESSIONS = "# Session handoffs written by session-close, one per session\n.gemba/sessions/\n"
BASE = PERSONAL + "\n" + WORKTREES + "\n" + SESSIONS


def run(content):
    """Runs the script on a .gitignore with this content (None: the file does not exist)."""
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, ".gitignore")
        if content is not None:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(content)
        result = subprocess.run([sys.executable, SCRIPT, path], capture_output=True, text=True)
        text = None
        if os.path.exists(path):
            with open(path, encoding="utf-8", newline="") as f:
                text = f.read()
        return result, text


class WriteTheBaseGitignore(unittest.TestCase):
    def test_a_repo_without_gitignore_gets_the_four_entries_in_three_commented_groups(self):
        result, text = run(None)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(text, BASE)

    def test_only_the_missing_entries_are_added_after_the_ones_already_there(self):
        before = "node_modules/\n\n# Mine\n.claude/worktrees\nCLAUDE.local.md\n"
        result, text = run(before)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(text.startswith(before), text)
        added = text[len(before):]
        self.assertEqual(added, "\n" + "# Personal Claude Code files, one set per developer\n.claude/settings.local.json\n\n" + SESSIONS)

    def test_the_lines_already_there_keep_their_order_and_none_is_deleted(self):
        before = "z-last/\n.gemba/sessions/\na-first/\n"
        _, text = run(before)
        self.assertEqual(text.splitlines()[:3], before.splitlines())
        self.assertIn("CLAUDE.local.md", text.splitlines())
        for line in before.splitlines():
            self.assertIn(line, text.splitlines())

    def test_a_gitignore_that_has_everything_changes_nothing(self):
        _, text = run(BASE)
        self.assertEqual(text, BASE)

    def test_a_second_run_changes_nothing(self):
        _, once = run("dist/\n")
        _, twice = run(once)
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
