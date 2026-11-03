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

import add_story_map  # noqa: E402
import build_story_map  # noqa: E402
import read_story_map  # noqa: E402
from test_build_story_map import CURRENT, LATER, NEXT, SPEC, delivered_first  # noqa: E402
from test_move_story_map import SPEC_3, board, first_top, label_tops, moves, sticky  # noqa: E402

ROW_STEP = build_story_map.ROW_STEP


def inserted(patch):
    """The sticky an insert_svg op adds: its line, its rect attributes and its text."""
    op = re.search(r'<insert_svg line="(\d+)">(.*?)</insert_svg>', patch, re.S)
    rect = dict(re.findall(r'([\w:-]+)="([^"]*)"', re.search(r"<rect\b[^>]*>", op.group(2)).group(0)))
    text = re.search(r"(<text\b[^>]*>)(.*?)</text>", op.group(2), re.S)
    return {
        "line": int(op.group(1)),
        "id": rect["id"],
        "x": float(rect["x"]),
        "y": float(rect["y"]),
        "fill": rect["fill"],
        "belongs-to": dict(re.findall(r'([\w:-]+)="([^"]*)"', text.group(1)))["belongs-to"],
        "text": re.search(r"<tspan[^>]*>([^<]*)</tspan>", text.group(2)).group(1),
    }


def applied(svg, patch):
    """The board as it reads once Confluence inserts the new elements at the end."""
    op = re.search(r'<insert_svg line="\d+">(.*?)</insert_svg>', patch, re.S)
    return svg.replace("</svg>", op.group(1).strip() + "\n</svg>")


class Placement(unittest.TestCase):
    def test_puts_the_story_in_the_column_of_its_task_and_the_row_of_its_release(self):
        svg = board()
        patch = add_story_map.add_patch(svg, "Release 2", "Send the reminder", "Editable message templates")
        got, task = inserted(patch), sticky(svg, "Send the reminder")
        self.assertEqual((got["x"], got["y"]), (task["x"], first_top(svg, "Release 2")))

    def test_the_story_takes_the_color_of_the_row_it_lands_in(self):
        svg = board()
        fills = {
            "MVP": add_story_map.add_patch(svg, "MVP", "Send the reminder", "Resend a failed reminder", traces="Problem"),
            "Release 2": add_story_map.add_patch(svg, "Release 2", "Send the reminder", "Editable message templates"),
            "Later": add_story_map.add_patch(svg, "Later", "Send the reminder", "Reminders by email"),
        }
        self.assertEqual({name: inserted(patch)["fill"] for name, patch in fills.items()},
                         {"MVP": CURRENT, "Release 2": NEXT, "Later": LATER})

    def test_the_color_follows_the_board_once_a_release_shipped(self):
        svg = board(delivered_first(SPEC_3))
        patch = add_story_map.add_patch(svg, "Release 2", "Send the reminder", "Editable message templates", traces="Problem")
        self.assertEqual(inserted(patch)["fill"], CURRENT)

    def test_stacks_under_the_stories_already_in_that_column(self):
        svg = board()
        below = sticky(svg, "Who sends it when the owner is away?")
        patch = add_story_map.add_patch(svg, "MVP", "Send the reminder", "Resend a failed reminder", traces="Problem")
        self.assertEqual(inserted(patch)["y"], round(below["y"] + ROW_STEP, 2))

    def test_a_deeper_row_pushes_the_rows_below_down(self):
        svg = board()
        before, later = first_top(svg, "Release 2"), sticky(svg, "Import dates from the notebook")
        patch = add_story_map.add_patch(svg, "MVP", "Send the reminder", "Resend a failed reminder", traces="Problem")
        self.assertEqual(moves(patch)[later["id"]], (later["x"], round(later["y"] + ROW_STEP, 2)))
        self.assertEqual(label_tops(patch)["Release 2"], round(before + ROW_STEP, 2))

    def test_nothing_moves_when_the_row_has_room(self):
        svg = board()
        patch = add_story_map.add_patch(svg, "Release 2", "Send the reminder", "Editable message templates")
        self.assertEqual(moves(patch), {})
        self.assertNotIn("<replace_svg", patch)

    def test_a_board_arranged_by_hand_stacks_from_where_the_stickies_are_now(self):
        svg = board(hand=True)
        below = sticky(svg, "Who sends it when the owner is away?")
        patch = add_story_map.add_patch(svg, "MVP", "Send the reminder", "Resend a failed reminder", traces="Problem")
        self.assertEqual(inserted(patch)["y"], round(below["y"] + ROW_STEP, 2))

    def test_the_sticky_goes_in_at_the_end_of_the_board(self):
        svg = board()
        patch = add_story_map.add_patch(svg, "Release 2", "Send the reminder", "Editable message templates")
        self.assertEqual(inserted(patch)["line"], int(svg.strip().splitlines()[-1].split()[0]))

    def test_the_text_belongs_to_the_new_sticky_and_its_id_is_free(self):
        svg = board()
        got = inserted(add_story_map.add_patch(svg, "Release 2", "Send the reminder", "Editable message templates"))
        self.assertEqual(got["belongs-to"], got["id"])
        self.assertNotIn(f'id="{got["id"]}"', svg)

    def test_the_board_reads_the_story_back_in_its_task_and_its_release(self):
        svg = board()
        patch = add_story_map.add_patch(svg, "Release 2", "Send the reminder", "Editable message templates")
        release = next(r for r in read_story_map.parse(applied(svg, patch))["releases"] if r["name"] == "Release 2")
        task = next(t for t in release["tasks"] if t["task"] == "Send the reminder")
        self.assertEqual([s["text"] for s in task["stories"]], ["Editable message templates"])
        self.assertEqual((release["count"], release["open"]), (2, 0))


