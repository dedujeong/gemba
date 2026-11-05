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


if __name__ == "__main__":
    unittest.main()
