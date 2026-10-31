import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "skills", "version-start", "scripts", "read_release.py")
# A board as getConfluenceContent returns it: MVP delivered (gray), Release 2 current with an open question, Release 3 later.
BOARD = os.path.join(ROOT, "tests", "fixtures", "story-map.svg")


def read(*args):
    result = subprocess.run([sys.executable, SCRIPT, BOARD, *args], capture_output=True, text=True, check=True)
    return result.stdout


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

    def test_reports_red_stickies_as_open_questions_not_stories(self):
        self.assertEqual(self.release["open_questions"], ["Who sends it when the owner is away?"])
        stories = [s for a in self.release["stories"] for t in a["tasks"] for s in t["stories"]]
        self.assertNotIn("Who sends it when the owner is away?", stories)


class Markdown(unittest.TestCase):
    def test_prints_the_release_with_its_open_questions(self):
        out = read()
        self.assertTrue(out.startswith("## Release 2"))
        self.assertIn("What the shop owner gets next.", out)
        self.assertIn("### Remind\n- **Send the reminder**\n  - Remind the day before", out)
        self.assertIn("### Open questions\n- Who sends it when the owner is away?", out)


if __name__ == "__main__":
    unittest.main()
