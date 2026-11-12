import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERENCE = os.path.join(ROOT, "references", "jira-calls.md")
SKILLS_THAT_CALL_JIRA = ("implement", "review", "close", "session-start", "session-close", "start", "setup")
READS = ("Read an issue", "Read the state of an issue", "Search issues", "Read the changelog",
         "Find a project", "List the components", "List the versions")
WRITES = ("Log the time", "Create an issue", "Link two issues", "Edit an issue")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def skill(name):
    return read(os.path.join(ROOT, "skills", name, "SKILL.md"))


def calls():
    """Each `## <call>` section of the reference, by its heading."""
    parts = re.split(r"^## ", read(REFERENCE), flags=re.M)[1:]
    return {part.split("\n", 1)[0].strip(): part for part in parts}


class EveryJiraCallIsInTheReference(unittest.TestCase):
    def test_the_reference_has_one_section_per_call(self):
        self.assertTrue(os.path.exists(REFERENCE))
        for name in READS + WRITES:
            with self.subTest(call=name):
                self.assertIn(name, calls())

    def test_every_read_names_its_fields_and_its_response_fields(self):
        found = calls()
        for name in READS:
            with self.subTest(call=name):
                self.assertIn("`executeRead`", found[name])
                self.assertIn("responseFields", found[name])
        for name in ("Read an issue", "Read the state of an issue", "Search issues"):
            with self.subTest(call=name):
                self.assertIn("fields", found[name].replace("responseFields", ""))

    def test_every_write_goes_through_execute_write_with_response_fields(self):
        found = calls()
        for name in WRITES:
            with self.subTest(call=name):
                self.assertIn("`executeWrite`", found[name])
                self.assertIn("responseFields", found[name])

    def test_the_reference_never_uses_the_evidence_view(self):
        self.assertNotIn("`evidence`", read(REFERENCE))


class SkillsUseTheReference(unittest.TestCase):
    def test_no_skill_asks_jira_for_the_evidence_view(self):
        for name in SKILLS_THAT_CALL_JIRA:
            with self.subTest(skill=name):
                self.assertNotIn("`evidence`", skill(name))

    def test_every_skill_that_calls_jira_names_the_reference(self):
        for name in SKILLS_THAT_CALL_JIRA:
            with self.subTest(skill=name):
                self.assertIn("../../references/jira-calls.md", skill(name))


class TheJiraSiteLivesInTheGembaBlock(unittest.TestCase):
    def test_the_block_has_the_jira_site(self):
        block = read(os.path.join(ROOT, "skills", "setup", "assets", "gemba-block.md"))
        self.assertIn("- Jira Site: <Jira site host>", block)
        self.assertLess(block.index("- Jira Project:"), block.index("- Jira Site:"))

    def test_setup_fills_the_jira_site_from_the_accessible_resources(self):
        text = skill("setup")
        self.assertIn("| Jira Site |", text)
        self.assertIn("getAccessibleAtlassianResources", text)
        self.assertIn("update its five fields", text)

    def test_the_readme_lists_the_jira_site_among_the_block_fields(self):
        self.assertIn("Jira project, Jira site, Confluence space", read(os.path.join(ROOT, "README.md")))

    def test_the_other_skills_use_the_jira_site_as_cloud_id(self):
        for name in SKILLS_THAT_CALL_JIRA:
            if name == "setup":
                continue
            with self.subTest(skill=name):
                text = skill(name)
                self.assertIn("Use its `Jira Site` as the `cloudId` of every call", text)
                self.assertNotIn("Get the cloudId once with `getAccessibleAtlassianResources`", text)


if __name__ == "__main__":
    unittest.main()
