import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "skills", "session-close", "scripts", "ensure_ignored.py")
PATTERN = ".gemba/sessions/"
COMMENT = "Session handoffs written by session-close, one per session"
SECTION = "# " + COMMENT + "\n" + PATTERN + "\n"


def run(content, pattern=PATTERN, comment=COMMENT):
    """Runs the script on a .gitignore with this content (None: the file does not exist) and returns its result."""
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, ".gitignore")
        if content is not None:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(content)
        result = subprocess.run([sys.executable, SCRIPT, path, pattern, comment], capture_output=True, text=True)
        text = None
        if os.path.exists(path):
            with open(path, encoding="utf-8", newline="") as f:
                text = f.read()
        return result, text


class EnsureIgnored(unittest.TestCase):
    def test_a_missing_file_is_created_with_the_comment_and_the_pattern(self):
        result, text = run(None)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(text, SECTION)

    def test_the_section_follows_the_last_one_after_a_blank_line(self):
        before = "# Python bytecode from the scripts and their tests\n__pycache__/\n"
        result, text = run(before)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(text, before + "\n" + SECTION)

    def test_a_last_line_without_a_final_newline_gets_one_and_nothing_else_changes(self):
        before = "# Results written by claude plugin eval on each run\n**/evals/results/"
        result, text = run(before)
        self.assertEqual(text, before + "\n\n" + SECTION)

    def test_a_pattern_already_there_changes_nothing(self):
        for already in (".gemba/sessions/", ".gemba/sessions"):
            before = "# Mine\n" + already + "\n"
            result, text = run(before)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(text, before)

    def test_a_second_run_changes_nothing(self):
        _, once = run("node_modules/\n")
        _, twice = run(once)
        self.assertEqual(once, twice)

    def test_an_empty_file_gets_the_section_without_a_leading_blank_line(self):
        _, text = run("")
        self.assertEqual(text, SECTION)


if __name__ == "__main__":
    unittest.main()
