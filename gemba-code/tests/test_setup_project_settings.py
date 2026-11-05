import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def skill():
    path = os.path.join(ROOT, "skills", "setup", "SKILL.md")
    with open(path, encoding="utf-8") as f:
        return f.read()


class SetupMergeMessage(unittest.TestCase):
    def test_setup_leaves_the_merge_message_with_into_main(self):
        self.assertIn('git config merge.suppressDest ""', skill())

    def test_setup_no_longer_claims_to_write_only_the_claude_md(self):
        self.assertNotIn("You write nothing else to the repository", skill())


class SetupAttribution(unittest.TestCase):
    def test_setup_turns_off_the_attribution_in_the_project_settings(self):
        text = skill()
        self.assertIn(".claude/settings.json", text)
        self.assertIn('"attribution": {"commit": "", "pr": ""}', text)

    def test_setup_keeps_the_other_settings(self):
        self.assertIn("Keep every other key", skill())


class SetupGitignore(unittest.TestCase):
    def test_setup_writes_the_base_gitignore_with_the_script(self):
        text = skill()
        self.assertIn("scripts/write_gitignore.py", text)
        for entry in (".claude/settings.local.json", "CLAUDE.local.md", ".claude/worktrees/", ".gemba/sessions/"):
            self.assertIn(entry, text)

    def test_the_gitignore_comes_after_the_attribution_and_before_the_report(self):
        text = skill()
        self.assertLess(text.index("Turn off the Claude attribution"), text.index("scripts/write_gitignore.py"))
        self.assertLess(text.index("scripts/write_gitignore.py"), text.index("## 7. Report"))

    def test_the_report_says_whether_the_gitignore_was_written(self):
        report = skill().split("## 7. Report")[1]
        self.assertIn(".gitignore", report)


if __name__ == "__main__":
    unittest.main()
