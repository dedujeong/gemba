import copy
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


URL = "https://deducoder.atlassian.net/browse/"


def with_issue_cards(svg, keys):
    """The same board with the stories whose text is in `keys` drawn as the card of their issue, as Confluence returns
    it: a rectangle of the card size with data-type="issue" and the link of the issue, and no text of its own."""
    texts = {m.group(1): m.group(2) for m in re.finditer(r'belongs-to="([^"]+)"[^>]*>[\s\d]*<tspan[^>]*>([^<]*)</tspan>', svg)}
    cards = {sid: keys[text] for sid, text in texts.items() if text in keys}

    def swap(m):
        tag = m.group(0)
        sid = re.search(r' id="([^"]*)"', tag).group(1)
        if sid not in cards:
            return tag
        tag = re.sub(r' data-type="[^"]*"', "", tag).replace("></rect>", ">").replace("/>", ">")
        tag = re.sub(r'width="[\d.]+" height="[\d.]+"', 'width="345" height="136.91"', tag)
        return (tag.rstrip(">").rstrip("/") + f' data-type="issue" data-smartlink-kind="block" data-smartlink-url="{URL}{cards[sid]}"'
                ' data-smartlink-supported-views="block" data-smartlink-supports-preview="false"></rect>')

    svg = re.sub(r"<rect\b[^>]*>(?:</rect>)?", swap, svg)
    for sid in cards:
        svg = re.sub(r'<text\b[^>]*belongs-to="' + re.escape(sid) + r'"[^>]*>.*?</text>', "", svg, flags=re.S)
    return svg


class IssueCards(unittest.TestCase):
    """A story drawn as the card of its Jira issue: it has no text, only the link of the issue."""
    KEYS = {"Save a date per customer": "GEMBA-1", "Send a WhatsApp reminder": "GEMBA-2",
            "Import dates from the notebook": "GEMBA-3"}

    def cards(self):
        return read_story_map.parse(with_issue_cards(board(), self.KEYS))

    def test_each_card_gives_its_key_and_the_release_it_sits_in(self):
        releases = {r["name"]: r for r in self.cards()["releases"]}
        keys = lambda release: [s["key"] for t in release["tasks"] for s in t["stories"] if not s["open"]]
        self.assertEqual(keys(releases["MVP"]), ["GEMBA-1", "GEMBA-2"])
        self.assertEqual(keys(releases["Release 2"]), ["GEMBA-3"])

    def test_a_card_counts_as_a_story_and_is_never_left_unplaced(self):
        data = self.cards()
        self.assertEqual(data["unplaced"], [])
        self.assertEqual([r["count"] for r in data["releases"]], [2, 1])

    def test_a_card_is_listed_by_its_key_where_a_story_is_listed_by_its_text(self):
        mvp = read_story_map.for_development(self.cards())
        self.assertEqual([st for a in mvp["stories"] for t in a["tasks"] for st in t["stories"]], ["GEMBA-1", "GEMBA-2"])

    def test_a_red_card_among_issue_cards_is_an_open_question_not_a_story(self):
        data = self.cards()
        self.assertEqual(data["releases"][0]["open"], 1)
        self.assertEqual([q["text"] for q in read_story_map.open_questions(data)], ["Who sends it when the owner is away?"])

    def test_a_sticky_or_a_rectangle_has_no_key(self):
        story = read_story_map.parse(board())["releases"][0]["tasks"][0]["stories"][0]
        self.assertIsNone(story["key"])


