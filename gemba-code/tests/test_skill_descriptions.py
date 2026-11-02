import glob
import os
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def descriptions():
    pattern = os.path.join(REPO, "*", "skills", "*", "SKILL.md")
    for path in sorted(glob.glob(pattern)):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("description:"):
                    yield os.path.relpath(path, REPO), line
                    break


class SkillDescriptionsSyncWithClaudeAi(unittest.TestCase):
    def test_every_skill_has_a_description(self):
        self.assertGreater(len(list(descriptions())), 0)

    def test_no_description_contains_angle_brackets(self):
        for path, line in descriptions():
            with self.subTest(skill=path):
                self.assertNotRegex(line, r"[<>]", path + " has angle brackets in its description")


if __name__ == "__main__":
    unittest.main()
