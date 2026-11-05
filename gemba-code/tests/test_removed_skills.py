import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def exists(*parts):
    return os.path.exists(os.path.join(ROOT, *parts))


def evals_that_fire(skill_name):
    evals = os.path.join(ROOT, "evals")
    found = []
    for name in sorted(os.listdir(evals)):
        grader = os.path.join(evals, name, "graders", "skill-fired.md")
        if os.path.isfile(grader):
            with open(grader, encoding="utf-8") as f:
                if skill_name in f.read():
                    found.append(name)
    return found


class VersionStartLivesInGembaProduct(unittest.TestCase):
    def test_the_skill_is_not_in_gemba_code(self):
        self.assertFalse(exists("skills", "version-start"))

    def test_its_scripts_have_no_tests_left(self):
        for name in ("next_version", "read_release", "write_keys"):
            self.assertFalse(exists("tests", f"test_{name}.py"), name)

    def test_no_eval_fires_it(self):
        self.assertEqual(evals_that_fire("version-start"), [])


class VersionCloseLivesInGembaProduct(unittest.TestCase):
    def test_the_skill_is_not_in_gemba_code(self):
        self.assertFalse(exists("skills", "version-close"))

    def test_no_eval_fires_it(self):
        self.assertEqual(evals_that_fire("version-close"), [])


if __name__ == "__main__":
    unittest.main()
