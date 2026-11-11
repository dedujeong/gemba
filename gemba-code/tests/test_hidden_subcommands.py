import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_confirm_push_hook import GEMBA_CLAUDE_MD, git, make_repo  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, "hooks")
PULL_REQUEST_MD = GEMBA_CLAUDE_MD.replace("Integration: merge", "Integration: pull request")

# hook -> (plain command it checks, the same command written with quotes or escapes)
QUOTED = {
    "confirm_push": ("git push origin develop", ("git pu\"\"sh origin develop", "git pu\\sh origin develop", "git 'push' origin develop")),
    "commit_rules": ("git commit -m bad", ("git com\"\"mit -m bad", "git com\\mit -m bad", "git \"commit\" -m bad")),
    "branch_rules": ("git switch -c bad", ("git swi\"\"tch -c bad", "git swi\\tch -c bad")),
    "history_rules": ("git push --force origin main", ("git pu\"\"sh --force origin main", "git pu\\sh --force origin main")),
    "integration_rules": ("git push origin develop", ("git pu\"\"sh origin develop", "git pu\\sh origin develop")),
}
HIDDEN = ("P=push; git $P --force origin main", "P=push; git ${P} --force origin main", "P=push; git \"$P\" origin main",
          "git $(echo push) --force origin main", "git `echo push` origin main",
          "git -c alias.p=push p --force origin main", "git lg")
SILENT = ("git status", "git log --oneline -3", "git diff --stat", "echo $P", "ls \"a b\"", "P=push; echo $P")
HOOK_NAMES = tuple(QUOTED)


def run(hook, repo, command, folder=None):
    script = os.path.join(folder or HOOKS, hook + ".py")
    event = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}, "cwd": repo}
    return subprocess.run([sys.executable, script], input=json.dumps(event), cwd=repo, capture_output=True, text=True)


def outcome(result):
    """(decision, reason) of the hook, or None when it printed nothing. Fails on more than one answer."""
    assert result.returncode == 0, result.stderr
    lines = result.stdout.strip().splitlines()
    assert len(lines) <= 1, result.stdout
    if not lines:
        return None
    out = json.loads(lines[0])["hookSpecificOutput"]
    return out["permissionDecision"], out["permissionDecisionReason"]


class Case(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo(PULL_REQUEST_MD)
        self.addCleanup(subprocess.run, ["rm", "-rf", self.repo])


class QuotesAndEscapesAreChecked(Case):
    def test_the_same_command_without_them_gets_the_same_answer(self):
        for hook, (plain, variants) in QUOTED.items():
            expected = outcome(run(hook, self.repo, plain))
            self.assertIsNotNone(expected, f"{hook} should answer for {plain}")
            for command in variants:
                with self.subTest(hook=hook, command=command):
                    self.assertEqual(outcome(run(hook, self.repo, command)), expected)


class HiddenSubcommandsAsk(Case):
    def test_every_hook_asks_once_with_a_generic_reason(self):
        for hook in HOOK_NAMES:
            for command in HIDDEN:
                with self.subTest(hook=hook, command=command):
                    found = outcome(run(hook, self.repo, command))
                    self.assertIsNotNone(found, "printed nothing")
                    self.assertEqual(found[0], "ask")

    def test_outside_a_project_with_setup_nothing_is_asked(self):
        plain = make_repo(None)
        self.addCleanup(subprocess.run, ["rm", "-rf", plain])
        for hook in HOOK_NAMES:
            for command in HIDDEN:
                with self.subTest(hook=hook, command=command):
                    self.assertIsNone(outcome(run(hook, plain, command)))

    def test_a_git_builtin_or_a_command_without_git_stays_silent(self):
        for hook in HOOK_NAMES:
            for command in SILENT:
                with self.subTest(hook=hook, command=command):
                    self.assertIsNone(outcome(run(hook, self.repo, command)))


class FallbacksCoverTheSameCommands(Case):
    def standalone(self, hook, command):
        """The hook alone in a folder: its parser module cannot be imported."""
        folder = tempfile.mkdtemp(dir=self.repo)
        with open(os.path.join(HOOKS, hook + ".py"), encoding="utf-8") as f, \
                open(os.path.join(folder, hook + ".py"), "w", encoding="utf-8") as g:
            g.write(f.read())
        return run(hook, self.repo, command, folder)

    def crashing(self, hook, command):
        folder = tempfile.mkdtemp(dir=self.repo)
        with open(os.path.join(HOOKS, "git_commands.py"), encoding="utf-8") as real, \
                open(os.path.join(folder, "git_commands.py"), "w", encoding="utf-8") as f:
            f.write(real.read() + "\n\ndef git_commands(*a, **k):\n    raise RuntimeError('boom')\n")
        with open(os.path.join(HOOKS, hook + ".py"), encoding="utf-8") as f, \
                open(os.path.join(folder, hook + ".py"), "w", encoding="utf-8") as g:
            g.write(f.read())
        return run(hook, self.repo, command, folder)

    def test_quoted_and_variable_subcommands_ask_and_git_status_stays_silent(self):
        asks = [command for _, variants in QUOTED.values() for command in variants[:2]] + list(HIDDEN[:6])
        for hook in HOOK_NAMES:
            for runner in (self.standalone, self.crashing):
                for command in asks:
                    if command in QUOTED[hook][1] or command in HIDDEN:
                        with self.subTest(hook=hook, runner=runner.__name__, command=command):
                            found = outcome(runner(hook, command))
                            self.assertIsNotNone(found, "printed nothing")
                            self.assertEqual(found[0], "ask")
                for command in ("git status", "echo $P"):
                    with self.subTest(hook=hook, runner=runner.__name__, command=command):
                        self.assertIsNone(outcome(runner(hook, command)))


if __name__ == "__main__":
    unittest.main()
