import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def description():
    path = os.path.join(ROOT, "skills", "implement", "SKILL.md")
    with open(path, encoding="utf-8") as f:
        match = re.search(r"^description: (.*)$", f.read(), re.MULTILINE)
    return match.group(1)


class ImplementDescription(unittest.TestCase):
    def test_the_trigger_sentence_stays_whole_and_ends_with_the_issue_key(self):
        text = description()
        sentence = re.search(r"Use when .*? followed by an issue key\.", text)
        self.assertIsNotNone(sentence)
        for phrase in ('"toma"', '"implementa"', '"empecemos con"', '"vamos con"'):
            self.assertIn(phrase, sentence.group(0))

    def test_the_spike_trigger_is_a_separate_final_sentence(self):
        text = description()
        self.assertTrue(
            text.endswith("Also use when the test of a Spike ends, to publish its findings."))
        self.assertEqual(text.count("Spike"), 1)


if __name__ == "__main__":
    unittest.main()
