import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_commit_rules_hook import run_hook  # noqa: E402
from test_confirm_push_hook import decision, git, make_repo  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*path):
    with open(os.path.join(ROOT, *path), encoding="utf-8") as f:
        return f.read()


def commits_line(text, start):
    lines = [line for line in text.splitlines() if line.startswith(start)]
    assert len(lines) == 1, lines
    return lines[0]


class TheScopeIsTheCodeLayoutAreaTheChangeTouches(unittest.TestCase):
    def assert_names_the_area(self, text):
        self.assertNotIn("Jira component", text)
        self.assertIn("`## Code layout`", text)

    def test_the_method_reference_names_the_area_and_not_the_jira_component(self):
        self.assert_names_the_area(commits_line(read("references", "context.md"), "- One line, with no body or footer"))

    def test_the_readme_names_the_area_and_not_the_jira_component(self):
        self.assert_names_the_area(commits_line(read("README.md"), "- Commits are one line"))

    def reasons(self):
        repo = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", repo])
        git(repo, "checkout", "-q", "-b", "story/ABC-1-export")
        out = []
        for message in ("feat(): add the export", "feat(Orders): add the export"):
            result = run_hook(repo, f'git commit -m "{message}"')
            out.append(decision(result)["permissionDecisionReason"])
        return out

    def test_the_hook_reasons_name_the_area_and_not_the_jira_component(self):
        for reason in self.reasons():
            self.assertNotIn("Jira component", reason)
            self.assertIn("Code layout", reason)


if __name__ == "__main__":
    unittest.main()
