import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def skill():
    with open(os.path.join(ROOT, "skills", "review", "SKILL.md"), encoding="utf-8") as f:
        return f.read()


def layout_section():
    return skill().split("### New files against the layout")[1].split("\n### ")[0].split("## 4. ")[0]


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


class ProjectWithoutALayout(unittest.TestCase):
    def test_without_a_code_layout_section_it_says_so_and_checks_nothing(self):
        text = layout_section()
        self.assertIn("no `## Code layout` section", text)
        self.assertIn("say so", text)
        self.assertIn("check nothing", text)

    def test_it_never_invents_a_layout(self):
        text = layout_section()
        self.assertIn("Never invent a layout", text)
        self.assertIn("common one for the stack", text)

    def test_the_missing_layout_does_not_block_the_issue(self):
        self.assertIn("does not block", layout_section())


class FileTheLayoutDoesNotCover(unittest.TestCase):
    def test_it_names_the_file_and_asks_whether_the_layout_should_cover_it(self):
        text = layout_section()
        self.assertIn("does not cover", text)
        self.assertIn("ask whether the layout should cover it", text)

    def test_it_does_not_block_the_issue(self):
        text = layout_section()
        self.assertIn("A file the layout does not cover does not block the issue", text)


class OnlyAddedAndRenamedFiles(unittest.TestCase):
    def test_the_files_come_from_the_diff_filtered_to_added_and_renamed(self):
        self.assertIn("git diff --name-status --diff-filter=AR develop...<branch>", layout_section())

    def test_a_renamed_file_counts_with_its_new_path(self):
        self.assertIn("new path", layout_section())

    def test_modified_files_are_not_reviewed_against_the_layout(self):
        self.assertIn("Modified files are not reviewed against the layout", layout_section())


class LayoutInThePullRequest(unittest.TestCase):
    def test_a_file_the_layout_does_not_cover_goes_to_the_maintainers_decision(self):
        section = skill().split("## 5. ")[1].split("## 6. ")[0]
        self.assertIn("a new file the layout does not cover", section)


if __name__ == "__main__":
    unittest.main()
