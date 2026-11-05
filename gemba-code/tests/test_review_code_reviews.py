import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def skill():
    with open(os.path.join(ROOT, "skills", "review", "SKILL.md"), encoding="utf-8") as f:
        return f.read()


def code_reviews_section():
    return skill().split("### Code reviews of the change")[1].split("## 4. ")[0]


class ChangeThatOnlyTouchesDocsSkillsOrBehavior(unittest.TestCase):
    def test_the_choice_of_code_reviews_comes_after_the_layout_check_and_before_section_4(self):
        text = skill()
        self.assertLess(text.index("### New files against the layout"), text.index("### Code reviews of the change"))
        self.assertLess(text.index("### Code reviews of the change"), text.index("## 4. "))

    def test_it_decides_from_the_files_and_the_size_of_the_diff(self):
        text = code_reviews_section()
        self.assertIn("git diff --name-only develop...<branch>", text)
        self.assertIn("git diff --shortstat develop...<branch>", text)

    def test_a_change_that_only_touches_docs_skills_or_behavior_launches_no_code_review(self):
        text = code_reviews_section()
        for kind in ("docs", "skills", "evals"):
            self.assertIn(kind, text)
        self.assertIn("launches no code review", text)

    def test_it_says_that_this_is_verified_with_evals_or_another_mechanism(self):
        self.assertIn("verified with evals or another mechanism", code_reviews_section())


class SmallChangeOfLowRisk(unittest.TestCase):
    def test_a_small_code_change_of_low_risk_may_launch_no_review(self):
        text = code_reviews_section()
        self.assertIn("small code change of low risk", text)
        self.assertIn("may launch none", text)

    def test_it_says_why_no_review_was_launched(self):
        self.assertIn("Say why", code_reviews_section())

    def test_the_risk_is_judged_by_the_sensitive_areas_the_change_touches(self):
        text = code_reviews_section()
        for area in ("auth", "permissions", "money", "personal data", "migrations", "dependencies", "deploy"):
            self.assertIn(area, text)


class CodeReviewsLaunchedInParallel(unittest.TestCase):
    def test_both_reviews_are_launched_in_the_same_turn(self):
        text = code_reviews_section()
        self.assertIn("`/code-review`", text)
        self.assertIn("`/security-review`", text)
        self.assertIn("in the same turn, in parallel", text)

    def test_the_level_of_code_review_is_chosen_by_size_and_risk_among_four(self):
        text = code_reviews_section()
        for level in ("`low`", "`medium`", "`high`", "`xhigh`"):
            self.assertIn(level, text)
        self.assertIn("by the size and the risk", text)

    def test_max_and_ultra_are_never_chosen(self):
        text = code_reviews_section()
        self.assertIn("never `max` or `ultra`", text)

    def test_it_says_what_was_launched_and_why(self):
        self.assertIn("Say what was launched and why", code_reviews_section())


if __name__ == "__main__":
    unittest.main()
