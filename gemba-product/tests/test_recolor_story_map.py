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
import recolor_story_map  # noqa: E402
from test_build_story_map import CURRENT, LATER, NEXT, OPEN, RELEASED, SPEC, stickies  # noqa: E402
from test_read_story_map import as_read  # noqa: E402

# The scheme before GEMBA-28, keyed by the new fill each sticky has now.
OLD_SCHEME = {
    "#f5e989": "#eed7fc",  # persona: purple
    "#eed7fc": "#baf3db",  # activities: green
    "#baf3db": "#fce4a6",  # current release: orange
    "#fce4a6": "#f0f1f2",  # next release: gray
    "#fff5db": "#f0f1f2",  # later releases: gray
}

SPEC_3 = copy.deepcopy(SPEC)
SPEC_3["releases"].append({"name": "Release 3", "stories": [["Third story"], []]})


SPEC_LATER = copy.deepcopy(SPEC)
SPEC_LATER["releases"].append({"name": "Later", "stories": [["Some day"], []]})


def old_scheme(svg):
    """The same board painted the way it was before the new colors."""
    return re.sub(r'(data-type="sticky" fill=")(#\w+)"', lambda m: f'{m.group(1)}{OLD_SCHEME.get(m.group(2), m.group(2))}"', svg)


def apply(svg, plan):
    """Do what update_elements_svg does: change only the fill of the stickies named."""
    for fill, ids in plan.items():
        for sid in ids:
            svg = re.sub(rf'(id="{sid}" data-type="sticky" fill=")#\w+"', rf'\g<1>{fill}"', svg)
    return svg


class Plan(unittest.TestCase):
    def test_every_sticky_of_an_old_board_goes_to_the_color_of_its_row(self):
        new = build_story_map.build(SPEC_3)
        plan = recolor_story_map.plan(as_read(old_scheme(new)))
        self.assertEqual(apply(old_scheme(new), plan), new)

    def test_only_fills_change_never_text_or_position(self):
        new = build_story_map.build(SPEC_3)
        old = old_scheme(new)
        changed = apply(old, recolor_story_map.plan(as_read(old)))
        self.assertEqual(re.sub(r' fill="#\w+"', "", changed), re.sub(r' fill="#\w+"', "", old))

    def test_a_delivered_release_goes_gray_and_the_next_becomes_current(self):
        old = old_scheme(build_story_map.build(SPEC_3))
        texts = stickies(apply(old, recolor_story_map.plan(as_read(old), released=["MVP"])))
        self.assertEqual(texts["Save a date per customer"], RELEASED)
        self.assertEqual(texts["Import dates from the notebook"], CURRENT)
        self.assertEqual(texts["Third story"], NEXT)
        self.assertEqual(texts["Who sends it when the owner is away?"], OPEN)

    def test_the_later_row_stays_later_whichever_releases_are_delivered(self):
        old = old_scheme(build_story_map.build(SPEC_LATER))
        for released in ([], ["MVP"], ["MVP", "Release 2"]):
            texts = stickies(apply(old, recolor_story_map.plan(as_read(old), released=released)))
            self.assertEqual(texts["Some day"], LATER, released)

    def test_open_questions_stay_red_and_the_light_red_is_normalized(self):
        new = build_story_map.build(SPEC_3)
        light = old_scheme(new).replace("#ffd5d2", "#ffeceb")
        plan = recolor_story_map.plan(as_read(light))
        self.assertEqual(apply(light, plan), new)

    def test_a_board_already_in_the_new_colors_has_nothing_to_change(self):
        self.assertEqual(recolor_story_map.plan(as_read(build_story_map.build(SPEC_3))), {})

    def test_a_board_arranged_by_hand_is_recolored_by_row(self):
        from test_read_story_map import arranged_by_hand
        new = arranged_by_hand(build_story_map.build(SPEC_3))
        self.assertEqual(apply(old_scheme(new), recolor_story_map.plan(as_read(old_scheme(new)))), new)


class UnknownRelease(unittest.TestCase):
    def test_a_delivered_release_that_is_not_on_the_board_is_an_error_naming_the_labels(self):
        board = as_read(old_scheme(build_story_map.build(SPEC_3)))
        for name in ["Nope", "mvp"]:
            with self.assertRaises(ValueError) as ctx:
                recolor_story_map.plan(board, released=[name])
            self.assertIn(name, str(ctx.exception))
            self.assertIn("MVP", str(ctx.exception))


class CommandLine(unittest.TestCase):
    def run_cli(self, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "board.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(as_read(old_scheme(build_story_map.build(SPEC_3))))
            return subprocess.run(
                [sys.executable, "-I", os.path.join(SCRIPTS, "recolor_story_map.py"), path, *extra],
                capture_output=True, text=True)

    def test_prints_the_ids_for_each_color(self):
        out = self.run_cli().stdout
        for fill in ["#f5e989", "#eed7fc", "#baf3db", "#fce4a6", "#fff5db"]:
            self.assertRegex(out, rf'{fill}: ids="s\d+(,s\d+)*"')

    def test_released_option_moves_the_stickies_of_the_named_release_to_gray(self):
        old = old_scheme(build_story_map.build(SPEC_3))
        plan = {fill: ids.split(",") for fill, ids in re.findall(r'(#\w+): ids="([^"]+)"', self.run_cli("--released", "MVP").stdout)}
        texts = stickies(apply(old, plan))
        self.assertEqual(texts["Save a date per customer"], RELEASED)
        self.assertEqual(texts["Import dates from the notebook"], CURRENT)

    def test_an_unknown_release_fails_with_the_labels_instead_of_being_ignored(self):
        run = self.run_cli("--released", "Nope")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("MVP", run.stderr)

    def test_released_without_a_name_is_a_usage_error_not_a_traceback(self):
        run = self.run_cli("--released")
        self.assertNotEqual(run.returncode, 0)
        self.assertNotIn("Traceback", run.stderr)


if __name__ == "__main__":
    unittest.main()
