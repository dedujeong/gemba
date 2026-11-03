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
import read_story_map  # noqa: E402
from test_build_story_map import SPEC, delivered_first  # noqa: E402


def as_read(svg):
    """Format a board SVG like getConfluenceContent returns it: a line number before each line."""
    lines = svg.replace("><", ">\n<").split("\n")
    return "\n".join(f"{i}  {line}" if i > 1 else f"{i}{line}" for i, line in enumerate(lines, 1))


def board(spec=SPEC):
    return as_read(build_story_map.build(spec))


def with_story_rectangles(svg, only=None):
    """The same board with its stories (the stickies that are not persona, activities or tasks) drawn as Jira-card rectangles.
    With `only`, just the stories whose text is in it."""
    backbone = {build_story_map.PERSONA, build_story_map.ACTIVITY, build_story_map.TASK}
    texts = {m.group(1): m.group(2) for m in re.finditer(r'belongs-to="(\w+)"[^>]*>[\s\d]*<tspan[^>]*>([^<]*)</tspan>', svg)}
    def swap(m):
        tag = m.group(0)
        fill = re.search(r' fill="([^"]*)"', tag).group(1)
        sid = re.search(r' id="([^"]*)"', tag).group(1)
        if 'data-type="sticky"' not in tag or fill in backbone or (only is not None and texts.get(sid) not in only):
            return tag
        tag = tag.replace('data-type="sticky"', 'data-type="rectangle"')
        return re.sub(r'width="[\d.]+" height="[\d.]+"', 'width="345" height="136.91"', tag)
    return re.sub(r"<rect\b[^>]*>", swap, svg)


class StoryRectangles(unittest.TestCase):
    """A story drawn as a rectangle of the Jira card counts exactly like a sticky."""

    def test_a_board_of_rectangles_reads_like_one_of_stickies(self):
        plain = read_story_map.parse(board())
        self.assertEqual(read_story_map.parse(with_story_rectangles(board())), plain)
        self.assertEqual(plain["releases"][0]["count"], 2)

    def test_a_board_with_both_shapes_reads_the_same(self):
        mixed = with_story_rectangles(board(), only={"Save a date per customer", "Import dates from the notebook"})
        self.assertEqual(read_story_map.parse(mixed), read_story_map.parse(board()))

    def test_a_red_rectangle_is_an_open_question_not_a_story(self):
        mvp = read_story_map.parse(with_story_rectangles(board()))["releases"][0]
        self.assertEqual((mvp["count"], mvp["open"]), (2, 1))
        light = read_story_map.parse(with_story_rectangles(board().replace("#ffd5d2", "#ffeceb")))["releases"][0]
        self.assertEqual((light["count"], light["open"]), (2, 1))


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


class CountsDoNotDependOnTheColorScheme(unittest.TestCase):
    def test_gray_and_red_stickies_count_as_before_the_new_colors(self):
        spec = delivered_first(SPEC)
        spec["releases"][1]["stories"][1] = [{"text": "Still open", "open": True}]
        counts = [(r["name"], r["count"], r["open"]) for r in read_story_map.parse(board(spec))["releases"]]
        self.assertEqual(counts, [("MVP", 1, 0), ("Release 2", 1, 1)])

    def test_the_old_and_the_new_scheme_give_the_same_counts(self):
        new = board()
        # Old scheme: the MVP orange, later releases gray (green was the activities row, which holds no stories).
        old = new.replace("#fce4a6", "#f0f1f2").replace("#baf3db", "#fce4a6")
        def counted(svg):
            return [{k: v for k, v in r.items() if k != "delivered"} for r in read_story_map.parse(svg)["releases"]]
        self.assertEqual(counted(old), counted(new))


def arranged_by_hand(svg):
    """Move every sticky some distance, as a person arranging the board would, without leaving its column and row."""
    def move(m):
        tag = m.group(0)
        if 'data-type="sticky"' not in tag:
            return tag
        tag = re.sub(r' x="([-\d.]+)"', lambda a: f' x="{float(a.group(1)) + 55}"', tag)
        return re.sub(r' y="([-\d.]+)"', lambda a: f' y="{float(a.group(1)) + 30}"', tag)
    return re.sub(r"<rect\b[^>]*>", move, svg)


