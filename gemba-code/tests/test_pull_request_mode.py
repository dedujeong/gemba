import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
TEMPLATE = os.path.join(ROOT, "skills", "review", "assets", "pull-request.md")
GITHUB_TEMPLATE = os.path.join(REPO, ".github", "pull_request_template.md")


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def section(text, heading):
    """The text of a '## ' section of a SKILL, up to the next one."""
    match = re.search(r"^## " + re.escape(heading) + r"\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    assert match, "no section " + heading
    return match.group(1)


class PullRequestTemplate(unittest.TestCase):
    def test_the_template_has_the_three_sections_in_order(self):
        with open(TEMPLATE, encoding="utf-8") as f:
            headings = re.findall(r"^## (.*)$", f.read(), re.M)
        self.assertEqual(headings, ["Criteria", "For the maintainer's decision", "Not verified"])

    def test_the_template_has_no_issue_or_commits_section(self):
        with open(TEMPLATE, encoding="utf-8") as f:
            text = f.read()
        self.assertNotIn("## Commits", text)
        self.assertNotIn("**Issue**", text)

    def test_github_shows_the_same_template_that_review_fills(self):
        with open(TEMPLATE, encoding="utf-8") as f:
            skill_copy = f.read()
        with open(GITHUB_TEMPLATE, encoding="utf-8") as f:
            self.assertEqual(f.read(), skill_copy)


class ReviewOpensThePullRequest(unittest.TestCase):
    def skill(self):
        return read("skills", "review", "SKILL.md")

    def test_review_reads_the_integration_of_the_project(self):
        self.assertIn("Integration", section(self.skill(), "1. Find the project"))

    def test_in_pull_request_mode_a_clean_review_pushes_and_opens_the_pull_request_into_develop(self):
        text = section(self.skill(), "5. Open the pull request")
        self.assertIn("`pull request`", text)
        self.assertIn("git push -u origin", text)
        self.assertIn("gh pr create --base develop", text)
        self.assertIn("comes out clean", text)

    def test_the_pull_request_is_titled_with_the_key_and_the_summary_and_filled_from_the_template(self):
        text = section(self.skill(), "5. Open the pull request")
        self.assertIn('--title "<KEY> <Summary>"', text)
        self.assertIn("assets/pull-request.md", text)

    def test_the_pull_request_is_never_opened_for_a_review_that_returns_to_implement_or_for_an_epic_or_spike(self):
        text = section(self.skill(), "5. Open the pull request")
        self.assertIn("unmet", text)
        self.assertIn("Epic", text)
        self.assertIn("Spike", text)

    def test_in_merge_mode_review_still_integrates_nothing(self):
        self.assertIn("Integrate nothing", section(self.skill(), "6. Report and stop"))


if __name__ == "__main__":
    unittest.main()
