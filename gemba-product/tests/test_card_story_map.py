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
import move_story_map  # noqa: E402
import read_story_map  # noqa: E402
from test_build_story_map import GRAY, OPEN  # noqa: E402
from test_move_story_map import SPEC_3, board, sticky  # noqa: E402

SITE = "https://deducoder.atlassian.net"
KEYS = {"Save a date per customer": "GEMBA-1", "Send a WhatsApp reminder": "GEMBA-2"}


def numbered(svg):
    """{line number: text} of a board as getConfluenceContent returns it."""
    return {int(m.group(1)): m.group(2) for m in (re.match(r"(\d+)(.*)$", l) for l in svg.splitlines()) if m}


def apply(svg, patch):
    """Do what updateConfluenceContent does with delete_svg, replace_svg and the moves of update_elements_svg: remove the
    lines of the deletes, put what a replace carries where its lines were, and set the x and y of the elements moved.
    The result is the board with line numbers."""
    lines = numbered(svg)
    for m in re.finditer(r'<delete_svg from="(\d+)" to="(\d+)"\s*/>', patch):
        for n in range(int(m.group(1)), int(m.group(2)) + 1):
            lines.pop(n, None)
    for m in re.finditer(r'<replace_svg from="(\d+)" to="(\d+)">\n?(.*?)\n?</replace_svg>', patch, re.S):
        first, last = int(m.group(1)), int(m.group(2))
        for n in range(first, last + 1):
            lines.pop(n, None)
        lines[first] = m.group(3)
    for m in re.finditer(r'<update_elements_svg ids="([^"]+)">\s*<attr x="([-\d.]+)" y="([-\d.]+)"\s*/>', patch):
        for n, body in lines.items():
            if f'id="{m.group(1)}"' in body and "<rect" in body:
                lines[n] = re.sub(r' x="[-\d.]+" y="[-\d.]+"', f' x="{m.group(2)}" y="{m.group(3)}"', body)
    for m in re.finditer(r'<update_elements_svg ids="([^"]+)">\s*<attr fill="(#\w+)"\s*/>', patch):
        for n, body in lines.items():
            if any(f'id="{sid}"' in body for sid in m.group(1).split(",")) and "<rect" in body:
                lines[n] = re.sub(r' fill="#\w+"', f' fill="{m.group(2)}"', body)
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


QUESTION = "Who sends it when the owner is away?"


class OpenQuestions(unittest.TestCase):
    """A red rectangle is a question nobody decided: it gets no issue, so it does not go with the release being declared."""
    def setUp(self):
        self.svg = board(SPEC_3)
        self.patch = card_story_map.card_patch(self.svg, KEYS, SITE)
        self.after = apply(self.svg, self.patch)

    def test_an_open_question_of_the_current_release_moves_to_the_release_after_it(self):
        releases = {r["name"]: r for r in read_story_map.parse(self.after)["releases"]}
        self.assertEqual((releases["MVP"]["open"], releases["Release 2"]["open"], releases["Later"]["open"]), (0, 1, 0))

    def test_the_question_keeps_its_column_stays_red_and_gets_no_card(self):
        before, after = sticky(self.svg, QUESTION), sticky(self.after, QUESTION)
        self.assertEqual(after["x"], before["x"])
        self.assertGreater(after["y"], before["y"])
        self.assertEqual(after["fill"], OPEN)
        self.assertEqual(sorted(cards(self.after)), ["GEMBA-1", "GEMBA-2"])

    def test_the_question_goes_to_later_when_that_is_the_row_after_the_current_release(self):
        spec = {**SPEC_3, "releases": [SPEC_3["releases"][0], SPEC_3["releases"][2]]}
        svg = board(spec)
        after = apply(svg, card_story_map.card_patch(svg, KEYS, SITE))
        self.assertEqual([(r["name"], r["open"]) for r in read_story_map.parse(after)["releases"]], [("MVP", 0), ("Later", 1)])

    def test_a_question_stays_where_it_is_when_no_row_follows_the_current_release(self):
        spec = {**SPEC_3, "releases": SPEC_3["releases"][:1]}
        svg = board(spec)
        patch = card_story_map.card_patch(svg, KEYS, SITE)
        self.assertNotIn("update_elements_svg", patch)
        self.assertEqual(read_story_map.parse(apply(svg, patch))["releases"][0]["open"], 1)


def fills(svg):
    """{story text: fill} of the story rectangles and stickies of the board, and of nothing else."""
    _, bands = read_story_map.read_bands(svg)
    return {s["text"]: s["fill"] for name, row in bands.items() if name not in read_story_map.BACKBONE for s in row}


