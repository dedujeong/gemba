import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "skills", "version-start", "scripts", "write_keys.py")
# A board as getConfluenceContent returns it: MVP delivered (gray), Release 2 current with an open question, Release 3 later.
BOARD = os.path.join(ROOT, "tests", "fixtures", "story-map.svg")
KEYS = {
    "Save the vehicle": "TALLER-12",
    "Suggest the date by service type": "TALLER-13",
    "Remind the day before": "TALLER-14",
}
KEY_LINE = '<tspan font-size="15.47px" dy="1">{}</tspan>'


def run(board, keys, *args):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(keys, f)
    try:
        return subprocess.run([sys.executable, SCRIPT, board, f.name, *args], capture_output=True, text=True)
    finally:
        os.unlink(f.name)


def with_keys_on_board(*texts):
    """The fixture as it would be read after the keys were written on the given stories."""
    with open(BOARD, encoding="utf-8") as f:
        svg = f.read()
    for text in texts:
        line = f'<tspan font-size="15.47px">{text}</tspan>'
        svg = svg.replace(line, line + KEY_LINE.format(KEYS[text]))
    f = tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False, encoding="utf-8")
    f.write(svg)
    f.close()
    return f.name


class WritesTheKey(unittest.TestCase):
    def setUp(self):
        result = run(BOARD, KEYS)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.patch = result.stdout

    def test_adds_the_key_as_a_last_line_of_the_sticky_text_keeping_the_name(self):
        for text, key in KEYS.items():
            self.assertIn(f'<tspan font-size="15.47px">{text}</tspan>\n    {KEY_LINE.format(key)}\n  </text>', self.patch)

    def test_replaces_only_the_text_of_each_story_of_the_current_release(self):
        ranges = re.findall(r'<replace_svg from="(\d+)" to="(\d+)">', self.patch)
        self.assertEqual(ranges, [("81", "83"), ("85", "87"), ("89", "91")])

    def test_leaves_activities_tasks_the_open_question_and_other_releases_alone(self):
        for untouched in ("Record a service", "Remind", "Save the customer", "Who sends it when the owner is away?",
                          "Save name and phone", "Weekly summary"):
            self.assertNotIn(f">{untouched}</tspan>", self.patch)


class WhatItDoesNotWrite(unittest.TestCase):
    def test_a_story_without_a_key_gets_no_patch_and_is_reported(self):
        result = run(BOARD, {"Save the vehicle": "TALLER-12"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(re.findall(r'<replace_svg from="(\d+)"', result.stdout), ["81"])
        self.assertIn("Without a key: Suggest the date by service type, Remind the day before", result.stderr)

    def test_a_key_for_a_story_that_is_not_in_the_release_fails_naming_it(self):
        result = run(BOARD, {**KEYS, "Weekly summary": "TALLER-20"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Weekly summary", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_a_sticky_that_already_carries_its_key_is_not_written_again(self):
        board = with_keys_on_board("Save the vehicle")
        try:
            result = run(board, KEYS)
        finally:
            os.unlink(board)
        self.assertEqual(re.findall(r'<replace_svg from="(\d+)"', result.stdout), ["85", "89"])


class ChecksTheBoard(unittest.TestCase):
    def check(self, board):
        result = run(board, KEYS, "--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_reports_from_the_board_which_stories_carry_their_key(self):
        board = with_keys_on_board("Save the vehicle", "Suggest the date by service type")
        try:
            report = self.check(board)
        finally:
            os.unlink(board)
        self.assertEqual(report["release"], "Release 2")
        self.assertEqual([(s["text"], s["found"], s["ok"]) for s in report["stories"]], [
            ("Save the vehicle", "TALLER-12", True),
            ("Suggest the date by service type", "TALLER-13", True),
            ("Remind the day before", None, False),
        ])

    def test_a_board_without_keys_reports_none_found(self):
        report = self.check(BOARD)
        self.assertTrue(all(s["found"] is None and not s["ok"] for s in report["stories"]))

    def test_the_story_name_is_the_text_without_the_key(self):
        board = with_keys_on_board("Remind the day before")
        try:
            report = self.check(board)
        finally:
            os.unlink(board)
        self.assertIn("Remind the day before", [s["text"] for s in report["stories"]])


if __name__ == "__main__":
    unittest.main()
