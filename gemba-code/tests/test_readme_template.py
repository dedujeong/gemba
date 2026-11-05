import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET = os.path.join(ROOT, "skills", "setup", "assets", "readme.md")


def template():
    """The README the asset gives, without the comment that says who fills it."""
    with open(ASSET, encoding="utf-8") as f:
        return re.sub(r"<!--.*?-->", "", f.read(), flags=re.S)


def fields(text):
    return re.findall(r"<[^<>\n]+>", text)


class ReadmeTemplateSections(unittest.TestCase):
    def test_it_has_the_four_sections_in_english_in_order(self):
        headings = re.findall(r"^## (.+)$", template(), re.M)
        self.assertEqual(headings, ["What it is", "Install", "Run", "Test"])

    def test_it_opens_with_the_product_name_and_a_one_line_description(self):
        lines = [line for line in template().splitlines() if line.strip()]
        self.assertEqual(lines[0], "# <Product name>")
        self.assertTrue(lines[1].startswith("<One-line description"), lines[1])

    def test_it_has_no_section_for_the_brief_the_story_map_or_the_license(self):
        for word in ("Brief", "Story Map", "License"):
            self.assertNotIn(word, template())


class ReadmeTemplateFields(unittest.TestCase):
    def test_every_command_block_holds_a_field_and_no_concrete_command(self):
        blocks = re.findall(r"```bash\n(.*?)\n```", template(), re.S)
        self.assertEqual(len(blocks), 3)
        for block in blocks:
            self.assertTrue(fields(block), block)
            self.assertNotRegex(block, r"\b(npm|pip|cargo|make|yarn|pnpm)\b")

    def test_what_changes_per_project_is_a_field(self):
        found = fields(template())
        for start in ("<Product name>", "<One-line description", "<The problem it solves", "<A requirement",
                      "<install command>", "<run command>", "<the variables", "<test command>"):
            self.assertTrue(any(f.startswith(start) for f in found), start)

    def test_no_text_is_left_outside_the_sections_that_is_not_a_field_or_a_label(self):
        prose = [line for line in template().splitlines()
                 if line.strip() and not line.startswith(("#", "```", "- ", "<"))]
        self.assertEqual(prose, ["Requirements:", "Environment variables: <the variables the project needs to run, or none>"])


if __name__ == "__main__":
    unittest.main()
