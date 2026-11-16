import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "skills", "setup", "assets", "readme.md")
CRITERIA = os.path.join(
    ROOT, "evals", "proposes-only-the-missing-readme-sections", "graders", "criteria.md"
)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def template_sections():
    text = re.sub(r"<!--.*?-->", "", read(TEMPLATE), flags=re.S)
    return re.findall(r"^## (.+)$", text, re.M)


class ExistingReadmeEvalCriteria(unittest.TestCase):
    def test_it_names_every_section_of_the_template(self):
        criteria = read(CRITERIA)
        for section in template_sections():
            self.assertIn(section, criteria, "the criteria do not name the section " + section)

    def test_it_proposes_the_license_only_when_a_license_is_known(self):
        self.assertIn("only when a license is known", read(CRITERIA))

    def test_it_still_fails_what_it_must_not_propose_or_invent(self):
        criteria = read(CRITERIA)
        for text in (
            "does not propose What it is or Install again",
            "omits Run or Test",
            "invents a command for Run or Test",
            "presents the README as already changed",
        ):
            self.assertIn(text, criteria)


if __name__ == "__main__":
    unittest.main()
