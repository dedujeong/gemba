import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "story-map", "scripts")
sys.path.insert(0, SCRIPTS)

import card_story_map  # noqa: E402
import read_story_map  # noqa: E402
from test_build_story_map import GRAY  # noqa: E402
from test_move_story_map import SPEC_3, board, sticky  # noqa: E402

SITE = "https://deducoder.atlassian.net"
KEYS = {"Save a date per customer": "GEMBA-1", "Send a WhatsApp reminder": "GEMBA-2"}


def numbered(svg):
    """{line number: text} of a board as getConfluenceContent returns it."""
    return {int(m.group(1)): m.group(2) for m in (re.match(r"(\d+)(.*)$", l) for l in svg.splitlines()) if m}


def apply(svg, patch):
    """Do what updateConfluenceContent does with delete_svg and replace_svg: remove the lines of the deletes, and put
    what a replace carries where its lines were. The result is the board without line numbers."""
    lines = numbered(svg)
    for m in re.finditer(r'<delete_svg from="(\d+)" to="(\d+)"\s*/>', patch):
        for n in range(int(m.group(1)), int(m.group(2)) + 1):
            lines.pop(n, None)
    for m in re.finditer(r'<replace_svg from="(\d+)" to="(\d+)">\n?(.*?)\n?</replace_svg>', patch, re.S):
        first, last = int(m.group(1)), int(m.group(2))
        for n in range(first, last + 1):
            lines.pop(n, None)
        lines[first] = m.group(3)
    return "\n".join(f"{n}  {lines[n]}" for n in sorted(lines))


def cards(svg):
    """The issue cards of a board: {key: (x, y, width, height, fill)}."""
    found = {}
    for m in re.finditer(r"<rect\b[^>]*>", svg):
        a = dict(re.findall(r'([\w:-]+)="([^"]*)"', m.group(0)))
        if a.get("data-type") == "issue":
            found[a["data-smartlink-url"].rsplit("/", 1)[1]] = (float(a["x"]), float(a["y"]), a["width"], a["height"], a["fill"])
    return found


class Rectangles(unittest.TestCase):
    def setUp(self):
        self.svg = board(SPEC_3)
        self.patch = card_story_map.card_patch(self.svg, KEYS, SITE)

    def test_each_story_rectangle_of_the_current_release_becomes_the_card_of_its_issue_in_the_same_place(self):
        found = cards(self.patch)
        self.assertEqual(sorted(found), ["GEMBA-1", "GEMBA-2"])
        for text, key in KEYS.items():
            s = sticky(self.svg, text)
            self.assertEqual(found[key][:4], (s["x"], s["y"], "345", "136.91"), text)

    def test_a_card_points_to_its_issue_in_the_site_of_the_project(self):
        self.assertIn(f'data-smartlink-url="{SITE}/browse/GEMBA-1"', self.patch)
        self.assertIn('data-smartlink-kind="block"', self.patch)

    def test_a_card_is_gray_because_confluence_stores_every_card_gray(self):
        self.assertEqual({v[4] for v in cards(self.patch).values()}, {GRAY})

    def test_the_text_of_a_rectangle_is_deleted_with_it(self):
        after = apply(self.svg, self.patch)
        for text in KEYS:
            self.assertNotIn(f">{text}<", after)

    def test_the_board_reads_each_card_as_a_declared_story(self):
        data = read_story_map.parse(apply(self.svg, self.patch))
        mvp = data["releases"][0]
        self.assertEqual((mvp["declared"], mvp["pending"]), (2, 0))
        self.assertEqual([s["key"] for t in mvp["tasks"] for s in t["stories"] if not s["open"]], ["GEMBA-1", "GEMBA-2"])

    def test_the_other_releases_and_the_open_question_keep_their_rectangles(self):
        after = apply(self.svg, self.patch)
        for text in ["Import dates from the notebook", "Some day", "Who sends it when the owner is away?"]:
            self.assertIn(f">{text}<", after)

    def test_a_key_for_a_text_that_is_not_a_story_of_the_current_release_stops_everything(self):
        for text in ["Import dates from the notebook", "Nope"]:
            with self.assertRaises(ValueError) as ctx:
                card_story_map.card_patch(self.svg, {**KEYS, text: "GEMBA-9"}, SITE)
            self.assertIn(text, str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