class ForDevelopment(unittest.TestCase):
    def test_gives_the_mvp_stories_grouped_by_activity_and_task(self):
        mvp = read_story_map.for_development(read_story_map.parse(board()))
        self.assertEqual(mvp["stories"], [
            {"activity": "Record a service", "tasks": [
                {"task": "Save the next service date", "stories": ["Save a date per customer"]}]},
            {"activity": "Remind", "tasks": [
                {"task": "Send the reminder", "stories": ["Send a WhatsApp reminder"]}]},
        ])

    def test_leaves_out_later_releases_and_lists_open_questions_apart(self):
        mvp = read_story_map.for_development(read_story_map.parse(board()))
        self.assertNotIn("Import dates from the notebook", str(mvp["stories"]))
        self.assertEqual(mvp["open_questions"], ["Who sends it when the owner is away?"])

    def test_a_board_arranged_by_hand_gives_the_same_stories(self):
        plain = read_story_map.for_development(read_story_map.parse(board()))
        moved = read_story_map.for_development(read_story_map.parse(as_read(arranged_by_hand(build_story_map.build(SPEC)))))
        self.assertEqual(moved, plain)


class DeliveredReleases(unittest.TestCase):
    """A gray release shipped: it is read as delivered and the scope is the first release that is not."""

    def shipped(self):
        spec = delivered_first(SPEC)
        spec["releases"][1]["stories"] = [[{"text": "Import dates from the notebook", "traces": "Problem"}], [{"text": "Print the labels", "traces": "Problem"}]]
        spec["releases"].append({"name": "Release 3", "description": "Later.", "stories": [["Print the reminders"], []]})
        return spec

    def test_a_gray_release_is_delivered_and_the_next_one_is_not(self):
        releases = read_story_map.parse(board(self.shipped()))["releases"]
        self.assertEqual([(r["name"], r["delivered"]) for r in releases],
                         [("MVP", True), ("Release 2", False), ("Release 3", False)])

    def test_a_board_with_nothing_delivered_marks_none(self):
        self.assertFalse(any(r["delivered"] for r in read_story_map.parse(board())["releases"]))

    def test_the_scope_is_the_first_release_not_delivered(self):
        mvp = read_story_map.for_development(read_story_map.parse(board(self.shipped())))
        self.assertEqual(mvp["release"], "Release 2")
        self.assertIn("Import dates from the notebook", str(mvp["stories"]))
        self.assertNotIn("Delivered story", str(mvp["stories"]))

    def test_growth_is_measured_on_the_current_release(self):
        board_now = read_story_map.parse(board(self.shipped()))
        self.assertEqual(read_story_map.change(board_now, 3), -1)

    def test_the_summary_says_which_releases_were_delivered_and_compares_the_current_one(self):
        out = read_story_map.summary(read_story_map.parse(board(self.shipped())), 2)
        self.assertIn("MVP: 1 story, 0 open questions (delivered)", out)
        self.assertIn("Release 2 stayed the same (was 2, now 2)", out)

    def test_a_release_with_only_open_questions_is_not_delivered(self):
        spec = self.shipped()
        spec["releases"][1]["stories"] = [[{"text": "Still unknown", "open": True}], []]
        self.assertFalse(read_story_map.parse(board(spec))["releases"][1]["delivered"])

    def test_a_release_with_one_gray_story_among_others_is_not_delivered(self):
        svg = board(self.shipped()).replace("#baf3db", "#f0f1f2", 1)  # one story of the current release turns gray
        self.assertFalse(read_story_map.parse(svg)["releases"][1]["delivered"])

    def test_later_is_never_the_current_release(self):
        spec = self.shipped()
        for r in spec["releases"][:3]:
            r["released"] = True
            r["stories"] = [["Done " + r["name"]], []]
        spec["releases"].append({"name": "Later", "description": "Nothing assigned.", "stories": [[{"text": "Some day", "traces": "Problem"}], []]})
        data = read_story_map.parse(board(spec))
        self.assertEqual(read_story_map.for_development(data)["release"], "")
        self.assertNotIn("grew", read_story_map.summary(data, 1))

    def test_every_story_carries_the_id_of_its_sticky_so_it_can_be_moved(self):
        data = read_story_map.parse(board())
        ids = [st["id"] for r in data["releases"] for t in r["tasks"] for st in t["stories"]]
        self.assertEqual(len(ids), 4)
        self.assertTrue(all(ids) and len(set(ids)) == 4)

    def test_when_everything_is_delivered_there_is_no_current_release(self):
        spec = self.shipped()
        for r in spec["releases"]:
            r["released"] = True
            r["stories"] = [["Done " + r["name"]], []]
        data = read_story_map.parse(board(spec))
        self.assertEqual(read_story_map.for_development(data)["release"], "")
        self.assertEqual(read_story_map.change(data, 4), 0)
        self.assertNotIn("grew", read_story_map.summary(data, 4))


