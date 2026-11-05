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
    def test_it_has_the_sections_in_english_in_order(self):
        headings = re.findall(r"^## (.+)$", template(), re.M)
        self.assertEqual(headings, ["What it is", "Install", "Run", "Test", "License"])

    def test_it_opens_with_the_product_name_and_a_one_line_description(self):
        lines = [line for line in template().splitlines() if line.strip()]
        self.assertEqual(lines[0], "# <Product name>")
        self.assertTrue(lines[1].startswith("<One-line description"), lines[1])

    def test_it_has_no_section_for_the_brief_or_the_story_map(self):
        for word in ("Brief", "Story Map"):
            self.assertNotIn(word, template())


class ReadmeTemplateLicense(unittest.TestCase):
    def section(self):
        return template().split("## License")[1]

    def test_the_section_names_the_license_and_links_the_license_file(self):
        self.assertIn("[<License name>](LICENSE).", self.section())

    def test_the_sentence_about_the_notice_is_marked_as_only_for_apache(self):
        text = self.section()
        self.assertIn("<Only with Apache-2.0:", text)
        self.assertIn("[NOTICE](NOTICE)", text)

    def test_the_copyright_line_has_the_year_and_the_holder_with_the_link(self):
        self.assertIn("Copyright <year> [<holder>](<holder URL>).", self.section())


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
                      "<install command>", "<run command>", "<the variables", "<test command>",
                      "<License name>", "<year>", "<holder>", "<holder URL>"):
            self.assertTrue(any(f.startswith(start) for f in found), start)

    def test_no_text_is_left_outside_the_sections_that_is_not_a_field_or_a_label(self):
        prose = [line for line in template().splitlines()
                 if line.strip() and not line.startswith(("#", "```", "- ", "<"))]
        self.assertEqual(prose, ["Requirements:", "Environment variables: <the variables the project needs to run, or none>",
                                 "[<License name>](LICENSE). <Only with Apache-2.0: If you redistribute <Product name> or a derivative work, keep, among other conditions, the copyright notice and the [NOTICE](NOTICE) file with the attribution to the author.>",
                                 "Copyright <year> [<holder>](<holder URL>)."])


if __name__ == "__main__":
    unittest.main()
