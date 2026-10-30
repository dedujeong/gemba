import copy
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "story-map", "scripts")
sys.path.insert(0, SCRIPTS)

import build_story_map  # noqa: E402
import read_story_map  # noqa: E402
from test_build_story_map import SPEC  # noqa: E402


def as_read(svg):
    """Format a board SVG like getConfluenceContent returns it: a line number before each line."""
    lines = svg.replace("><", ">\n<").split("\n")
    return "\n".join(f"{i}  {line}" if i > 1 else f"{i}{line}" for i, line in enumerate(lines, 1))


def board(spec=SPEC):
    return as_read(build_story_map.build(spec))


class Counts(unittest.TestCase):
    def test_counts_stories_per_release_without_open_questions(self):
        counts = read_story_map.parse(board())["releases"]
        self.assertEqual([(r["name"], r["count"], r["open"]) for r in counts],
                         [("MVP", 2, 1), ("Release 2", 1, 0)])

    def test_counts_what_the_board_has_now_not_what_the_spec_said(self):
        grown = copy.deepcopy(SPEC)
        grown["releases"][0]["stories"][0].append({"text": "Added in the review", "traces": "Problem"})
        counts = read_story_map.parse(board(grown))["releases"]
        self.assertEqual(counts[0]["count"], 3)

    def test_reports_the_stories_of_each_release(self):
        counts = read_story_map.parse(board())["releases"]
        texts = [st["text"] for t in counts[0]["tasks"] for st in t["stories"]]
        self.assertIn("Save a date per customer", texts)
        self.assertEqual([st["text"] for t in counts[1]["tasks"] for st in t["stories"]], ["Import dates from the notebook"])


class Change(unittest.TestCase):
    def test_change_is_signed_against_the_previous_count(self):
        board_now = read_story_map.parse(board())
        self.assertEqual(read_story_map.change(board_now, 1), 1)
        self.assertEqual(read_story_map.change(board_now, 2), 0)
        self.assertEqual(read_story_map.change(board_now, 5), -3)


class OpenQuestionColors(unittest.TestCase):
    def test_the_light_red_the_palette_snaps_to_is_an_open_question(self):
        light = board().replace("#ffd5d2", "#ffeceb")
        mvp = read_story_map.parse(light)["releases"][0]
        self.assertEqual((mvp["count"], mvp["open"]), (2, 1))


class CommandLine(unittest.TestCase):
    def run_cli(self, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "board.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(board())
            return subprocess.run(
                [sys.executable, "-I", os.path.join(SCRIPTS, "read_story_map.py"), path, *extra],
                capture_output=True, text=True, check=True).stdout

    def test_prints_the_count_per_release(self):
        out = self.run_cli()
        self.assertIn("MVP: 2 stories, 1 open question", out)
        self.assertIn("Release 2: 1 story, 0 open questions", out)

    def test_says_the_first_release_grew(self):
        self.assertIn("MVP grew by 1 (was 1, now 2)", self.run_cli("--previous", "1"))

    def test_says_the_first_release_shrank(self):
        self.assertIn("MVP shrank by 3 (was 5, now 2)", self.run_cli("--previous", "5"))

    def test_says_the_first_release_stayed(self):
        self.assertIn("MVP stayed the same (was 2, now 2)", self.run_cli("--previous", "2"))


if __name__ == "__main__":
    unittest.main()