class Gaps(unittest.TestCase):
    """The walk of the map before closing: the tasks of the current release with no story."""

    def test_names_the_tasks_of_the_current_release_with_no_story(self):
        data = read_story_map.parse(board(delivered_first(SPEC)))
        self.assertEqual(read_story_map.gaps(data),
                         [{"activity": "Remind", "task": "Send the reminder"}])

    def test_a_release_that_covers_every_task_has_no_gaps(self):
        self.assertEqual(read_story_map.gaps(read_story_map.parse(board())), [])

    def test_a_task_with_only_an_open_question_is_a_gap(self):
        spec = copy.deepcopy(SPEC)
        spec["releases"][0]["stories"][1] = [{"text": "Who sends it when the owner is away?", "open": True}]
        self.assertEqual(read_story_map.gaps(read_story_map.parse(board(spec))),
                         [{"activity": "Remind", "task": "Send the reminder"}])


class OpenQuestions(unittest.TestCase):
    def test_names_each_open_question_of_the_current_release_with_its_task(self):
        self.assertEqual(read_story_map.open_questions(read_story_map.parse(board())),
                         [{"activity": "Remind", "task": "Send the reminder",
                           "text": "Who sends it when the owner is away?"}])

    def test_a_release_without_red_stickies_has_none(self):
        spec = copy.deepcopy(SPEC)
        spec["releases"][0]["stories"][1] = [{"text": "Send a WhatsApp reminder", "traces": "Problem"}]
        self.assertEqual(read_story_map.open_questions(read_story_map.parse(board(spec))), [])

    def test_only_the_current_release_is_read(self):
        spec = copy.deepcopy(SPEC)
        spec["releases"][1]["stories"][1] = [{"text": "Still open in Release 2", "open": True}]
        self.assertEqual([q["text"] for q in read_story_map.open_questions(read_story_map.parse(board(spec)))],
                         ["Who sends it when the owner is away?"])


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

    def test_mvp_option_prints_only_the_mvp_by_activity_and_task(self):
        out = self.run_cli("--mvp")
        self.assertIn("### Record a service", out)
        self.assertIn("  - Save a date per customer", out)
        self.assertNotIn("Import dates from the notebook", out)

    def test_says_the_first_release_grew(self):
        self.assertIn("MVP grew by 1 (was 1, now 2)", self.run_cli("--previous", "1"))

    def test_says_the_first_release_shrank(self):
        self.assertIn("MVP shrank by 3 (was 5, now 2)", self.run_cli("--previous", "5"))

    def test_mvp_option_prints_the_first_release_not_delivered(self):
        spec = delivered_first(SPEC)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "board.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(board(spec))
            out = subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "read_story_map.py"), path, "--mvp"],
                                 capture_output=True, text=True, check=True).stdout
        self.assertIn("## Release 2", out)
        self.assertNotIn("Delivered story", out)

    def test_gaps_option_names_the_tasks_with_no_story_of_the_current_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "board.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(board(delivered_first(SPEC)))
            out = subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "read_story_map.py"), path, "--gaps"],
                                 capture_output=True, text=True, check=True).stdout
        self.assertIn("Release 2: 1 task with no story", out)
        self.assertIn("- Remind: Send the reminder", out)

    def test_gaps_option_says_so_when_every_task_has_a_story(self):
        self.assertIn("MVP: every task has a story", self.run_cli("--gaps"))

    def test_says_the_first_release_stayed(self):
        self.assertIn("MVP stayed the same (was 2, now 2)", self.run_cli("--previous", "2"))


    def test_gaps_option_names_each_open_question_of_the_current_release(self):
        out = self.run_cli("--gaps")
        self.assertIn("MVP: 1 open question with no decision", out)
        self.assertIn("- Remind: Send the reminder: Who sends it when the owner is away?", out)


if __name__ == "__main__":
    unittest.main()
