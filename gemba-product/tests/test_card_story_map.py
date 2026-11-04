import json
import os
import re
import subprocess
import sys
import tempfile
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


def as_stickies(svg):
    """The same board with its story rectangles drawn as stickies, the way the older boards have them."""
    def swap(m):
        tag = m.group(0)
        if 'data-type="rectangle"' not in tag:
            return tag
        tag = tag.replace('data-type="rectangle"', 'data-type="sticky"')
        return re.sub(r'width="[\d.]+" height="[\d.]+"', 'width="240.05" height="144.03"', tag)
    return re.sub(r"<rect\b[^>]*>", swap, svg)


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


class Stickies(unittest.TestCase):
    def setUp(self):
        self.svg = as_stickies(board(SPEC_3))
        self.patch = card_story_map.card_patch(self.svg, KEYS, SITE)

    def test_each_story_sticky_becomes_the_card_of_its_issue_in_the_same_place(self):
        found = cards(self.patch)
        for text, key in KEYS.items():
            s = sticky(self.svg, text)
            self.assertEqual(found[key][:4], (s["x"], s["y"], "345", "136.91"), text)

    def test_the_board_reads_each_card_as_a_declared_story(self):
        after = apply(self.svg, self.patch)
        for text in KEYS:
            self.assertNotIn(f">{text}<", after)
        mvp = read_story_map.parse(after)["releases"][0]
        self.assertEqual((mvp["declared"], mvp["pending"]), (2, 0))


class MissingCards(unittest.TestCase):
    """A story whose card could not be put stays on the board as it was, and the result names it."""
    def setUp(self):
        self.svg = board(SPEC_3)
        self.first = {"Save a date per customer": "GEMBA-1"}

    def test_a_story_without_a_key_keeps_its_rectangle_and_is_named(self):
        patch = card_story_map.card_patch(self.svg, self.first, SITE)
        self.assertEqual(sorted(cards(patch)), ["GEMBA-1"])
        self.assertIn(">Send a WhatsApp reminder<", apply(self.svg, patch))
        self.assertEqual(card_story_map.without_key(self.svg, self.first), ["Send a WhatsApp reminder"])

    def test_the_check_names_the_story_whose_card_is_still_missing(self):
        after = apply(self.svg, card_story_map.card_patch(self.svg, self.first, SITE))
        self.assertEqual(card_story_map.check(after, KEYS),
                         {"declared": [{"text": "Save a date per customer", "key": "GEMBA-1"}],
                          "pending": [{"text": "Send a WhatsApp reminder", "key": "GEMBA-2"}]})

    def test_the_check_finds_every_card_once_the_release_has_no_pending_story(self):
        after = apply(self.svg, card_story_map.card_patch(self.svg, KEYS, SITE))
        self.assertEqual([d["key"] for d in card_story_map.check(after, KEYS)["declared"]], ["GEMBA-1", "GEMBA-2"])
        self.assertEqual(card_story_map.check(after, KEYS)["pending"], [])


class CommandLine(unittest.TestCase):
    def run_cli(self, svg, keys, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            path, keyfile = os.path.join(tmp, "board.svg"), os.path.join(tmp, "keys.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg)
            with open(keyfile, "w", encoding="utf-8") as f:
                json.dump(keys, f)
            return subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "card_story_map.py"), path, keyfile, "--site", SITE, *extra],
                                  capture_output=True, text=True)

    def test_a_story_without_a_key_is_reported_on_stderr_and_the_patch_still_prints(self):
        run = self.run_cli(board(SPEC_3), {"Save a date per customer": "GEMBA-1"})
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("Without a key: Send a WhatsApp reminder", run.stderr)
        self.assertIn("GEMBA-1", run.stdout)

    def test_check_prints_what_is_declared_and_what_is_pending_as_json(self):
        svg = board(SPEC_3)
        after = apply(svg, card_story_map.card_patch(svg, {"Save a date per customer": "GEMBA-1"}, SITE))
        run = self.run_cli(after, KEYS, "--check")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["pending"], [{"text": "Send a WhatsApp reminder", "key": "GEMBA-2"}])


if __name__ == "__main__":
    unittest.main()
