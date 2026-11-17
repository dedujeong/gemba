import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def walk_section():
    with open(os.path.join(ROOT, "skills", "implement", "SKILL.md"), encoding="utf-8") as f:
        text = f.read()
    match = re.search(r"^## 6\. Walk the work\n(.*?)(?=^## 7\. )", text, re.S | re.M)
    assert match, "no section 6"
    return match.group(1)


class ImplementReadsOnlyTheNamedArtboards(unittest.TestCase):
    def test_it_reads_the_artboards_section_of_an_interface_story(self):
        text = walk_section()
        self.assertIn("interface Story", text)
        self.assertIn("`### Artboards`", text)

    def test_it_reads_only_those_artboards_and_not_the_whole_prototype(self):
        text = walk_section()
        self.assertIn("only those artboards", text)
        self.assertIn("never the whole prototype", text)

    def test_without_named_artboards_it_stops_and_asks_which_before_reading_the_design(self):
        text = walk_section()
        self.assertIn("has no `### Artboards`", text)
        self.assertIn("stop and ask which artboards it uses", text)
        self.assertIn("before reading the design", text)

    def test_a_story_with_no_interface_reads_no_design(self):
        self.assertIn("A Story with no screen reads no design", walk_section())


if __name__ == "__main__":
    unittest.main()
