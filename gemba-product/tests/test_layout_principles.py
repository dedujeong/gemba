import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHITECTURE = os.path.join(ROOT, "skills", "architecture")
PRINCIPLES = os.path.join(ARCHITECTURE, "references", "layout-principles.md")
SKILL = os.path.join(ARCHITECTURE, "SKILL.md")


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


class LayoutPrinciples(unittest.TestCase):
    def test_reference_exists(self):
        self.assertTrue(os.path.isfile(PRINCIPLES))

    def test_reference_states_both_principles(self):
        body = read(PRINCIPLES).lower()
        self.assertIn("what changes together stays together", body)
        self.assertIn("one direction", body)
        self.assertIn("public entry", body)

    def test_skill_points_to_the_reference(self):
        self.assertIn("references/layout-principles.md", read(SKILL))


if __name__ == "__main__":
    unittest.main()
