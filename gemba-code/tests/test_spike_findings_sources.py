import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*path):
    with open(os.path.join(ROOT, *path), encoding="utf-8") as f:
        return f.read()


def finish_a_spike():
    return read("skills", "implement", "SKILL.md").split("## 10. Finish a Spike")[1]


def spike_findings_rule():
    return read("references", "context.md").split("## Spike findings")[1].split("\n## ")[0]


class SpikeSourcesAreCards(unittest.TestCase):
    def test_implement_lists_every_adr_and_link_consulted_as_a_block_card(self):
        text = finish_a_spike()
        self.assertIn("Sources lists, as block cards", text)
        self.assertIn('data-card-appearance="block"', text)
        self.assertIn("every ADR and every link consulted while running the test", text)

    def test_the_method_says_the_same(self):
        self.assertIn("Sources lists, as block cards, every ADR and every link consulted while running the test",
                      spike_findings_rule())


if __name__ == "__main__":
    unittest.main()
