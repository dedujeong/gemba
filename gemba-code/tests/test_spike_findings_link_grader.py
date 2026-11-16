import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRADER = os.path.join(
    ROOT, "evals", "publishes-the-findings-when-the-test-ends", "graders", "links-the-issue-once.md"
)
TIMEOUT = 3

RUNNER = (
    "import json, re, sys\n"
    "pattern, flags, text = json.load(sys.stdin)\n"
    "print(bool(re.search(pattern, text, re.I if 'i' in flags else 0)))\n"
)


def grader_field(name):
    with open(GRADER, encoding="utf-8") as f:
        match = re.search(r"^%s: '?(.*?)'?$" % name, f.read(), re.M)
    return match.group(1)


def matches(text):
    """Run the grader's regex on the text in a subprocess so a runaway match fails the test instead of hanging it."""
    payload = json.dumps([grader_field("pattern"), grader_field("flags"), text])
    try:
        result = subprocess.run(
            [sys.executable, "-I", "-c", RUNNER],
            input=payload, capture_output=True, text=True, timeout=TIMEOUT, check=True,
        )
    except subprocess.TimeoutExpired:
        raise AssertionError("the grader regex took more than %d s on this text" % TIMEOUT)
    return result.stdout.strip() == "True"


class LinksTheIssueOnceGrader(unittest.TestCase):
    def test_a_link_row_in_the_middle_of_the_table_matches(self):
        text = (
            "| Acción | Herramienta |\n"
            "| Crear | createConfluenceContent TALLER-50 Can we send WhatsApp reminders |\n"
            "| Enlazar | enlace remoto a TALLER-50 |\n"
            "| Cerrar | x |\n"
        )
        self.assertTrue(matches(text))

    def test_a_link_row_as_the_last_line_without_a_final_newline_matches(self):
        text = "| Crear | page TALLER-50 |\n| Vincular | enlace remoto a TALLER-50 |"
        self.assertTrue(matches(text))

    def test_a_long_answer_with_one_link_row_matches(self):
        text = "x\n" * 100 + "| Vincular | link a TALLER-50 |\n" + "y\n" * 100
        self.assertTrue(matches(text))

    def test_a_long_answer_without_a_link_row_does_not_match_and_does_not_hang(self):
        self.assertFalse(matches("x\n" * 40))

    def test_two_lines_that_link_the_issue_do_not_match(self):
        text = "| Enlazar | enlace a TALLER-50 |\nNota: el link de TALLER-50 va una sola vez.\n"
        self.assertFalse(matches(text))


if __name__ == "__main__":
    unittest.main()
