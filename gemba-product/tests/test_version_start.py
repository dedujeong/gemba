import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(ROOT, "skills", "version-start")


def skill():
    with open(os.path.join(SKILL_DIR, "SKILL.md"), encoding="utf-8") as f:
        return f.read()


class VersionStartIsInTheProductPlugin(unittest.TestCase):
    def test_the_skill_is_named_version_start(self):
        self.assertRegex(skill(), r"(?m)^name: version-start$")

    def test_every_script_the_skill_runs_is_next_to_it(self):
        scripts = set(re.findall(r"scripts/(\w+\.py)", skill()))
        self.assertTrue(scripts, "the skill runs no script")
        for script in scripts:
            with self.subTest(script=script):
                self.assertTrue(os.path.isfile(os.path.join(SKILL_DIR, "scripts", script)))


class VersionStartDeclaresThroughGembaCode(unittest.TestCase):
    def test_every_mention_of_start_names_the_gemba_code_skill(self):
        self.assertEqual(re.findall(r"(?<!gemba-code:)`start`", skill()), [])

    def test_the_cards_and_the_release_task_are_declared_with_it(self):
        text = skill()
        cards = text.split("## 7. Declare the cards")[1].split("## 8.")[0]
        release = text.split("## 8. Declare the release Task")[1].split("## 9.")[0]
        self.assertIn("`gemba-code:start`", cards)
        self.assertIn("`gemba-code:start`", release)


class VersionStartProposesTheNumber(unittest.TestCase):
    def test_the_skill_runs_the_script_to_propose_the_number(self):
        text = skill()
        self.assertIn("scripts/next_version.py", text)
        self.assertIn("--fix", text)

    def test_the_skill_no_longer_forbids_computing_the_number(self):
        text = skill()
        self.assertNotIn("never compute it yourself", text)
        self.assertNotIn("Ask for the number", text)


class VersionStartUnifiesTheComponents(unittest.TestCase):
    def test_the_same_part_of_the_product_carries_the_same_component_in_the_release(self):
        text = skill()
        self.assertIn("same part of the product", text)
        self.assertIn("same component", text)

    def test_the_release_task_has_a_component_in_a_project_without_components(self):
        text = skill()
        self.assertIn("no components yet", text)
        self.assertNotIn("never name a new one", text)

    def test_the_component_the_maintainer_names_for_the_release_task_wins(self):
        self.assertIn("A component the maintainer names for the Task is the one used", skill())


if __name__ == "__main__":
    unittest.main()
