import copy
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "story-map", "scripts")
sys.path.insert(0, SCRIPTS)

import build_story_map  # noqa: E402
import move_story_map  # noqa: E402
import read_story_map  # noqa: E402
from test_build_story_map import SPEC  # noqa: E402
from test_read_story_map import arranged_by_hand, as_read  # noqa: E402

ROW_STEP, GAP = build_story_map.ROW_STEP, build_story_map.RELEASE_GAP

SPEC_3 = copy.deepcopy(SPEC)
SPEC_3["releases"].append({"name": "Later", "description": "Not assigned yet.", "stories": [["Some day"], []]})


def stored(svg):
    """The board as Confluence stores it: a label's y is its top, not the center the builder writes."""
    def top(m):
        text = m.group(0)
        if 'data-type="text"' not in text or "board-header" in text:
            return text
        description = re.findall(r"<tspan[^>]*>([^<]*)</tspan>", text)[-1]
        y = float(re.search(r' y="([-\d.]+)"', text).group(1)) - build_story_map.label_height(description) / 2
        return re.sub(r' y="[-\d.]+"', f' y="{round(y, 2)}"', text, count=1)
    return re.sub(r"<text\b[^>]*data-type=\"text\".*?</text>", top, svg, flags=re.S)


def board(spec=SPEC_3, hand=False):
    svg = stored(build_story_map.build(spec))
    return as_read(arranged_by_hand(svg) if hand else svg)


def sticky(svg, text):
    """The sticky with this text, as the reader sees it."""
    _, bands = read_story_map.read_bands(svg)
    return next(s for stickies in bands.values() for s in stickies if s["text"] == text)


def moves(patch):
    """{id: (x, y)} of every update_elements_svg in the patch."""
    return {m.group(1): (float(m.group(2)), float(m.group(3)))
            for m in re.finditer(r'<update_elements_svg ids="([^"]+)">\s*<attr x="([-\d.]+)" y="([-\d.]+)"\s*/>', patch)}


def label_tops(patch):
    """{name: top} the replace_svg ops of the patch ask for, with the top as label_story_map computes it."""
    out = {}
    for m in re.finditer(r"<replace_svg.*?</replace_svg>", patch, re.S):
        text = m.group(0)
        name = re.search(r'font-size="27px"[^>]*>([^<]*)<', text).group(1)
        y = float(re.search(r' y="([-\d.]+)"', text).group(1))
        description = re.findall(r"<tspan[^>]*>([^<]*)</tspan>", text)[-1]
        out[name] = round(y - build_story_map.label_height(description) / 2, 2)
    return out


def first_top(svg, name):
    return min(s["y"] for s in read_story_map.read_bands(svg)[1][name])


class Placement(unittest.TestCase):
    def test_an_empty_cell_takes_the_first_row_of_the_target_at_the_same_column(self):
        svg = board()
        story = sticky(svg, "Send a WhatsApp reminder")  # the second task's column; Release 2 has nothing there
        patch = move_story_map.move_patch(svg, [story["id"]], "Release 2")
        self.assertEqual(moves(patch), {story["id"]: (story["x"], first_top(svg, "Release 2"))})

    def test_a_cell_with_stories_takes_the_next_row_below_them(self):
        svg = board()
        story, below = sticky(svg, "Save a date per customer"), sticky(svg, "Import dates from the notebook")
        patch = move_story_map.move_patch(svg, [story["id"]], "Release 2")
        self.assertEqual(moves(patch)[story["id"]], (below["x"], round(below["y"] + ROW_STEP, 2)))

    def test_a_row_without_stickies_takes_the_top_of_its_label(self):
        spec = copy.deepcopy(SPEC_3)
        spec["releases"][2]["stories"] = [[], []]
        svg = board(spec)
        story = sticky(svg, "Import dates from the notebook")
        labels, _ = read_story_map.read_bands(svg)
        later = next(l for l in labels if l["name"] == "Later")
        self.assertEqual(moves(move_story_map.move_patch(svg, [story["id"]], "Later"))[story["id"]], (story["x"], later["y"]))

    def test_several_stories_into_one_empty_cell_stack_one_below_the_other(self):
        svg = board()
        a, b = sticky(svg, "Send a WhatsApp reminder"), sticky(svg, "Who sends it when the owner is away?")
        got = moves(move_story_map.move_patch(svg, [a["id"], b["id"]], "Release 2"))
        top = first_top(svg, "Release 2")
        self.assertEqual((got[a["id"]][1], got[b["id"]][1]), (top, round(top + ROW_STEP, 2)))

    def test_a_board_arranged_by_hand_stacks_from_where_the_stickies_are_now(self):
        svg = board(hand=True)
        story, below = sticky(svg, "Save a date per customer"), sticky(svg, "Import dates from the notebook")
        got = moves(move_story_map.move_patch(svg, [story["id"]], "Release 2"))[story["id"]]
        self.assertEqual(got, (below["x"], round(below["y"] + ROW_STEP, 2)))


