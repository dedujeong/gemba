import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def skill(name):
    with open(os.path.join(ROOT, "skills", name, "SKILL.md"), encoding="utf-8") as f:
        return f.read()


class WorklogTimeFromTheScript(unittest.TestCase):
    def test_the_skills_that_log_time_read_the_changelog_with_the_tool_that_returns_it(self):
        for name in ("implement", "review", "close"):
            with self.subTest(skill=name):
                text = skill(name)
                self.assertIn("listJiraIssueChangelogs", text)
                self.assertNotIn("expand: changelog", text)

    def test_the_skills_that_log_time_get_it_from_the_script(self):
        for name, path in (("implement", "scripts/state_time.py"),
                           ("review", "../implement/scripts/state_time.py"),
                           ("close", "../implement/scripts/state_time.py")):
            with self.subTest(skill=name):
                self.assertIn(f"python3 {path}", skill(name))

    def test_started_and_time_spent_are_the_ones_the_script_prints(self):
        for name in ("implement", "review", "close"):
            with self.subTest(skill=name):
                text = skill(name)
                self.assertIn("`started`", text)
                self.assertIn("`timeSpent`", text)
                self.assertNotIn("the time from then until now", text)


class OnlyTheTimeNotLoggedYet(unittest.TestCase):
    def test_the_skills_take_the_last_stretch_and_never_add_up_every_one(self):
        for name in ("implement", "review", "close"):
            with self.subTest(skill=name):
                text = skill(name)
                self.assertNotIn("adds up every stretch", text)
                self.assertIn("which is the one not logged yet", text)


if __name__ == "__main__":
    unittest.main()
