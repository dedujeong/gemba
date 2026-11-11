import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_confirm_push_hook import SCRIPT, decision, make_repo, run_hook


class AsksEvenWhenTheSharedModuleCannotBeImported(unittest.TestCase):
    def test_a_push_asks_when_git_commands_is_missing(self):
        alone = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, alone)
        script = os.path.join(alone, "confirm_push.py")
        shutil.copy(SCRIPT, script)
        repo = make_repo()
        self.addCleanup(shutil.rmtree, repo)
        event = '{"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "git push origin develop"}, "cwd": "%s"}' % repo
        result = subprocess.run([sys.executable, script], input=event, cwd=repo, capture_output=True, text=True)
        out = decision(result)
        self.assertIsNotNone(out, result.stderr)
        self.assertEqual(out["permissionDecision"], "ask")


class ReadsTheProjectOfTheDashCFolder(unittest.TestCase):
    def test_a_push_to_a_gemba_project_from_outside_it_asks(self):
        gemba = make_repo()
        outside = make_repo(claude_md=None)
        self.addCleanup(shutil.rmtree, gemba)
        self.addCleanup(shutil.rmtree, outside)
        out = decision(run_hook(outside, "git -C %s push origin develop" % gemba))
        self.assertIsNotNone(out)
        self.assertEqual(out["permissionDecision"], "ask")
        self.assertIn("develop", out["permissionDecisionReason"])


class UsesTheContextOfTheCompoundCommand(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo()
        self.addCleanup(shutil.rmtree, self.repo)

    def test_a_bare_push_names_the_branch_the_command_switched_to(self):
        out = decision(run_hook(self.repo, "git switch -c task/ABC-9-x && git push"))
        self.assertIn("task/ABC-9-x", out["permissionDecisionReason"])

    def test_a_push_after_a_cd_reads_the_project_of_that_folder(self):
        other = make_repo()
        outside = make_repo(claude_md=None)
        self.addCleanup(shutil.rmtree, other)
        self.addCleanup(shutil.rmtree, outside)
        out = decision(run_hook(outside, "cd %s && git push" % other))
        self.assertEqual(out["permissionDecision"], "ask")

    def test_a_push_after_a_cd_that_cannot_be_followed_asks(self):
        out = decision(run_hook(self.repo, "cd $DIR && git push"))
        self.assertEqual(out["permissionDecision"], "ask")

    def test_a_wrapped_push_next_to_a_parsed_command_asks(self):
        out = decision(run_hook(self.repo, "git status && bash -c 'git push --force'"))
        self.assertEqual(out["permissionDecision"], "ask")

    def test_a_push_mentioned_in_the_argument_of_another_git_command_does_not_ask(self):
        self.assertIsNone(decision(run_hook(self.repo, 'git log --grep push')))
        self.assertIsNone(decision(run_hook(self.repo, 'git commit -m "git push later"')))


if __name__ == "__main__":
    unittest.main()
