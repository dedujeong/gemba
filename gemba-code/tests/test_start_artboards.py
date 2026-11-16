import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def artboards_section():
    text = read("skills", "start", "SKILL.md")
    match = re.search(r"^### Name the artboards of an interface Story\n(.*?)(?=^##+ |\Z)", text, re.S | re.M)
    assert match, "no section Name the artboards of an interface Story"
    return match.group(1)


class StartNamesTheArtboards(unittest.TestCase):
    def test_an_interface_story_gets_an_artboards_section_with_the_ones_that_belong_to_it(self):
        text = artboards_section()
        self.assertIn("interface Story", text)
        self.assertIn("`### Artboards`", text)

    def test_the_names_come_from_the_prototype_section_of_the_design_page(self):
        text = artboards_section()
        self.assertIn("`Prototype` section of the `Design` page", text)

    def test_a_story_with_no_interface_gets_no_artboards_section(self):
        self.assertIn("no `### Artboards`", artboards_section())

    def test_it_never_invents_an_artboard_and_asks_in_the_round_of_questions(self):
        text = artboards_section()
        self.assertIn("Never invent an artboard", text)
        self.assertIn("single round", text)

    def test_the_story_template_has_the_section_after_the_criteria(self):
        template = read("skills", "start", "assets", "story.md")
        self.assertIn("### Artboards", template)
        self.assertLess(template.index("### Acceptance criteria"), template.index("### Artboards"))


if __name__ == "__main__":
    unittest.main()
