import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "skills", "setup", "scripts", "write_license.py")

# Stand-ins for the official texts: the plugin keeps no copy of the real ones.
FAKE_MIT = "MIT License\n\nCopyright (c) <year> <copyright holders>\n\nStand-in permission text.\n"
FAKE_APACHE = "Apache License\nVersion 2.0\n\nStand-in terms.\n"


def run(license_name, files=None, sources=None, holder="Ana Pérez", year="2026", extra=()):
    """Runs the script on a temp repo; files are the ones the repo already has, sources the official texts it can read."""
    with tempfile.TemporaryDirectory() as folder:
        repo = os.path.join(folder, "repo")
        source = os.path.join(folder, "source")
        os.makedirs(repo)
        os.makedirs(source)
        for name, text in (files or {}).items():
            with open(os.path.join(repo, name), "w", encoding="utf-8", newline="") as f:
                f.write(text)
        for name, text in (sources if sources is not None else {"MIT.txt": FAKE_MIT, "Apache-2.0.txt": FAKE_APACHE}).items():
            with open(os.path.join(source, name), "w", encoding="utf-8", newline="") as f:
                f.write(text)
        cmd = [sys.executable, SCRIPT, repo, license_name, "--holder", holder, "--year", year,
               "--product", "Taller", "--source-dir", source, *extra]
        result = subprocess.run(cmd, capture_output=True, text=True)
        written = {}
        for name in sorted(os.listdir(repo)):
            with open(os.path.join(repo, name), encoding="utf-8", newline="") as f:
                written[name] = f.read()
        return result, written


class WriteTheLicense(unittest.TestCase):
    def test_mit_puts_the_holder_and_the_year_inside_the_license(self):
        result, written = run("MIT")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(written["LICENSE"], "MIT License\n\nCopyright (c) 2026 Ana Pérez\n\nStand-in permission text.\n")

    def test_mit_creates_no_notice(self):
        _, written = run("MIT")
        self.assertEqual(list(written), ["LICENSE"])

    def test_apache_writes_the_official_text_as_it_is(self):
        result, written = run("Apache-2.0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(written["LICENSE"], FAKE_APACHE)

    def test_none_writes_no_license_and_no_notice(self):
        result, written = run("none")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(written, {})

    def test_an_existing_license_is_left_byte_for_byte(self):
        mine = "My own terms\r\nno final newline"
        result, written = run("MIT", files={"LICENSE": mine})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(written, {"LICENSE": mine})
        self.assertIn("already exists", result.stdout)

    def test_a_text_that_cannot_be_read_writes_nothing_and_says_what_is_missing(self):
        result, written = run("MIT", sources={})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(written, {})
        self.assertIn("MIT", result.stderr)
        self.assertIn("https://", result.stderr)
        self.assertIn("nothing was written", result.stderr)


class WriteTheNotice(unittest.TestCase):
    def test_apache_writes_the_notice_from_the_template_with_the_confirmed_data(self):
        result, written = run("Apache-2.0", extra=("--holder-url", "https://github.com/ana"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(written["NOTICE"], "Taller\nCopyright 2026 Ana Pérez (https://github.com/ana)\n")
        self.assertEqual(written["LICENSE"], FAKE_APACHE)

    def test_without_a_holder_url_the_parentheses_are_left_out(self):
        _, written = run("Apache-2.0")
        self.assertEqual(written["NOTICE"], "Taller\nCopyright 2026 Ana Pérez\n")

    def test_an_existing_notice_is_left_byte_for_byte(self):
        mine = "Mine\r\nno final newline"
        result, written = run("Apache-2.0", files={"NOTICE": mine})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(written["NOTICE"], mine)
        self.assertEqual(written["LICENSE"], FAKE_APACHE)
        self.assertIn("NOTICE already exists", result.stdout)

    def test_a_license_that_exists_means_no_notice_is_written(self):
        _, written = run("Apache-2.0", files={"LICENSE": "Other terms\n"})
        self.assertEqual(written, {"LICENSE": "Other terms\n"})

    def test_when_the_text_cannot_be_read_no_notice_is_written_either(self):
        result, written = run("Apache-2.0", sources={})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(written, {})

    def test_the_template_of_the_notice_has_its_four_fields(self):
        with open(os.path.join(ROOT, "skills", "setup", "assets", "notice.md"), encoding="utf-8") as f:
            text = f.read()
        for field in ("<Product name>", "<year>", "<holder>", "<holder URL>"):
            self.assertIn(field, text)


class ThePluginKeepsNoLicenseText(unittest.TestCase):
    def test_no_file_of_the_plugin_holds_the_text_of_a_license(self):
        marks = ("Permission is hereby granted", "TERMS AND CONDITIONS FOR USE, REPRODUCTION")
        found = []
        for folder, dirs, names in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in ("results", "__pycache__", "tests")]
            for name in names:
                path = os.path.join(folder, name)
                try:
                    with open(path, encoding="utf-8") as f:
                        text = f.read()
                except (UnicodeDecodeError, OSError):
                    continue
                if any(mark in text for mark in marks):
                    found.append(os.path.relpath(path, ROOT))
        self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()
