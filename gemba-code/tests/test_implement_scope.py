import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def skill(name):
    with open(os.path.join(ROOT, "skills", name, "SKILL.md"), encoding="utf-8") as f:
        return f.read()


class ImplementTakesTheScopeFromTheAreaTheChangeTouches(unittest.TestCase):
    def scope_line(self):
        lines = [line for line in skill("implement").splitlines() if line.strip().startswith("- `<scope>`")]
        self.assertEqual(len(lines), 1)
        return lines[0]

    def test_the_scope_is_not_the_component_of_the_issue(self):
        self.assertNotIn("Jira component of the issue", self.scope_line())

    def test_the_scope_is_the_name_of_the_code_layout_area_the_change_touches(self):
        line = self.scope_line()
        self.assertIn("`## Code layout`", line)
        self.assertIn("area the change touches", line)

    def test_an_area_of_any_type_gives_the_scope(self):
        line = self.scope_line()
        self.assertIn("`domain`", line)
        self.assertIn("`technical`", line)

    def test_without_a_fitting_area_or_with_two_or_more_the_commit_has_no_scope(self):
        line = self.scope_line()
        self.assertIn("no area fits", line)
        self.assertIn("two or more", line)
        self.assertIn("no scope", line)


if __name__ == "__main__":
    unittest.main()
