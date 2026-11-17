import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def skill():
    path = os.path.join(ROOT, "skills", "setup", "SKILL.md")
    with open(path, encoding="utf-8") as f:
        return f.read()


def readme():
    with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as f:
        return f.read()


class SetupDeletesTheRemoteBranchOnMerge(unittest.TestCase):
    HEADING = "## 11. Delete the remote branch on merge"

    def section(self):
        return skill().split(self.HEADING)[1].split("## 12. ")[0]

    def test_the_step_comes_after_the_code_layout_and_before_the_report(self):
        text = skill()
        self.assertLess(text.index("## 10. Write the code layout"), text.index(self.HEADING))
        self.assertLess(text.index(self.HEADING), text.index("## 12. Report"))

    def test_it_only_acts_on_a_github_repository(self):
        text = self.section()
        self.assertIn("`origin`", text)
        self.assertIn("GitHub", text)
        self.assertIn("nothing", text)

    def test_it_turns_the_setting_on_with_the_github_api(self):
        text = self.section()
        self.assertIn("gh repo view --json nameWithOwner --jq .nameWithOwner", text)
        self.assertIn("gh api --method PATCH repos/<owner>/<repo> -F delete_branch_on_merge=true", text)

    def test_it_confirms_by_reading_the_setting_back(self):
        text = self.section()
        self.assertIn("gh api repos/<owner>/<repo> --jq .delete_branch_on_merge", text)
        self.assertIn("`true`", text)

    def test_it_changes_nothing_when_the_setting_is_already_on(self):
        self.assertIn("already `true`", self.section())

    def test_without_commands_it_puts_them_in_the_reply(self):
        self.assertIn("If you cannot run commands", self.section())

    def test_without_permission_it_does_not_retry_nor_assume_it_worked(self):
        text = self.section()
        self.assertIn("lacks permission", text)
        self.assertIn("do not retry", text)

    def test_without_permission_it_tells_the_maintainer_what_to_enable_and_where(self):
        text = self.section()
        self.assertIn("Automatically delete head branches", text)
        self.assertIn("Settings > General > Pull Requests", text)

    def test_the_report_says_what_happened_with_the_setting(self):
        report = skill().split("## 12. Report")[1]
        self.assertIn("delete branch on merge", report)

    def test_the_readme_mentions_it(self):
        self.assertIn("delete the remote branch on merge", readme())


if __name__ == "__main__":
    unittest.main()
