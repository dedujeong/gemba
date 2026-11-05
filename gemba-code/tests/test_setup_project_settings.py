import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def skill():
    path = os.path.join(ROOT, "skills", "setup", "SKILL.md")
    with open(path, encoding="utf-8") as f:
        return f.read()


class SetupMergeMessage(unittest.TestCase):
    def test_setup_leaves_the_merge_message_with_into_main(self):
        self.assertIn('git config merge.suppressDest ""', skill())

    def test_setup_no_longer_claims_to_write_only_the_claude_md(self):
        self.assertNotIn("You write nothing else to the repository", skill())


class SetupAttribution(unittest.TestCase):
    def test_setup_turns_off_the_attribution_in_the_project_settings(self):
        text = skill()
        self.assertIn(".claude/settings.json", text)
        self.assertIn('"attribution": {"commit": "", "pr": ""}', text)

    def test_setup_keeps_the_other_settings(self):
        self.assertIn("Keep every other key", skill())


class SetupGitignore(unittest.TestCase):
    def test_setup_writes_the_base_gitignore_with_the_script(self):
        text = skill()
        self.assertIn("scripts/write_gitignore.py", text)
        for entry in (".claude/settings.local.json", "CLAUDE.local.md", ".claude/worktrees/", ".gemba/sessions/"):
            self.assertIn(entry, text)

    def test_the_gitignore_comes_after_the_attribution_and_before_the_report(self):
        text = skill()
        self.assertLess(text.index("Turn off the Claude attribution"), text.index("scripts/write_gitignore.py"))
        self.assertLess(text.index("scripts/write_gitignore.py"), text.index("## 9. Report"))

    def test_the_report_says_whether_the_gitignore_was_written(self):
        report = skill().split("## 9. Report")[1]
        self.assertIn(".gitignore", report)


class SetupLicense(unittest.TestCase):
    def section(self):
        return skill().split("## 7. Write the license")[1].split("## 8. Write the project README")[0]

    def test_the_license_comes_after_the_gitignore_and_before_the_readme(self):
        text = skill()
        self.assertLess(text.index("## 6. Write the base .gitignore"), text.index("## 7. Write the license"))
        self.assertLess(text.index("## 7. Write the license"), text.index("## 8. Write the project README"))

    def test_it_asks_which_license_among_apache_mit_or_none_when_there_is_no_license(self):
        text = self.section()
        self.assertIn("has no `LICENSE`", text)
        for choice in ("Apache-2.0", "MIT", "none"):
            self.assertIn(choice, text)
        self.assertIn("do not choose for the person", text)

    def test_the_holder_the_holder_url_and_the_year_are_proposed_and_confirmed_before_writing(self):
        text = self.section()
        for source in ("git config user.name", "git remote get-url origin"):
            self.assertIn(source, text)
        self.assertIn("year", text)
        self.assertIn("Never write the files before the person confirms", text)

    def test_the_files_are_written_by_the_script_and_never_typed_or_copied(self):
        text = self.section()
        self.assertIn("scripts/write_license.py", text)
        self.assertIn("never type or paraphrase a license text", text)
        self.assertIn("keep a copy", text)

    def test_an_existing_license_is_not_asked_about_or_replaced(self):
        text = self.section()
        self.assertIn("ask nothing", text)
        self.assertIn("leave it as it is", text)

    def test_when_the_text_cannot_be_read_nothing_is_written_and_what_is_missing_is_said(self):
        text = self.section()
        self.assertIn("writes nothing", text)
        self.assertIn("what is missing", text)

    def test_the_report_says_what_happened_with_the_license(self):
        report = skill().split("## 9. Report")[1]
        self.assertIn("license", report)


class SetupReadme(unittest.TestCase):
    def section(self):
        return skill().split("## 8. Write the project README")[1].split("## 9. Report")[0]

    def test_the_readme_comes_after_the_gitignore_and_before_the_report(self):
        text = skill()
        self.assertLess(text.index("## 6. Write the base .gitignore"), text.index("## 8. Write the project README"))
        self.assertLess(text.index("## 8. Write the project README"), text.index("## 9. Report"))

    def test_it_is_written_from_the_template_of_the_assets(self):
        self.assertIn("assets/readme.md", self.section())

    def test_the_name_the_description_and_what_it_is_come_from_the_product_brief(self):
        text = self.section()
        self.assertIn("Product Brief", text)
        for field in ("product name", "one-line description", "What it is"):
            self.assertIn(field, text)

    def test_install_run_and_test_come_only_from_what_the_repository_states(self):
        text = self.section()
        self.assertIn("Install, Run and Test", text)
        self.assertIn("only from what the repository states", text)
        self.assertIn("stays as a field to fill", text)

    def test_it_is_written_only_when_the_repository_has_no_readme(self):
        self.assertIn("no `README.md`", self.section())

    def test_the_comment_of_the_template_is_removed(self):
        self.assertIn("Remove the comment", self.section())

    def test_the_content_is_in_the_project_language_and_the_structure_in_english(self):
        text = self.section()
        self.assertIn("project's `Language`", text)
        self.assertIn("section names and every field that stays to fill are kept exactly as the template has them, in English", text)

    def test_a_requirement_is_a_proper_name_with_its_version_and_not_a_sentence(self):
        text = self.section()
        self.assertIn("canonical form with its version", text)
        self.assertIn("never a sentence or the hint of the field", text)

    def test_the_report_says_whether_the_readme_was_written(self):
        report = skill().split("## 9. Report")[1]
        self.assertIn("README", report)


class SetupExistingReadme(unittest.TestCase):
    def section(self):
        return skill().split("## 8. Write the project README")[1].split("## 9. Report")[0]

    def test_an_existing_readme_is_never_replaced_or_rewritten(self):
        text = self.section()
        self.assertIn("already has a `README.md`", text)
        self.assertIn("never replace or rewrite it", text)

    def test_its_headings_are_compared_with_the_four_of_the_template(self):
        text = self.section()
        self.assertIn("Compare its headings", text)
        self.assertIn("counts as present", text)
        self.assertIn('"Installation" for Install', text)

    def test_only_the_missing_sections_are_proposed_and_not_written(self):
        text = self.section()
        self.assertIn("Propose only the sections it lacks", text)
        self.assertIn("do not write them", text)

    def test_the_report_says_which_sections_were_proposed(self):
        report = skill().split("## 9. Report")[1]
        self.assertIn("proposed", report)


if __name__ == "__main__":
    unittest.main()
