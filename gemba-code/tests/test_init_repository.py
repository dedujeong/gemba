import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "skills", "setup", "scripts", "init_repository.py")
SKILL = os.path.join(ROOT, "skills", "setup", "SKILL.md")

IDENTITY = {"GIT_AUTHOR_NAME": "Maintainer", "GIT_AUTHOR_EMAIL": "maintainer@example.com",
            "GIT_COMMITTER_NAME": "Maintainer", "GIT_COMMITTER_EMAIL": "maintainer@example.com"}


def git(folder, *args):
    result = subprocess.run(["git", "-C", folder, *args], capture_output=True, text=True,
                            env={**os.environ, **IDENTITY})
    return result.stdout.strip()


def run(folder):
    return subprocess.run([sys.executable, SCRIPT, folder], capture_output=True, text=True,
                          env={**os.environ, **IDENTITY})


def skill():
    with open(SKILL, encoding="utf-8") as f:
        return f.read()


class TempFolder(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.folder)

    def make_origin(self):
        """A repository with main and a develop one commit ahead, to clone from."""
        origin = os.path.join(self.folder, "origin")
        os.mkdir(origin)
        git(origin, "init", "-q", "-b", "main")
        git(origin, "commit", "-q", "--allow-empty", "-m", "initial commit")
        git(origin, "branch", "develop")
        git(origin, "switch", "-q", "develop")
        git(origin, "commit", "-q", "--allow-empty", "-m", "feat: add z")
        return origin


class InitRepository(TempFolder):

    def branches(self):
        return sorted(git(self.folder, "branch", "--format=%(refname:short)").split())

    def test_a_folder_without_a_repository_gets_main_with_an_empty_initial_commit_and_develop(self):
        with open(os.path.join(self.folder, "notes.txt"), "w", encoding="utf-8") as f:
            f.write("not committed\n")
        result = run(self.folder)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.branches(), ["develop", "main"])
        self.assertEqual(git(self.folder, "log", "--format=%s", "main"), "initial commit")
        self.assertEqual(git(self.folder, "show", "--format=", "--name-only", "main"), "")
        self.assertEqual(git(self.folder, "rev-parse", "develop"), git(self.folder, "rev-parse", "main"))
        self.assertEqual(git(self.folder, "branch", "--show-current"), "main")
        self.assertIn("notes.txt", git(self.folder, "status", "--porcelain"))

    def test_a_repository_without_commits_is_treated_as_new(self):
        git(self.folder, "init", "-q", "-b", "main")
        result = run(self.folder)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.branches(), ["develop", "main"])
        self.assertEqual(git(self.folder, "log", "--format=%s", "main"), "initial commit")

    def test_a_repository_without_develop_gets_develop_from_main(self):
        git(self.folder, "init", "-q", "-b", "main")
        git(self.folder, "commit", "-q", "--allow-empty", "-m", "initial commit")
        git(self.folder, "commit", "-q", "--allow-empty", "-m", "feat: add x")
        main = git(self.folder, "rev-parse", "main")
        result = run(self.folder)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.branches(), ["develop", "main"])
        self.assertEqual(git(self.folder, "rev-parse", "develop"), main)
        self.assertEqual(git(self.folder, "rev-parse", "main"), main)

    def test_a_repository_with_main_and_develop_keeps_its_branches_and_history(self):
        git(self.folder, "init", "-q", "-b", "main")
        git(self.folder, "commit", "-q", "--allow-empty", "-m", "initial commit")
        git(self.folder, "branch", "develop")
        git(self.folder, "switch", "-q", "develop")
        git(self.folder, "commit", "-q", "--allow-empty", "-m", "feat: add y")
        before = {b: git(self.folder, "rev-parse", b) for b in ("main", "develop")}
        result = run(self.folder)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.branches(), ["develop", "main"])
        self.assertEqual({b: git(self.folder, "rev-parse", b) for b in ("main", "develop")}, before)
        self.assertEqual(git(self.folder, "branch", "--show-current"), "develop")

    def test_a_repository_with_commits_but_no_main_is_left_alone_and_asks(self):
        git(self.folder, "init", "-q", "-b", "master")
        git(self.folder, "commit", "-q", "--allow-empty", "-m", "initial commit")
        result = run(self.folder)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("main", result.stdout + result.stderr)
        self.assertEqual(self.branches(), ["master"])


class ClonesAndIdentity(TempFolder):

    def test_a_clone_gets_its_local_main_and_develop_from_the_remote_ones(self):
        origin = self.make_origin()
        clone = os.path.join(self.folder, "clone")
        subprocess.run(["git", "clone", "-q", "-b", "develop", origin, clone], check=True)
        result = run(clone)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(git(clone, "rev-parse", "main"), git(origin, "rev-parse", "main"))
        self.assertEqual(git(clone, "rev-parse", "develop"), git(origin, "rev-parse", "develop"))

    def test_without_a_git_identity_it_says_so_and_asks_for_one(self):
        home = os.path.join(self.folder, "home")
        os.mkdir(home)
        project = os.path.join(self.folder, "project")
        os.mkdir(project)
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env.update({"HOME": home, "XDG_CONFIG_HOME": home, "GIT_CONFIG_NOSYSTEM": "1", "EMAIL": ""})
        result = subprocess.run([sys.executable, SCRIPT, project], capture_output=True, text=True, env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stdout.startswith("git has no identity"), result.stdout)
        self.assertIn("ask the person for the name and email", result.stdout)


class FailedBranches(TempFolder):

    def lock(self, repo, branch):
        heads = os.path.join(repo, ".git", "refs", "heads")
        os.makedirs(heads, exist_ok=True)
        open(os.path.join(heads, f"{branch}.lock"), "w").close()

    def test_a_develop_that_cannot_be_created_after_the_initial_commit_fails(self):
        git(self.folder, "init", "-q", "-b", "main")
        self.lock(self.folder, "develop")
        result = run(self.folder)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("develop", result.stdout)

    def test_a_branch_that_cannot_be_created_from_the_remote_fails_instead_of_using_main(self):
        origin = self.make_origin()
        clone = os.path.join(self.folder, "clone")
        subprocess.run(["git", "clone", "-q", "-b", "main", origin, clone], check=True)
        self.lock(clone, "develop")
        result = run(clone)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("origin/develop", result.stdout)
        self.assertEqual(git(clone, "branch", "--list", "develop"), "")


class SetupPreparesTheRepositoryFirst(unittest.TestCase):
    def test_the_first_step_runs_the_script_and_never_renames_a_branch(self):
        text = skill()
        step = text.split("## 1. Prepare the repository")[1].split("## 2. ")[0]
        self.assertIn("scripts/init_repository.py", step)
        self.assertIn("never rename", step)
        self.assertIn("ask", step)
        self.assertLess(text.index("## 1. Prepare the repository"), text.index("## 2. Read what is there"))

    def test_the_report_says_what_was_done_with_the_repository(self):
        report = skill().split("## 11. Report")[1]
        self.assertIn("repository", report)


class CommitExceptionInTheMethod(unittest.TestCase):
    def test_the_commit_rule_names_the_initial_commit_in_lowercase(self):
        with open(os.path.join(ROOT, "references", "context.md"), encoding="utf-8") as f:
            rule = next(line for line in f if line.startswith("- One line, with no body or footer"))
        self.assertIn("a repository's `initial commit`", rule)
        self.assertNotIn("Initial commit", rule)


if __name__ == "__main__":
    unittest.main()