class NextReleases(unittest.TestCase):
    """The releases after the one being declared are gray, and the cards in them are always gray."""
    def setUp(self):
        # A board painted the way it was before the gray: the next release orange and the Later row light orange.
        self.svg = board(SPEC_3).replace('fill="#f0f1f2"', 'fill="#fce4a6"')

    def test_the_stories_of_the_next_releases_turn_gray(self):
        after = fills(apply(self.svg, card_story_map.card_patch(self.svg, KEYS, SITE)))
        self.assertEqual((after["Import dates from the notebook"], after["Some day"]), (GRAY, GRAY))

    def test_the_pending_stories_of_the_current_release_and_the_red_questions_keep_their_color(self):
        before = fills(self.svg)
        after = fills(apply(self.svg, card_story_map.card_patch(self.svg, {"Save a date per customer": "GEMBA-1"}, SITE)))
        self.assertEqual(after["Send a WhatsApp reminder"], before["Send a WhatsApp reminder"])
        self.assertEqual(after[QUESTION], OPEN)

    def test_a_board_whose_next_releases_are_already_gray_gets_no_color_change(self):
        patch = card_story_map.card_patch(board(SPEC_3), KEYS, SITE)
        self.assertNotIn("<attr fill=", patch)


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


class MovingCards(unittest.TestCase):
    """A card moves to another column (another task) of its release and keeps its issue."""
    def setUp(self):
        svg = board(SPEC_3)
        self.svg = apply(svg, card_story_map.card_patch(svg, KEYS, SITE))
        _, bands = read_story_map.read_bands(self.svg)
        self.mvp = {s["key"]: s for s in bands["MVP"]}
        self.tasks = {s["text"]: s for s in bands["Tasks"]}

    def test_a_card_moves_to_the_column_of_another_task_in_its_release_below_what_is_there(self):
        first, second = self.mvp["GEMBA-1"], self.mvp["GEMBA-2"]
        patch = move_story_map.move_patch(self.svg, [first["id"]], "MVP", task="Send the reminder")
        self.assertEqual(moves(patch),
                         {first["id"]: (self.tasks["Send the reminder"]["x"], round(second["y"] + move_story_map.ROW_STEP, 2))})

    def test_the_card_keeps_its_issue_because_the_patch_only_changes_its_place(self):
        first = self.mvp["GEMBA-1"]
        patch = move_story_map.move_patch(self.svg, [first["id"]], "MVP", task="Send the reminder")
        self.assertNotIn("replace_svg", patch)
        self.assertNotIn("delete_svg", patch)
        self.assertNotIn("insert_svg", patch)
        after = apply(self.svg, patch)
        self.assertEqual(cards(after)["GEMBA-1"][2:4], ("345", "136.91"))
        self.assertIn(f'data-smartlink-url="{SITE}/browse/GEMBA-1"', after)

    def test_the_board_reads_the_moved_card_in_the_column_of_the_task(self):
        first = self.mvp["GEMBA-1"]
        after = apply(self.svg, move_story_map.move_patch(self.svg, [first["id"]], "MVP", task="Send the reminder"))
        mvp = read_story_map.parse(after)["releases"][0]
        column = next(t for t in mvp["tasks"] if t["task"] == "Send the reminder")
        self.assertEqual([s["key"] for s in column["stories"]], ["GEMBA-2", "GEMBA-1"])

    def test_without_a_task_a_story_still_cannot_move_to_the_release_it_is_in(self):
        with self.assertRaises(ValueError):
            move_story_map.move_patch(self.svg, [self.mvp["GEMBA-1"]["id"]], "MVP")

    def test_an_unknown_task_is_an_error_naming_the_real_ones(self):
        with self.assertRaises(ValueError) as ctx:
            move_story_map.move_patch(self.svg, [self.mvp["GEMBA-1"]["id"]], "MVP", task="Nope")
        self.assertIn("Send the reminder", str(ctx.exception))

    def test_a_card_moves_to_a_task_of_another_release_too(self):
        first = self.mvp["GEMBA-1"]
        patch = move_story_map.move_patch(self.svg, [first["id"]], "Release 2", task="Send the reminder")
        x, _ = moves(patch)[first["id"]]
        self.assertEqual(x, self.tasks["Send the reminder"]["x"])


def moves(patch):
    return {m.group(1): (float(m.group(2)), float(m.group(3)))
            for m in re.finditer(r'<update_elements_svg ids="([^"]+)">\s*<attr x="([-\d.]+)" y="([-\d.]+)"\s*/>', patch)}


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
