import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def skill():
    with open(os.path.join(ROOT, "skills", "review", "SKILL.md"), encoding="utf-8") as f:
        return f.read()


def layout_section():
    return skill().split("### New files against the layout")[1].split("## 4. ")[0]


def return_section():
    return skill().split("## 4. ")[1].split("## 5. ")[0]


class NewFileOutsideTheLayout(unittest.TestCase):
    def test_the_check_is_part_of_the_diff_review_and_comes_before_section_4(self):
        text = skill()
        self.assertLess(text.index("## 3. Review the diff"), text.index("### New files against the layout"))
        self.assertLess(text.index("### New files against the layout"), text.index("## 4. "))

    def test_each_new_file_is_checked_against_the_code_layout_of_the_claude_md(self):
        text = layout_section()
        self.assertIn("`## Code layout`", text)
        self.assertIn("`CLAUDE.md`", text)

    def test_a_file_outside_the_layout_is_named_with_the_place_the_layout_gives_it(self):
        text = layout_section()
        self.assertIn("name the file", text)
        self.assertIn("where the layout says it should go", text)

    def test_a_file_outside_the_layout_returns_the_issue_to_implement(self):
        self.assertIn("outside the layout", layout_section())
        self.assertIn("outside the layout", return_section())
        self.assertIn("Implement", return_section())


if __name__ == "__main__":
    unittest.main()
