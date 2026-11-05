import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def skill():
    with open(os.path.join(ROOT, "skills", "implement", "SKILL.md"), encoding="utf-8") as f:
        return f.read()


def section(title, next_title):
    return skill().split(title)[1].split(next_title)[0]


class MechanicalChangeSkipsThePlan(unittest.TestCase):
    def plan(self):
        return section("## 7. Plan the work", "## 8. Build each criterion")

    def test_the_plan_is_skipped_only_when_the_maintainer_says_the_change_is_mechanical(self):
        text = self.plan()
        self.assertIn("the maintainer says the change is mechanical", text)
        self.assertIn("in the request or later", text)

    def test_it_never_decides_by_itself_that_a_change_is_mechanical(self):
        self.assertIn("never decide by yourself that a change is mechanical", self.plan())

    def test_a_mechanical_change_does_not_enter_plan_mode_and_goes_to_the_red_test(self):
        text = self.plan()
        self.assertIn("do not enter plan mode", text)
        self.assertIn("section 8", text)

    def test_the_walk_is_not_skipped(self):
        self.assertIn("The walk of section 6 still happens", self.plan())

    def test_without_the_indication_the_plan_is_proposed_as_always(self):
        text = self.plan()
        self.assertIn("Without that indication", text)
        self.assertIn("EnterPlanMode", text)
        self.assertIn("ExitPlanMode", text)

    def test_the_red_test_still_comes_first_in_the_build(self):
        text = section("## 8. Build each criterion", "## 9. Finish")
        self.assertIn("Red: write the test of the criterion and run it", text)

    def test_the_take_step_points_the_mechanical_case_to_the_plan_section(self):
        text = section("## 2. Take the issue", "## 3. Create the branch")
        self.assertIn("mechanical", text)


if __name__ == "__main__":
    unittest.main()
