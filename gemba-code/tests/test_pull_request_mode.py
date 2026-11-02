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

    def test_a_pull_request_that_is_already_open_is_updated_by_the_push_not_created_again(self):
        text = section(self.skill(), "5. Open the pull request")
        check = "gh pr list --head <branch> --state open"
        self.assertIn(check, text)
        self.assertLess(text.index(check), text.index("gh pr create --base develop"))

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


class CloseLeavesTheMergeToTheMaintainer(unittest.TestCase):
    def skill(self):
        return read("skills", "close", "SKILL.md")

    def test_close_reads_the_integration_of_the_project(self):
        self.assertIn("Integration", section(self.skill(), "1. Find the project"))

    def test_in_merge_mode_close_still_merges_with_no_ff(self):
        self.assertIn("git merge --no-ff", section(self.skill(), "2. Merge and move to Done"))

    def test_in_pull_request_mode_close_goes_to_its_own_section(self):
        self.assertIn("section 5", section(self.skill(), "2. Merge and move to Done"))

    def test_in_pull_request_mode_close_never_merges(self):
        text = section(self.skill(), "5. Close in pull request mode")
        self.assertNotIn("git merge", text)
        self.assertIn("maintainer", text)

    def test_a_pull_request_not_merged_keeps_the_issue_in_review(self):
        text = section(self.skill(), "5. Close in pull request mode")
        self.assertIn("gh pr view", text)
        self.assertIn("not merged", text)
        self.assertIn("do not move the issue to Done", text)

    def test_a_merged_pull_request_syncs_develop_and_removes_the_branch_before_done(self):
        text = section(self.skill(), "5. Close in pull request mode")
        for step in ("git switch develop", "git pull origin develop", "git branch -d", "addOrEditJiraIssueWorklog"):
            self.assertIn(step, text)
        self.assertLess(text.index("git pull origin develop"), text.index("transitionJiraIssue"))
        self.assertLess(text.index("addOrEditJiraIssueWorklog"), text.index("transitionJiraIssue"))


class PublishingNeverMergesIntoMainInPullRequestMode(unittest.TestCase):
    def skill(self):
        return read("skills", "version-close", "SKILL.md")

    def test_version_close_reads_the_integration_of_the_project(self):
        self.assertIn("Integration", section(self.skill(), "1. Find the project"))

    def test_the_collaborative_mode_is_no_longer_left_out(self):
        self.assertNotIn("is not covered here", self.skill())

    def test_in_merge_mode_publishing_still_merges_develop_into_main(self):
        self.assertIn("git merge --no-ff develop", section(self.skill(), "3. Publish the release"))

    def test_in_pull_request_mode_nothing_is_merged_into_main_and_a_pull_request_is_opened(self):
        text = section(self.skill(), "3. Publish the release")
        self.assertIn("`pull request`", text)
        self.assertIn("Nothing is merged into `main`", text)
        self.assertIn("gh pr create --base main --head develop", text)

    def test_a_pull_request_into_main_that_is_already_open_is_reused_not_created_again(self):
        text = section(self.skill(), "3. Publish the release")
        check = "gh pr list --base main --head develop --state open"
        self.assertIn(check, text)
        self.assertLess(text.index(check), text.index("gh pr create --base main"))

    def test_the_tag_and_the_release_wait_for_the_maintainer_to_merge_it(self):
        text = section(self.skill(), "3. Publish the release")
        self.assertIn("git merge-base --is-ancestor origin/develop origin/main", text)
        self.assertIn("the merge into `main` is the maintainer's decision", text)


class SessionCloseOffersTheBackup(unittest.TestCase):
    def skill(self):
        return read("skills", "session-close", "SKILL.md")

    def test_session_close_reads_the_integration_of_the_project(self):
        self.assertIn("Integration", section(self.skill(), "1. Find the project"))

    def test_in_pull_request_mode_it_offers_to_push_the_branch_and_pushes_only_if_the_person_says_yes(self):
        text = section(self.skill(), "5. Offer to back up the branch")
        self.assertIn("`pull request`", text)
        self.assertIn("git push -u origin", text)
        self.assertIn("only if the person says yes", text)

    def test_the_backup_opens_no_pull_request_and_leaves_spikes_alone(self):
        text = section(self.skill(), "5. Offer to back up the branch")
        self.assertIn("open no pull request", text)
        self.assertIn("Spike", text)

    def test_in_merge_mode_it_offers_nothing(self):
        self.assertIn("`merge`", section(self.skill(), "5. Offer to back up the branch"))

    def test_the_handoff_is_written_before_the_offer(self):
        text = self.skill()
        self.assertLess(text.index("## 4. Write the handoff"), text.index("## 5. Offer to back up the branch"))


class MethodRulesDescribePullRequestMode(unittest.TestCase):
    def rules(self):
        return read("references", "context.md")

    def test_the_pull_request_is_opened_by_review_with_the_key_and_the_summary(self):
        text = section(self.rules(), "Merges")
        self.assertIn("`review`", text)
        self.assertIn("`<KEY> <Summary>`", text)

    def test_the_maintainer_merges_and_close_only_waits_for_it(self):
        text = section(self.rules(), "Merges")
        self.assertIn("GitHub's default message", text)
        self.assertIn("`close` merges nothing", text)

    def test_no_skill_merges_into_develop_or_main_in_pull_request_mode(self):
        text = section(self.rules(), "Merges")
        self.assertIn("No skill merges into `develop` or `main`", text)
        self.assertIn("branch protection", text)

    def test_done_in_pull_request_mode_means_the_pull_request_was_merged(self):
        self.assertIn("has merged the pull request", section(self.rules(), "Work cycle"))

    def test_the_rules_still_fit_the_session_start_hook(self):
        self.assertLess(len(self.rules()), 10000)


if __name__ == "__main__":
    unittest.main()
