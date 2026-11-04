import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "version-close", "SKILL.md")


def skill():
    with open(SKILL, encoding="utf-8") as f:
        return f.read()


def section(text, heading):
    """The body of a `## <heading>` section, up to the next `## ` heading."""
    parts = text.split("## " + heading)
    return parts[1].split("\n## ")[0] if len(parts) > 1 else ""


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


class VersionCloseHandsLearnTheRealTime(unittest.TestCase):
    def step(self):
        return section(skill(), "3. Hand the facts to learn")

    def test_it_reads_the_issues_with_their_estimate_and_time_spent(self):
        text = self.step()
        self.assertIn('project = <Jira Project> AND fixVersion = "<version>"', text)
        self.assertIn("original estimate and time spent", text)

    def test_the_delivered_issues_are_the_done_ones_and_the_cancelled_are_listed_apart(self):
        text = self.step()
        self.assertIn("The delivered ones are those in Done", text)
        self.assertIn("listed apart and its estimate does not enter the totals", text)

    def test_the_release_task_is_listed_apart_while_it_is_not_done(self):
        text = self.step()
        self.assertIn("release Task", text)
        self.assertIn("pending", text)

    def test_it_hands_a_table_with_the_estimate_and_the_time_of_each_delivered_issue(self):
        text = self.step()
        self.assertIn("each with its original estimate and the time recorded in its worklogs", text)
        self.assertIn("`none`", text)

    def test_the_totals_are_added_with_a_tool_and_never_from_memory(self):
        text = self.step()
        self.assertIn("with a tool (Bash), never from memory", text)
        self.assertIn("give both totals", text)

    def test_it_tells_the_maintainer_that_story_map_takes_it_from_there(self):
        self.assertIn("`story-map` skill takes it from here", self.step())


if __name__ == "__main__":
    unittest.main()
