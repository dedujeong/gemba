import copy
import os
import xml.etree.ElementTree as ET
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "story-map", "scripts")
sys.path.insert(0, SCRIPTS)

import build_story_map  # noqa: E402
import label_story_map  # noqa: E402
from test_build_story_map import SPEC  # noqa: E402
from test_read_story_map import arranged_by_hand, as_read  # noqa: E402

SPEC_3 = copy.deepcopy(SPEC)
SPEC_3["releases"].append({"name": "Later", "description": "Not assigned yet.", "stories": [["Some day"], []]})

SHORT = "Smaller scope."
LONG = "The scope grew with the second round of interviews and the pricing rules."  # two lines at 42 characters


def board(spec=SPEC_3, hand=False):
    svg = build_story_map.build(spec)
    return as_read(arranged_by_hand(svg) if hand else svg)


def first_row_y(svg, texts):
    """The y of the first row of stickies whose text is in `texts`."""
    ys = {m.group(1): float(m.group(2)) for m in re.finditer(r'id="(s\d+)" data-type="sticky" fill="#\w+" x="[-\d.]+" y="([-\d.]+)"', svg)}
    owners = {m.group(1): m.group(2) for m in re.finditer(r'belongs-to="(s\d+)"><tspan[^>]*>([^<]*)</tspan>', svg)}
    return min(ys[sid] for sid, text in owners.items() if text in texts)


def patched_text(patch):
    return re.search(r"<text\b.*</text>", patch, re.S).group(0)


def top_of(patch):
    """The top the patch asks for: its y minus half the height of a label with that description."""
    text = patched_text(patch)
    y = float(re.search(r' y="([-\d.]+)"', text).group(1))
    description = re.findall(r"<tspan[^>]*>([^<]*)</tspan>", text)[-1]
    description = "" if "27px" in text.split(description)[0].split("<tspan")[-1] else description
    return round(y - build_story_map.label_height(description) / 2, 2)


class Replace(unittest.TestCase):
    def test_the_new_text_is_level_with_the_first_row_of_its_release(self):
        svg = board()
        patch = label_story_map.replace_patch(svg, "Release 2", SHORT)
        self.assertEqual(top_of(patch), first_row_y(build_story_map.build(SPEC_3), ["Import dates from the notebook"]))

    def test_y_is_the_top_plus_half_the_height_of_one_or_two_lines(self):
        svg, top = board(), first_row_y(build_story_map.build(SPEC_3), ["Import dates from the notebook"])
        one = float(re.search(r' y="([-\d.]+)"', label_story_map.replace_patch(svg, "Release 2", SHORT)).group(1))
        two = float(re.search(r' y="([-\d.]+)"', label_story_map.replace_patch(svg, "Release 2", LONG)).group(1))
        self.assertEqual((round(one - top, 2), round(two - top, 2)), (51, 62))

    def test_a_board_arranged_by_hand_aligns_to_the_row_where_it_is_now(self):
        moved = build_story_map.build(SPEC_3)
        moved = arranged_by_hand(moved)
        patch = label_story_map.replace_patch(board(hand=True), "Release 2", SHORT)
        self.assertEqual(top_of(patch), first_row_y(moved, ["Import dates from the notebook"]))

    def test_the_patch_replaces_only_the_lines_of_that_label(self):
        svg = board()
        patch = label_story_map.replace_patch(svg, "Release 2", SHORT)
        first, last = map(int, re.search(r'<replace_svg from="(\d+)" to="(\d+)">', patch).groups())
        lines = {int(m.group(1)): m.group(2) for m in re.finditer(r"(?m)^(\d+)\s*(.*)$", svg)}
        self.assertIn('id="label-release-1"', lines[first])
        self.assertTrue(lines[last].strip().endswith("</text>"))
        self.assertNotIn("<rect", "".join(lines[n] for n in range(first, last + 1)))
        self.assertEqual(patch.count("<replace_svg"), 1)
        self.assertNotIn("data-type=\"sticky\"", patch)
        self.assertEqual(patch.count("<text"), 1)

    def test_the_label_keeps_its_own_id_x_and_width(self):
        svg = board().replace('id="label-release-1"', 'id="label-release-1" data-keep="1"')
        svg = re.sub(r'(<text x=")[-\d.]+(" y="[-\d.]+" width=")[\d.]+(" [^>]*id="label-release-1")', r"\g<1>-20.5\g<2>400\g<3>", svg)
        text = patched_text(label_story_map.replace_patch(svg, "Release 2", SHORT))
        self.assertIn('x="-20.5"', text)
        self.assertIn('width="400"', text)
        self.assertIn('id="label-release-1"', text)

    def test_the_font_scale_is_written_like_the_builder_writes_it(self):
        text = patched_text(label_story_map.replace_patch(board(), "Release 2", SHORT))
        self.assertIn('font-scale="1"', text)

    def test_without_a_description_the_label_keeps_its_text_and_only_realigns(self):
        text = patched_text(label_story_map.replace_patch(board(), "Release 2", None))
        self.assertIn("What does not enter the first release.", text)

    def test_an_unknown_label_is_an_error_naming_the_real_ones(self):
        with self.assertRaises(ValueError) as ctx:
            label_story_map.replace_patch(board(), "Release 9", SHORT)
        self.assertIn("Release 9", str(ctx.exception))
        self.assertIn("Release 2", str(ctx.exception))

    def test_a_release_without_stickies_needs_the_top_from_the_person(self):
        spec = copy.deepcopy(SPEC_3)
        spec["releases"][2]["stories"] = [[], []]
        with self.assertRaises(ValueError):
            label_story_map.replace_patch(board(spec), "Later", SHORT)
        patch = label_story_map.replace_patch(board(spec), "Later", SHORT, top=1000)
        self.assertEqual(top_of(patch), 1000)