class RowsBelow(unittest.TestCase):
    def test_nothing_else_moves_when_the_target_has_room(self):
        svg = board()
        story = sticky(svg, "Send a WhatsApp reminder")
        patch = move_story_map.move_patch(svg, [story["id"]], "Release 2")
        self.assertEqual(list(moves(patch)), [story["id"]])
        self.assertNotIn("<replace_svg", patch)

    def test_a_deeper_stack_pushes_the_rows_below_down_and_keeps_the_builder_spacing(self):
        svg = board()
        story, later = sticky(svg, "Save a date per customer"), sticky(svg, "Some day")
        before = first_top(svg, "Later")
        patch = move_story_map.move_patch(svg, [story["id"]], "Release 2")
        got = moves(patch)
        self.assertEqual(got[later["id"]], (later["x"], round(later["y"] + ROW_STEP, 2)))
        self.assertEqual(label_tops(patch), {"Later": round(before + ROW_STEP, 2)})
        self.assertEqual(sorted(got), sorted([story["id"], later["id"]]))  # no sticky above the target is touched

    def test_the_push_is_only_what_is_missing_on_a_board_with_extra_room(self):
        svg = board()
        later = sticky(svg, "Some day")
        extra = 500
        roomy = re.sub(rf'(id="{later["id"]}" data-type="sticky" fill="#\w+" x="[-\d.]+" y=")([-\d.]+)',
                       lambda m: f"{m.group(1)}{float(m.group(2)) + extra}", svg)
        story = sticky(roomy, "Save a date per customer")
        self.assertNotIn(later["id"], moves(move_story_map.move_patch(roomy, [story["id"]], "Release 2")))

    def test_every_row_below_moves_by_the_same_distance(self):
        spec = copy.deepcopy(SPEC_3)
        spec["releases"].insert(2, {"name": "Release 3", "description": "Even later.", "stories": [["Print the labels"], []]})
        svg = board(spec)
        story = sticky(svg, "Save a date per customer")
        patch = move_story_map.move_patch(svg, [story["id"]], "Release 2")
        got = moves(patch)
        for text in ("Print the labels", "Some day"):
            s = sticky(svg, text)
            self.assertEqual(got[s["id"]][1], round(s["y"] + ROW_STEP, 2), text)
        self.assertEqual(set(label_tops(patch)), {"Release 3", "Later"})


class Shapes(unittest.TestCase):
    def test_a_story_listed_twice_is_an_error_not_a_second_slot(self):
        story = sticky(board(), "Send a WhatsApp reminder")
        with self.assertRaises(ValueError) as ctx:
            move_story_map.move_patch(board(), [story["id"], story["id"]], "Release 2")
        self.assertIn("twice", str(ctx.exception))

    def test_a_sticky_of_the_backbone_cannot_be_moved_into_a_release(self):
        task = sticky(board(), "Send the reminder")
        with self.assertRaises(ValueError) as ctx:
            move_story_map.move_patch(board(), [task["id"]], "Release 2")
        self.assertIn("Send the reminder", str(ctx.exception))

    def test_a_neighbour_that_overlaps_the_column_counts_as_the_stack(self):
        svg = board()
        below = sticky(svg, "Import dates from the notebook")
        shifted = re.sub(rf'(id="{below["id"]}" data-type="sticky" fill="#\w+" x=")([-\d.]+)',
                         lambda m: f"{m.group(1)}{float(m.group(2)) + 130}", svg)
        story = sticky(shifted, "Save a date per customer")
        y = moves(move_story_map.move_patch(shifted, [story["id"]], "Release 2"))[story["id"]][1]
        self.assertEqual(y, round(below["y"] + ROW_STEP, 2))

    def test_stickies_that_leave_a_row_below_no_longer_decide_how_far_the_rows_move(self):
        spec = copy.deepcopy(SPEC_3)
        spec["releases"][1]["stories"] = [["Import dates from the notebook", "Print the labels", "Export the dates"], []]
        svg = board(spec)
        ids = [sticky(svg, t)["id"] for t in ("Import dates from the notebook", "Print the labels")]
        # Two stories go up into the MVP's first column; the row they left still starts at its third story.
        patch = move_story_map.move_patch(svg, ids, "MVP")
        self.assertEqual(sorted(moves(patch)), sorted(ids))
        self.assertNotIn("<replace_svg", patch)


class Errors(unittest.TestCase):
    def test_an_unknown_sticky_is_an_error_naming_it(self):
        with self.assertRaises(ValueError) as ctx:
            move_story_map.move_patch(board(), ["nope"], "Release 2")
        self.assertIn("nope", str(ctx.exception))

    def test_an_unknown_release_is_an_error_naming_the_real_ones(self):
        story = sticky(board(), "Some day")
        with self.assertRaises(ValueError) as ctx:
            move_story_map.move_patch(board(), [story["id"]], "Release 9")
        self.assertIn("Release 9", str(ctx.exception))
        self.assertIn("Release 2", str(ctx.exception))

    def test_a_row_of_the_backbone_is_not_a_place_for_a_story(self):
        story = sticky(board(), "Some day")
        with self.assertRaises(ValueError):
            move_story_map.move_patch(board(), [story["id"]], "Tasks")

    def test_moving_a_story_to_the_row_it_is_already_in_is_an_error(self):
        story = sticky(board(), "Some day")
        with self.assertRaises(ValueError) as ctx:
            move_story_map.move_patch(board(), [story["id"]], "Later")
        self.assertIn("already", str(ctx.exception))


class CommandLine(unittest.TestCase):
    def run_cli(self, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "board.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(board())
            return subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "move_story_map.py"), path, *extra],
                                  capture_output=True, text=True)

    def test_prints_the_patch(self):
        story = sticky(board(), "Send a WhatsApp reminder")
        run = self.run_cli("--story", story["id"], "--to", "Release 2")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("<update_elements_svg", run.stdout)

    def test_an_unknown_sticky_fails_with_a_message_not_a_traceback(self):
        run = self.run_cli("--story", "nope", "--to", "Release 2")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("nope", run.stderr)
        self.assertNotIn("Traceback", run.stderr)


if __name__ == "__main__":
    unittest.main()
