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


if __name__ == "__main__":
    unittest.main()