class Shapes(unittest.TestCase):
    def test_a_label_whose_attributes_are_wrapped_onto_several_lines_is_still_found(self):
        svg = build_story_map.build(SPEC_3).replace('id="label-release-1" data-type="text">', 'id="label-release-1"\ndata-type="text">')
        patch = label_story_map.replace_patch(as_read(svg), "Release 2", SHORT)
        self.assertIn(SHORT, patch)

    def test_two_rows_with_the_same_name_are_an_ambiguity_not_a_guess(self):
        svg = build_story_map.build(SPEC_3).replace(">Later<", ">Release 2<")
        with self.assertRaises(ValueError) as ctx:
            label_story_map.replace_patch(as_read(svg), "Release 2", SHORT)
        self.assertIn("More than one row", str(ctx.exception))

    def test_every_row_aligns_to_its_own_first_row_when_each_was_moved_a_different_distance(self):
        svg = build_story_map.build(SPEC_3)
        owners = {m.group(2): m.group(1) for m in re.finditer(r'belongs-to="(s\d+)"><tspan[^>]*>([^<]*)</tspan>', svg)}
        rows = {"MVP": (13, ["Save a date per customer", "Send a WhatsApp reminder", "Who sends it when the owner is away?"]),
                "Release 2": (37, ["Import dates from the notebook"]), "Later": (91, ["Some day"])}
        moves = {text: dy for dy, texts in rows.values() for text in texts}
        for text, dy in moves.items():
            sid = owners[text]
            svg = re.sub(rf'(id="{sid}" data-type="sticky" fill="#\w+" x="[-\d.]+" y=")([-\d.]+)',
                         lambda m: f"{m.group(1)}{float(m.group(2)) + dy}", svg)
        original = build_story_map.build(SPEC_3)
        for name, (dy, texts) in rows.items():
            self.assertEqual(top_of(label_story_map.replace_patch(as_read(svg), name, SHORT)),
                             round(first_row_y(original, texts) + dy, 2), name)

    def test_three_lines_add_73(self):
        top = first_row_y(build_story_map.build(SPEC_3), ["Import dates from the notebook"])
        patch = label_story_map.replace_patch(board(), "Release 2", "x" * 100)
        self.assertEqual(round(float(re.search(r' y="([-\d.]+)"', patch).group(1)) - top, 2), 73)

    def test_text_that_needs_escaping_still_makes_a_valid_element(self):
        patch = label_story_map.replace_patch(board(), "Release 2", 'Tom & "Jerry" <b>')
        text = ET.fromstring(patched_text(patch))
        self.assertIn('Tom & "Jerry" <b>', "".join(text.itertext()))


class Insert(unittest.TestCase):
    def test_a_new_label_lands_next_to_the_row_it_is_given(self):
        patch = label_story_map.insert_patch(board(), "Release 3", SHORT, top=2500)
        self.assertEqual(top_of(patch), 2500)
        self.assertIn(">Release 3<", patch)
        self.assertEqual(patch.count("<insert_svg"), 1)

    def test_it_is_inserted_after_the_last_element_of_the_board(self):
        svg = board()
        patch = label_story_map.insert_patch(svg, "Release 3", SHORT, top=2500)
        line = int(re.search(r'<insert_svg line="(\d+)">', patch).group(1))
        closing = max(int(m.group(1)) for m in re.finditer(r"(?m)^(\d+)\s*</svg>", svg))
        self.assertEqual(line, closing)

    def test_the_new_id_never_collides_with_one_the_builder_gave(self):
        ids = set(re.findall(r'id="([^"]+)"', board()))
        patch = label_story_map.insert_patch(board(), "Release 1", SHORT, top=2500)
        self.assertNotIn(re.search(r'id="([^"]+)"', patch).group(1), ids)

    def test_a_name_already_on_the_board_is_an_error(self):
        with self.assertRaises(ValueError):
            label_story_map.insert_patch(board(), "Release 2", SHORT, top=2500)


class CommandLine(unittest.TestCase):
    def run_cli(self, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "board.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(board())
            return subprocess.run(
                [sys.executable, "-I", os.path.join(SCRIPTS, "label_story_map.py"), path, *extra],
                capture_output=True, text=True)

    def test_label_prints_the_replace_patch(self):
        run = self.run_cli("--label", "Release 2", "--description", SHORT)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("<replace_svg", run.stdout)

    def test_add_prints_the_insert_patch(self):
        run = self.run_cli("--add", "Release 3", "--description", SHORT, "--top", "2500")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("<insert_svg", run.stdout)

    def test_an_unknown_label_fails_with_a_message_not_a_traceback(self):
        run = self.run_cli("--label", "Nope")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("Release 2", run.stderr)
        self.assertNotIn("Traceback", run.stderr)

    def test_add_without_top_is_a_usage_error(self):
        run = self.run_cli("--add", "Release 3")
        self.assertNotEqual(run.returncode, 0)
        self.assertNotIn("Traceback", run.stderr)


if __name__ == "__main__":
    unittest.main()
