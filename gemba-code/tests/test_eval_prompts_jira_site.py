import glob
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPTS = sorted(glob.glob(os.path.join(ROOT, "evals", "*", "prompt.md")))

SITE = re.compile(r"^- Jira Site: \S+\.atlassian\.net\s*$")


def gemba_blocks(text):
    """The bullet lists that follow each `## Gemba` heading of a prompt."""
    lines = text.splitlines()
    blocks = []
    for index, line in enumerate(lines):
        if line.strip() != "## Gemba":
            continue
        block = []
        for following in lines[index + 1:]:
            if following.startswith("- "):
                block.append(following)
            elif block or following.strip():
                break
        blocks.append(block)
    return blocks


def without_site(text):
    return [block for block in gemba_blocks(text) if not any(SITE.match(line) for line in block)]


class JiraSiteInEvalPrompts(unittest.TestCase):
    def test_the_walk_finds_prompts_with_a_gemba_block(self):
        self.assertTrue(any(gemba_blocks(open(p, encoding="utf-8").read()) for p in PROMPTS))

    def test_every_gemba_block_of_an_eval_prompt_has_the_jira_site(self):
        missing = []
        for path in PROMPTS:
            with open(path, encoding="utf-8") as f:
                if without_site(f.read()):
                    missing.append(os.path.basename(os.path.dirname(path)))
        self.assertEqual(missing, [], f"{len(missing)} eval prompts have a Gemba block without Jira Site")


class TheReaderOfTheBlock(unittest.TestCase):
    block = "## Gemba\n\n- Jira Project: TALLER\n{site}- Confluence Space: TALLER\n- Language: es-MX\n\n## Code layout\n"

    def test_it_finds_a_block_without_the_site(self):
        self.assertEqual(len(without_site(self.block.format(site=""))), 1)

    def test_it_accepts_a_block_with_the_site(self):
        self.assertEqual(without_site(self.block.format(site="- Jira Site: taller.atlassian.net\n")), [])

    def test_it_reads_only_the_bullets_of_the_block(self):
        (block,) = gemba_blocks(self.block.format(site=""))
        self.assertEqual(len(block), 3)


if __name__ == "__main__":
    unittest.main()