class IssueStatuses(unittest.TestCase):
    """The status a card shows is drawn by Jira, not stored in the SVG: it is handed to the reader by key."""
    STATUSES = {"GEMBA-1": "Done", "GEMBA-2": "Implement"}

    def svg(self):
        return with_issue_cards(board(), IssueCards.KEYS)

    def mvp_stories(self, data):
        return [s for t in data["releases"][0]["tasks"] for s in t["stories"] if not s["open"]]

    def run_cli(self, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            path, statuses = os.path.join(tmp, "board.svg"), os.path.join(tmp, "statuses.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.svg())
            with open(statuses, "w", encoding="utf-8") as f:
                json.dump(self.STATUSES, f)
            return subprocess.run(
                [sys.executable, "-I", os.path.join(SCRIPTS, "read_story_map.py"), path, "--statuses", statuses, *extra],
                capture_output=True, text=True, check=True).stdout

    def test_each_card_gets_the_status_it_was_handed_by_key(self):
        stories = self.mvp_stories(read_story_map.parse(self.svg(), self.STATUSES))
        self.assertEqual([(s["key"], s["status"]) for s in stories], [("GEMBA-1", "Done"), ("GEMBA-2", "Implement")])

    def test_a_card_with_no_status_handed_has_none(self):
        stories = self.mvp_stories(read_story_map.parse(self.svg(), {"GEMBA-1": "Done"}))
        self.assertEqual([s["status"] for s in stories], ["Done", None])
        self.assertEqual({s["status"] for s in self.mvp_stories(read_story_map.parse(self.svg()))}, {None})

    def test_a_sticky_never_has_a_status(self):
        stories = self.mvp_stories(read_story_map.parse(board(), self.STATUSES))
        self.assertEqual({s["status"] for s in stories}, {None})

    def test_the_command_line_takes_the_statuses_and_prints_them_in_json(self):
        mvp = json.loads(self.run_cli("--json"))["releases"][0]
        self.assertEqual([s["status"] for t in mvp["tasks"] for s in t["stories"] if not s["open"]], ["Done", "Implement"])

    def test_the_markdown_shows_the_status_next_to_the_key(self):
        out = self.run_cli()
        self.assertIn("  - GEMBA-1 (Done)", out)
        self.assertIn("  - GEMBA-2 (Implement)", out)


class CancelledCards(unittest.TestCase):
    """An issue that was cancelled stays on the board: the card reads as cancelled and is no longer scope."""
    STATUSES = {"GEMBA-1": "Done", "GEMBA-2": "Cancelled"}

    def data(self, statuses=None):
        return read_story_map.parse(with_issue_cards(board(), IssueCards.KEYS), self.STATUSES if statuses is None else statuses)

    def stories(self, data):
        return {s["key"]: s for t in data["releases"][0]["tasks"] for s in t["stories"] if s["key"]}

    def test_a_card_of_a_cancelled_issue_reads_as_cancelled(self):
        stories = self.stories(self.data())
        self.assertEqual((stories["GEMBA-2"]["status"], stories["GEMBA-2"]["cancelled"]), ("Cancelled", True))
        self.assertFalse(stories["GEMBA-1"]["cancelled"])

    def test_the_status_is_read_whatever_its_case(self):
        self.assertTrue(self.stories(self.data({"GEMBA-2": "cancelled"}))["GEMBA-2"]["cancelled"])

    def test_a_card_with_no_status_or_a_sticky_is_not_cancelled(self):
        self.assertFalse(self.stories(self.data({}))["GEMBA-2"]["cancelled"])
        self.assertFalse(read_story_map.parse(board())["releases"][0]["tasks"][0]["stories"][0]["cancelled"])

    def test_the_release_counts_its_cancelled_cards_apart(self):
        self.assertEqual([r["cancelled"] for r in self.data()["releases"]], [1, 0])
        self.assertIn("MVP: 2 stories, 1 open question, 1 cancelled", read_story_map.summary(self.data()))
        self.assertNotIn("cancelled", read_story_map.summary(self.data({})))

    def test_a_cancelled_card_is_not_scope_for_development(self):
        mvp = read_story_map.for_development(self.data({"GEMBA-1": "Implement", "GEMBA-2": "Cancelled"}))
        self.assertEqual([st for a in mvp["stories"] for t in a["tasks"] for st in t["stories"]], ["GEMBA-1"])


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
            return [{k: v for k, v in r.items() if k not in ("delivered", "state")} for r in read_story_map.parse(svg)["releases"]]
        self.assertEqual(counted(old), counted(new))


def arranged_by_hand(svg):
    """Move every sticky some distance, as a person arranging the board would, without leaving its column and row."""
    def move(m):
        tag = m.group(0)
        if 'data-type="sticky"' not in tag and 'data-type="rectangle"' not in tag:
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
    """A release is delivered when its issues are Done or Cancelled, never because of its color; the scope is the green one."""

    def shipped(self):
        spec = delivered_first(SPEC)
        spec["releases"][1]["stories"] = [[{"text": "Import dates from the notebook", "traces": "Problem"}], [{"text": "Print the labels", "traces": "Problem"}]]
        spec["releases"].append({"name": "Release 3", "description": "Later.", "stories": [["Print the reminders"], []]})
        return spec

    def test_a_gray_release_is_not_delivered_because_it_is_gray(self):
        releases = read_story_map.parse(board(self.shipped()))["releases"]
        self.assertEqual([(r["name"], r["delivered"]) for r in releases],
                         [("MVP", False), ("Release 2", False), ("Release 3", False)])

    def test_a_board_with_nothing_delivered_marks_none(self):
        self.assertFalse(any(r["delivered"] for r in read_story_map.parse(board())["releases"]))

    def test_the_scope_is_the_first_green_release(self):
        mvp = read_story_map.for_development(read_story_map.parse(board(self.shipped())))
        self.assertEqual(mvp["release"], "Release 2")
        self.assertIn("Import dates from the notebook", str(mvp["stories"]))
        self.assertNotIn("Delivered story", str(mvp["stories"]))

    def test_growth_is_measured_on_the_current_release(self):
        board_now = read_story_map.parse(board(self.shipped()))
        self.assertEqual(read_story_map.change(board_now, 3), -1)

    def test_the_summary_compares_the_current_release(self):
        out = read_story_map.summary(read_story_map.parse(board(self.shipped())), 2)
        self.assertIn("MVP: 1 story, 0 open questions", out)
        self.assertNotIn("(delivered)", out)
        self.assertIn("Release 2 stayed the same (was 2, now 2)", out)

    def test_a_release_with_only_open_questions_is_not_delivered(self):
        spec = self.shipped()
        spec["releases"][1]["stories"] = [[{"text": "Still unknown", "open": True}], []]
        self.assertFalse(read_story_map.parse(board(spec))["releases"][1]["delivered"])

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


class ReleaseStates(unittest.TestCase):
    """green = the release about to be declared, gray = the ones after it; delivered only comes from the issues."""
    GREEN, GRAY, ORANGE = "#baf3db", "#f0f1f2", "#fce4a6"
    DONE = {"GEMBA-1": "Done", "GEMBA-2": "Cancelled"}

    def states(self, svg, statuses=None):
        return [(r["name"], r["state"]) for r in read_story_map.parse(svg, statuses)["releases"]]

    def later_row(self):
        spec = copy.deepcopy(SPEC)
        spec["releases"].append({"name": "Later", "description": "Nothing assigned.", "stories": [["Some day"], []]})
        return spec

    def test_the_green_release_is_the_current_one_and_a_gray_one_comes_next(self):
        gray = board().replace(self.ORANGE, self.GRAY)
        self.assertEqual(self.states(gray), [("MVP", "current"), ("Release 2", "next")])

    def test_any_other_color_after_the_green_release_is_next_too(self):
        self.assertEqual(self.states(board()), [("MVP", "current"), ("Release 2", "next")])

    def test_two_green_releases_have_one_current_and_one_next(self):
        both = board().replace(self.ORANGE, self.GREEN)
        self.assertEqual(self.states(both), [("MVP", "current"), ("Release 2", "next")])

    def test_the_later_row_is_never_current_even_when_it_is_green(self):
        svg = board(self.later_row()).replace("#fff5db", self.GREEN)
        self.assertEqual(self.states(svg.replace("#baf3db", self.GRAY, 2))[-1], ("Later", "later"))

    def test_a_release_whose_issues_are_all_done_or_cancelled_is_delivered_and_the_next_green_one_is_current(self):
        svg = with_issue_cards(board().replace(self.ORANGE, self.GREEN), IssueCards.KEYS)
        self.assertEqual(self.states(svg, {"GEMBA-1": "Done", "GEMBA-2": "Cancelled", "GEMBA-3": "Backlog"}),
                         [("MVP", "delivered"), ("Release 2", "current")])

    def test_one_issue_still_open_keeps_the_release_current(self):
        svg = with_issue_cards(board(), IssueCards.KEYS)
        self.assertEqual(self.states(svg, {"GEMBA-1": "Done", "GEMBA-2": "Implement"})[0], ("MVP", "current"))

    def test_without_the_statuses_nothing_is_delivered(self):
        svg = with_issue_cards(board(), IssueCards.KEYS)
        self.assertEqual(self.states(svg), [("MVP", "current"), ("Release 2", "next")])

    def test_stickies_and_rectangles_are_never_delivered(self):
        self.assertFalse(any(r["delivered"] for r in read_story_map.parse(board(), self.DONE)["releases"]))

    def test_a_board_in_the_old_colors_has_no_current_release(self):
        old = board(delivered_first(SPEC)).replace(self.GREEN, self.ORANGE)
        data = read_story_map.parse(old)
        self.assertIsNone(read_story_map.current(data))
        self.assertEqual(read_story_map.for_development(data)["release"], "")

    def test_the_summary_marks_a_delivered_release(self):
        svg = with_issue_cards(board().replace(self.ORANGE, self.GREEN), IssueCards.KEYS)
        out = read_story_map.summary(read_story_map.parse(svg, {"GEMBA-1": "Done", "GEMBA-2": "Done"}))
        self.assertIn("MVP: 2 stories, 1 open question (delivered)", out)


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

    def test_names_every_open_question_when_there_are_several(self):
        spec = copy.deepcopy(SPEC)
        spec["releases"][0]["stories"][1].append({"text": "Do we charge per message?", "open": True})
        self.assertEqual([q["text"] for q in read_story_map.open_questions(read_story_map.parse(board(spec)))],
                         ["Who sends it when the owner is away?", "Do we charge per message?"])

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


class ReleaseDescription(unittest.TestCase):
    """The value a release delivers, written on its row label: what version-start puts on the fix version."""
    FIRST = "What the first release achieves for the shop owner."

    def run_mvp(self, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "board.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(board())
            return subprocess.run(
                [sys.executable, "-I", os.path.join(SCRIPTS, "read_story_map.py"), path, "--mvp", *extra],
                capture_output=True, text=True, check=True).stdout

    def test_every_release_carries_the_description_of_its_row_label(self):
        releases = read_story_map.parse(board())["releases"]
        self.assertEqual(releases[0]["description"], self.FIRST)
        self.assertEqual(releases[1]["description"], "What does not enter the first release.")

    def test_the_current_release_for_development_carries_it(self):
        mvp = read_story_map.for_development(read_story_map.parse(board()))
        self.assertEqual(mvp["description"], self.FIRST)

    def test_mvp_json_gives_the_current_release_with_its_description_and_open_questions(self):
        mvp = json.loads(self.run_mvp("--json"))
        self.assertEqual(sorted(mvp), ["description", "open_questions", "release", "stories"])
        self.assertEqual(mvp["release"], "MVP")
        self.assertEqual(mvp["description"], self.FIRST)
        self.assertEqual(mvp["open_questions"], ["Who sends it when the owner is away?"])

    def test_mvp_markdown_prints_the_description_under_the_release(self):
        self.assertIn("## MVP\n\n" + self.FIRST, self.run_mvp())


if __name__ == "__main__":
    unittest.main()
