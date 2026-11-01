import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Every place of the plugin that says when the findings page of a Spike is created.
PLACES = [
    os.path.join("references", "context.md"),
    os.path.join("skills", "start", "SKILL.md"),
    os.path.join("skills", "start", "assets", "spike.md"),
]


def read(relative):
    with open(os.path.join(ROOT, relative), encoding="utf-8") as f:
        return f.read()


class SpikeFindingsTiming(unittest.TestCase):
    def test_no_place_says_the_page_is_created_when_the_spike_starts(self):
        for place in PLACES:
            with self.subTest(place=place):
                self.assertNotIn("when the Spike starts", read(place))

    def test_every_place_says_the_page_is_created_when_the_test_ends(self):
        for place in PLACES:
            with self.subTest(place=place):
                self.assertIn("when the test ends", read(place))


if __name__ == "__main__":
    unittest.main()
