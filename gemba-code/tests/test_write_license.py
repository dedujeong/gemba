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
