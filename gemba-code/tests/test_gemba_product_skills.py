import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class StartNamesTheGembaProductSkill(unittest.TestCase):
    def test_every_mention_of_version_start_says_it_is_gemba_products(self):
        text = read("skills", "start", "SKILL.md")
        mentions = re.findall(r"version-start", text)
        owned = re.findall(r"Gemba Product's `?version-start`?", text)
        self.assertTrue(mentions)
        self.assertEqual(len(mentions), len(owned))


class ReadmeNamesTheGembaProductSkills(unittest.TestCase):
    def test_it_names_version_start_and_version_close_of_gemba_product(self):
        text = read("README.md")
        self.assertIn("Gemba Product's `version-start` and `version-close`", text)


if __name__ == "__main__":
    unittest.main()
