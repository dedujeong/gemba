import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*path):
    with open(os.path.join(ROOT, *path), encoding="utf-8") as f:
        return f.read()


class LanguageRuleCoversWhatThePersonReads(unittest.TestCase):
    def test_the_method_rule_covers_replies_plans_reports_and_questions(self):
        rule = read("references", "context.md").split("## Language")[1]
        self.assertIn("Everything the person reads — replies, plans, reports and questions — is in the project's `Language`", rule)
        self.assertIn("Headings, labels, field names, code, commit messages, branch names and Jira Summaries stay in English", rule)

    def test_implement_writes_its_plan_in_the_project_language(self):
        plan = read("skills", "implement", "SKILL.md").split("## 7. Plan the work")[1].split("## 8. ")[0]
        self.assertIn("Write the plan in the project's `Language`, the plan file included", plan)


if __name__ == "__main__":
    unittest.main()
