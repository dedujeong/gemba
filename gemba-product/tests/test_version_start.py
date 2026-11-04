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

    def test_every_script_the_skill_runs_exists_where_it_says(self):
        scripts = set(re.findall(r"((?:\.\./[\w-]+/)?scripts/\w+\.py)", skill()))
        self.assertTrue(scripts, "the skill runs no script")
        for script in scripts:
            with self.subTest(script=script):
                self.assertTrue(os.path.isfile(os.path.join(SKILL_DIR, script)))


class VersionStartDeclaresThroughGembaCode(unittest.TestCase):
    def test_every_mention_of_start_names_the_gemba_code_skill(self):
        self.assertEqual(re.findall(r"(?<!gemba-code:)`start`", skill()), [])

    def test_the_cards_and_the_release_task_are_declared_with_it(self):
        text = skill()
        cards = text.split("## 7. Declare the cards")[1].split("## 8.")[0]
        release = text.split("## 8. Declare the release Task")[1].split("## 9.")[0]
        self.assertIn("`gemba-code:start`", cards)
        self.assertIn("`gemba-code:start`", release)


class VersionStartNeedsGembaCode(unittest.TestCase):
    def first_step(self):
        return skill().split("## 1.")[1].split("## 2.")[0]

    def test_it_checks_for_the_gemba_code_skill_before_anything_else(self):
        self.assertIn("`gemba-code:start`", self.first_step())
        self.assertIn("available skills", self.first_step())

    def test_it_says_gemba_code_is_required_when_the_skill_is_missing(self):
        self.assertIn("Gemba Code is required", self.first_step())

    def test_it_creates_nothing_when_the_skill_is_missing(self):
        self.assertIn("create no fix version", self.first_step())
        self.assertIn("declare nothing", self.first_step())


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


class VersionStartReadsTheMapWithTheSingleReader(unittest.TestCase):
    def step(self, number):
        return skill().split(f"## {number}.")[1].split("\n## ")[0]

    def test_it_reads_the_current_release_with_the_reader_of_story_map(self):
        text = self.step(3)
        self.assertIn("python3 ../story-map/scripts/read_story_map.py", text)
        self.assertIn("--mvp --json", text)

    def test_it_keeps_no_reader_of_its_own(self):
        self.assertNotIn("read_release", skill())

    def test_it_stops_on_the_open_questions_the_reader_returns_apart(self):
        text = self.step(4)
        self.assertIn("`open_questions`", text)
        self.assertIn("nothing of the version is declared", text)


class VersionStartLeavesTheKeysToTheCards(unittest.TestCase):
    def test_the_product_plugin_keeps_no_copy_of_the_old_readers(self):
        for script in ("read_release.py", "write_keys.py"):
            with self.subTest(script=script):
                self.assertFalse(os.path.exists(os.path.join(SKILL_DIR, "scripts", script)))

    def test_the_skill_no_longer_writes_keys_on_the_stickies(self):
        text = skill()
        self.assertNotIn("write_keys", text)
        self.assertNotIn("Put the keys on the Story Map", text)


if __name__ == "__main__":
    unittest.main()
