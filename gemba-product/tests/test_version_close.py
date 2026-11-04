import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "version-close", "SKILL.md")


def skill():
    with open(SKILL, encoding="utf-8") as f:
        return f.read()


def section(text, heading):
    """The body of a `## <heading>` section, up to the next `## ` heading."""
    return text.split("## " + heading)[1].split("\n## ")[0]


class VersionCloseChecksTheOpenIssues(unittest.TestCase):
    def test_the_skill_is_named_version_close(self):
        self.assertRegex(skill(), r"(?m)^name: version-close$")

    def test_it_searches_the_issues_of_the_fix_version_outside_done_or_cancelled(self):
        text = section(skill(), "2. Check the issues")
        self.assertIn('fixVersion = "<version>" AND status NOT IN (Done, Cancelled)', text)

    def test_the_release_task_never_counts_as_open_work(self):
        text = section(skill(), "2. Check the issues")
        self.assertIn("Leave out the release Task of the version", text)

    def test_when_an_issue_is_left_it_does_not_close_and_names_each_open_one(self):
        text = section(skill(), "2. Check the issues")
        self.assertIn("do not close the version", text)
        self.assertIn("List each one on its own line, as a link with its summary and status", text)

    def test_when_none_is_left_it_says_no_issue_keeps_the_version_open(self):
        self.assertIn("no issue keeps the version open", section(skill(), "2. Check the issues"))


if __name__ == "__main__":
    unittest.main()
