import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def skill(name):
    with open(os.path.join(ROOT, "skills", name, "SKILL.md"), encoding="utf-8") as f:
        return f.read()


class StartProposesTheComponent(unittest.TestCase):
    def component_row(self):
        rows = [line for line in skill("start").splitlines() if line.startswith("| Component |")]
        self.assertEqual(len(rows), 1)
        return rows[0]

    def test_a_project_without_components_takes_the_part_from_what_the_change_touches(self):
        row = self.component_row()
        self.assertIn("no components yet", row)
        self.assertIn("Product Brief", row)

    def test_a_new_component_is_said_to_be_new(self):
        self.assertIn("say that it is new", self.component_row())

    def test_few_broad_components_are_preferred(self):
        self.assertIn("few broad components", self.component_row())

    def test_an_existing_component_that_fits_is_reused(self):
        self.assertIn("reuse", self.component_row())

    def test_an_epic_keeps_no_component(self):
        self.assertIn("An Epic has no component", self.component_row())


if __name__ == "__main__":
    unittest.main()