class Checks(unittest.TestCase):
    def message(self, *args, **kwargs):
        with self.assertRaises(ValueError) as error:
            add_story_map.add_patch(*args, **kwargs)
        return str(error.exception)

    def test_an_unknown_task_names_the_tasks_of_the_board(self):
        message = self.message(board(), "Release 2", "Charge the service", "Editable message templates")
        self.assertIn("Save the next service date", message)
        self.assertIn("Send the reminder", message)

    def test_an_unknown_release_names_the_rows_of_the_board(self):
        message = self.message(board(), "Release 3", "Send the reminder", "Editable message templates")
        self.assertIn("Release 2", message)
        self.assertIn("Later", message)

    def test_a_story_of_the_current_release_without_traces_is_rejected(self):
        message = self.message(board(), "MVP", "Send the reminder", "Resend a failed reminder")
        self.assertIn("traces", message)

    def test_a_story_of_a_later_release_needs_no_traces(self):
        self.assertIn("<insert_svg", add_story_map.add_patch(board(), "Release 2", "Send the reminder", "Editable message templates"))

    def test_a_delivered_release_takes_no_story(self):
        message = self.message(board(delivered_first(SPEC_3)), "MVP", "Send the reminder", "Resend a failed reminder")
        self.assertIn("delivered", message)


class CommandLine(unittest.TestCase):
    def run_cli(self, *extra, spec=SPEC_3):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "board.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(board(spec))
            return subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "add_story_map.py"), path, *extra],
                                  capture_output=True, text=True)

    def test_prints_the_patch_that_adds_the_story(self):
        done = self.run_cli("--to", "Release 2", "--task", "Send the reminder", "--text", "Editable message templates")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(inserted(done.stdout)["text"], "Editable message templates")

    def test_an_unknown_task_fails_with_its_message(self):
        done = self.run_cli("--to", "Release 2", "--task", "Charge the service", "--text", "Editable message templates")
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("Charge the service", done.stderr)


if __name__ == "__main__":
    unittest.main()
