import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEURISTICS = os.path.join(ROOT, "skills", "start", "references", "criteria-heuristics.md")

# Each heuristic with a phrase of its question.
NAMES = {
    "Nothing": "no data",
    "One": "only one",
    "Many": "more than one",
    "Limit": "edge of a value",
    "Duplicate": "already exists",
    "No permission": "should not",
    "Half-done failure": "fails halfway",
    "Undo": "reverted",
    "Other state": "another state",
}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class CriteriaHeuristics(unittest.TestCase):
    def setUp(self):
        self.text = read(HEURISTICS)

    def test_each_heuristic_has_its_question(self):
        rows = {line.split("|")[1].strip(): line for line in self.text.splitlines() if line.startswith("| ") and line.count("|") >= 4}
        for name, phrase in NAMES.items():
            self.assertIn(name, rows, name)
            self.assertIn(phrase, rows[name], name)

    def test_has_the_decision_table_method(self):
        self.assertRegex(self.text, r"(?m)^## Decision table")
        self.assertIn("one row per combination", self.text)
        self.assertIn("never goes in the issue", self.text)

    def test_is_written_in_english(self):
        self.assertIsNone(re.search(r"[¿¡áéíóúñÁÉÍÓÚÑ]", self.text))


class StoryTemplate(unittest.TestCase):
    def test_points_at_the_heuristics_and_holds_an_undecided_story(self):
        text = read(os.path.join(ROOT, "skills", "start", "assets", "story.md"))
        self.assertIn("references/criteria-heuristics.md", text)
        self.assertIn("is not declared", text)


if __name__ == "__main__":
    unittest.main()
