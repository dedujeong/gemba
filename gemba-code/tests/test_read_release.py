import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "skills", "version-start", "scripts", "read_release.py")
FIXTURES = os.path.join(ROOT, "tests", "fixtures")
# A board as getConfluenceContent returns it: MVP delivered (gray), Release 2 current, Release 3 later.
BOARD = os.path.join(FIXTURES, "story-map-decided.svg")
# The same board with a red sticky in Release 2: an open question.
BOARD_WITH_RED = os.path.join(FIXTURES, "story-map.svg")


def run(board, *args):
    return subprocess.run([sys.executable, SCRIPT, board, *args], capture_output=True, text=True)


def read(*args):
    result = run(BOARD, *args)
    result.check_returncode()
    return result.stdout


def with_story_rectangles(svg, only):
    """The same board with the stories whose text is in `only` drawn as Jira-card rectangles instead of stickies."""
    texts = {m.group(1): m.group(2) for m in re.finditer(r'belongs-to="(\w+)"[^>]*>[\s\d]*<tspan[^>]*>([^<]*)</tspan>', svg)}

    def swap(m):
        tag = m.group(0)
        sid = re.search(r' id="([^"]*)"', tag).group(1)
        if 'data-type="sticky"' not in tag or texts.get(sid) not in only:
            return tag
        tag = tag.replace('data-type="sticky"', 'data-type="rectangle"')
        return re.sub(r'width="[\d.]+" height="[\d.]+"', 'width="345" height="136.91"', tag)

    return re.sub(r"<rect\b[^>]*>", swap, svg)


def write_board(svg):
    board = os.path.join(tempfile.mkdtemp(), "board.svg")
    with open(board, "w", encoding="utf-8") as f:
        f.write(svg)
    return board


class CurrentRelease(unittest.TestCase):
    def setUp(self):
        self.release = json.loads(read("--json"))

    def test_takes_the_first_release_that_is_not_gray(self):
        self.assertEqual(self.release["release"], "Release 2")

    def test_reports_the_value_the_release_delivers_from_its_row_label(self):
        self.assertEqual(self.release["description"], "What the shop owner gets next.")

    def test_groups_its_stories_by_activity_and_task(self):
        self.assertEqual(self.release["stories"], [
            {"activity": "Record a service", "tasks": [
                {"task": "Save the customer", "stories": ["Save the vehicle"]},
                {"task": "Save the next service date", "stories": ["Suggest the date by service type"]},
            ]},
            {"activity": "Remind", "tasks": [
                {"task": "Send the reminder", "stories": ["Remind the day before"]},
            ]},
        ])

    def test_leaves_out_delivered_and_later_releases(self):
        stories = [s for a in self.release["stories"] for t in a["tasks"] for s in t["stories"]]
        for elsewhere in ("Save name and phone", "Today's list", "Weekly summary", "Automatic sending"):
            self.assertNotIn(elsewhere, stories)



class RedStickies(unittest.TestCase):
    def test_fails_naming_the_red_sticky_and_prints_no_release(self):
        result = run(BOARD_WITH_RED)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("Release 2", result.stderr)
        self.assertIn("Who sends it when the owner is away?", result.stderr)

    def test_names_every_red_sticky(self):
        svg = open(BOARD_WITH_RED, encoding="utf-8").read()
        second = (
            '<rect width="240.05" height="144.03" id="s99" data-type="sticky" fill="#ffd5d2" x="1228.5" y="1135"/>\n'
            '<text x="1348.53" y="1207" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s99-text" belongs-to="s99">\n'
            '<tspan font-size="15.47px">Do we charge per message?</tspan>\n</text>\n'
        )
        board = os.path.join(tempfile.mkdtemp(), "two-reds.svg")
        with open(board, "w", encoding="utf-8") as f:
            f.write(svg.replace("</svg>", second + "</svg>"))
        result = run(board, "--json")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("Who sends it when the owner is away?", result.stderr)
        self.assertIn("Do we charge per message?", result.stderr)


RELEASE_2 = {"Save the vehicle", "Suggest the date by service type", "Remind the day before"}
QUESTION = "Who sends it when the owner is away?"


class StoryRectangles(unittest.TestCase):
    """A story drawn as a rectangle of the Jira card counts exactly like a sticky."""

    def setUp(self):
        self.svg = open(BOARD, encoding="utf-8").read()
        self.plain = read("--json")

    def read_with(self, svg, *args):
        return run(write_board(svg), *args)

    def test_a_release_of_rectangles_reads_like_one_of_stickies(self):
        result = self.read_with(with_story_rectangles(self.svg, RELEASE_2), "--json")
        result.check_returncode()
        self.assertEqual(result.stdout, self.plain)

    def test_a_board_with_both_shapes_reads_whole(self):
        mixed = with_story_rectangles(self.svg, {"Save the vehicle", "Remind the day before"})
        result = self.read_with(mixed, "--json")
        result.check_returncode()
        self.assertEqual(result.stdout, self.plain)

    def test_a_red_rectangle_is_an_open_question_not_a_story(self):
        red = open(BOARD_WITH_RED, encoding="utf-8").read()
        for fill in ("#ffd5d2", "#ffeceb"):
            board = with_story_rectangles(red.replace("#ffd5d2", fill), RELEASE_2 | {QUESTION})
            result = self.read_with(board, "--json")
            self.assertNotEqual(result.returncode, 0, fill)
            self.assertEqual(result.stdout, "")
            self.assertIn(QUESTION, result.stderr)


class Markdown(unittest.TestCase):
    def test_prints_the_release(self):
        out = read()
        self.assertTrue(out.startswith("## Release 2"))
        self.assertIn("What the shop owner gets next.", out)
        self.assertIn("### Remind\n- **Send the reminder**\n  - Remind the day before", out)


if __name__ == "__main__":
    unittest.main()
