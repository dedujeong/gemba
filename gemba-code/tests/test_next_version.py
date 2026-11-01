import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "skills", "version-start", "scripts", "next_version.py")


def version(name, released=True, archived=False):
    return {"name": name, "released": released, "archived": archived}


def run(product, versions, *args):
    """Runs the script on the versions as getJiraProjectVersions returns them, from a temporary file."""
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "versions.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"values": versions}, f)
        return subprocess.run([sys.executable, SCRIPT, product, path, *args], capture_output=True, text=True)


class NextVersion(unittest.TestCase):
    def test_a_release_raises_the_minor_number_of_the_last_published_version(self):
        versions = [version("Gemba Code v0.1.0"), version("Gemba Code v0.1.1"),
                    version("Gemba Code v0.2.0"), version("Gemba Code v0.3.0")]
        result = run("Gemba Code", versions)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "Gemba Code v0.4.0")

    def test_versions_are_ordered_by_number_not_by_text(self):
        result = run("Taller", [version("Taller v0.9.0"), version("Taller v0.10.0")])
        self.assertEqual(result.stdout.strip(), "Taller v0.11.0")

    def test_a_bug_fix_raises_the_third_number(self):
        result = run("Gemba Code", [version("Gemba Code v0.2.0"), version("Gemba Code v0.3.0")], "--fix")
        self.assertEqual(result.stdout.strip(), "Gemba Code v0.3.1")

    def test_other_products_and_unpublished_or_archived_versions_do_not_count(self):
        versions = [version("Gemba Product v0.3.1"), version("Gemba Code v0.3.0"),
                    version("Gemba Code v0.4.0", released=False),
                    version("Gemba Code v0.5.0", archived=True)]
        self.assertEqual(run("Gemba Code", versions).stdout.strip(), "Gemba Code v0.4.0")

    def test_a_product_without_published_versions_starts_at_0_1_0(self):
        self.assertEqual(run("Taller", [version("Gemba Code v0.3.0")]).stdout.strip(), "Taller v0.1.0")

    def test_the_major_number_never_changes_on_its_own(self):
        self.assertEqual(run("Taller", [version("Taller v1.2.0")]).stdout.strip(), "Taller v1.3.0")


class VersionStartProposesTheNumber(unittest.TestCase):
    def skill(self):
        with open(os.path.join(ROOT, "skills", "version-start", "SKILL.md"), encoding="utf-8") as f:
            return f.read()

    def test_the_skill_runs_the_script_to_propose_the_number(self):
        text = self.skill()
        self.assertIn("scripts/next_version.py", text)
        self.assertIn("--fix", text)

    def test_the_skill_no_longer_forbids_computing_the_number(self):
        text = self.skill()
        self.assertNotIn("never compute it yourself", text)
        self.assertNotIn("Ask for the number", text)


if __name__ == "__main__":
    unittest.main()
