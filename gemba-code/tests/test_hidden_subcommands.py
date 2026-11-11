import json
import ast
import os
import shutil
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
          "git lg")
FALLBACK_HIDDEN = HIDDEN[:5] + ("git -c alias.p=push p --force origin main",)
SILENT = ("git status", "git log --oneline -3", "git diff --stat", "echo $P", "ls \"a b\"", "P=push; echo $P")
HOOK_NAMES = tuple(QUOTED)


def run(hook, repo, command, folder=None, env=None):
    script = os.path.join(folder or HOOKS, hook + ".py")
    event = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}, "cwd": repo}
    return subprocess.run([sys.executable, script], input=json.dumps(event), cwd=repo, capture_output=True, text=True, env=env)


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
        shutil.copy(os.path.join(HOOKS, "fallback_words.py"), folder)
        return run(hook, self.repo, command, folder)

    def crashing(self, hook, command):
        folder = tempfile.mkdtemp(dir=self.repo)
        with open(os.path.join(HOOKS, "git_commands.py"), encoding="utf-8") as real, \
                open(os.path.join(folder, "git_commands.py"), "w", encoding="utf-8") as f:
            f.write(real.read() + "\n\ndef git_commands(*a, **k):\n    raise RuntimeError('boom')\n")
        with open(os.path.join(HOOKS, hook + ".py"), encoding="utf-8") as f, \
                open(os.path.join(folder, hook + ".py"), "w", encoding="utf-8") as g:
            g.write(f.read())
        shutil.copy(os.path.join(HOOKS, "fallback_words.py"), folder)
        return run(hook, self.repo, command, folder)

    def test_quoted_and_variable_subcommands_ask_and_git_status_stays_silent(self):
        asks = [command for _, variants in QUOTED.values() for command in variants[:2]] + list(FALLBACK_HIDDEN)
        for hook in HOOK_NAMES:
            for runner in (self.standalone, self.crashing):
                for command in asks:
                    if command in QUOTED[hook][1] or command in FALLBACK_HIDDEN:
                        with self.subTest(hook=hook, runner=runner.__name__, command=command):
                            found = outcome(runner(hook, command))
                            self.assertIsNotNone(found, "printed nothing")
                            self.assertEqual(found[0], "ask")
                for command in ("git status", "echo $P", "git log --format=%H $BASE..HEAD"):
                    with self.subTest(hook=hook, runner=runner.__name__, command=command):
                        self.assertIsNone(outcome(runner(hook, command)))


def anywhere(plain, replacement):
    return plain.replace("git", replacement, 1)


class WrappersAreCheckedOnTheirUnquotedText(Case):
    def test_a_quoted_subcommand_inside_a_wrapper_gets_the_answer_of_the_plain_wrapper(self):
        pairs = {"confirm_push": ("bash -c 'git \"pu\"\"sh\" origin main'", "bash -c 'git push origin main'"),
                 "commit_rules": ("sh -c 'git com\"\"mit -m x'", "sh -c 'git commit -m x'"),
                 "history_rules": ("bash -c 'git pu\"\"sh --force origin main'", "bash -c 'git push --force origin main'"),
                 "integration_rules": ("bash -c 'git \"pu\"\"sh\" origin main'", "bash -c 'git push origin main'"),
                 "branch_rules": ("sh -c 'git swi\"\"tch -c bad'", "sh -c 'git switch -c bad'")}
        for hook, (quoted, plain) in pairs.items():
            expected = outcome(run(hook, self.repo, plain))
            self.assertIsNotNone(expected, f"{hook} should ask about {plain}")
            self.assertEqual(expected[0], "ask")
            with self.subTest(hook=hook):
                self.assertEqual(outcome(run(hook, self.repo, quoted)), expected)


class WrappedVariablesAsk(Case):
    def test_a_wrapped_hidden_subcommand_or_a_program_variable_asks_once(self):
        for hook, (plain, _) in QUOTED.items():
            commands = [plain.replace("git", "$GIT", 1), plain.replace("git", "${GIT}", 1),
                        "sudo " + plain.replace("git", "$GIT", 1), "time " + plain.replace("git", "$GIT", 1)]
            if hook != "branch_rules":
                commands += ["sudo git $P --force origin main", "time git -c alias.p=push p origin main",
                             "env X=1 git lg", "! git $(echo push) origin main", "bash -c 'git $P origin main'"]
            for command in commands:
                with self.subTest(hook=hook, command=command):
                    found = outcome(run(hook, self.repo, command))
                    self.assertIsNotNone(found, "printed nothing")
                    self.assertEqual(found[0], "ask")

    def test_a_variable_elsewhere_in_a_git_command_is_not_a_hidden_subcommand(self):
        for hook in HOOK_NAMES:
            for command in ("git log --format=%H $BASE..HEAD", "sudo git log $BASE", "$EDITOR notes.md", "git status $X"):
                with self.subTest(hook=hook, command=command):
                    self.assertIsNone(outcome(run(hook, self.repo, command)))


class AliasesAreExpanded(Case):
    def setUp(self):
        super().setUp()
        for name, value in (("pf", "push --force"), ("cm", "commit -m bad"), ("sw", "switch -c"), ("st", "status"),
                            ("sh", "!echo hi"), ("pp", "pf"), ("broken", "push \"unclosed")):
            git(self.repo, "config", "alias." + name, value)

    EQUIVALENT = (("git -c alias.p='push --force' p origin main", "git push --force origin main"),
                  ("git -c alias.c='commit -m bad' c", "git commit -m bad"),
                  ("git pf origin main", "git push --force origin main"),
                  ("git cm", "git commit -m bad"),
                  ("git sw bad", "git switch -c bad"),
                  ("git -C . pf origin main", "git -C . push --force origin main"),
                  ("git st", "git status"))

    def test_an_alias_is_judged_like_its_expansion(self):
        for aliased, plain in self.EQUIVALENT:
            answers = [outcome(run(hook, self.repo, plain)) for hook in HOOK_NAMES]
            for hook, expected in zip(HOOK_NAMES, answers):
                with self.subTest(hook=hook, command=aliased):
                    self.assertEqual(outcome(run(hook, self.repo, aliased)), expected)
        self.assertEqual(outcome(run("history_rules", self.repo, self.EQUIVALENT[0][0]))[0], "deny")
        self.assertEqual(outcome(run("commit_rules", self.repo, self.EQUIVALENT[1][0]))[0], "deny")

    def test_a_shell_alias_a_nested_alias_or_an_unreadable_one_asks(self):
        for command in ("git sh", "git pp origin main", "git broken", "git -c alias.a=b -c alias.b=push a"):
            for hook in HOOK_NAMES:
                with self.subTest(hook=hook, command=command):
                    found = outcome(run(hook, self.repo, command))
                    self.assertIsNotNone(found, "printed nothing")
                    self.assertEqual(found[0], "ask")


class WhatIsABuiltin(Case):
    def test_global_options_with_a_value_and_builtins_that_are_not_porcelain_are_silent(self):
        for command in ("git --attr-source HEAD status", "git --config-env a=B status", "git --super-prefix x status",
                        "git --list-cmds=main status", "git -c a=b --attr-source HEAD log", "git init-db", "git upload-pack .",
                        "git receive-pack .", "git upload-archive .", "git daemon --help", "git http-backend",
                        "git credential-cache exit", "git credential-store get", "git merge-recursive a -- b c",
                        "git merge-ours", "git merge-octopus", "git merge-resolve", "git merge-subtree", "git instaweb"):
            for hook in HOOK_NAMES:
                with self.subTest(hook=hook, command=command):
                    self.assertIsNone(outcome(run(hook, self.repo, command)))

    def test_a_known_external_command_still_asks(self):
        for hook in HOOK_NAMES:
            with self.subTest(hook=hook):
                self.assertEqual(outcome(run(hook, self.repo, "git lfs pull"))[0], "ask")


class Cost(Case):
    def shim(self, command, hook):
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        log = os.path.join(folder, "log")
        script = os.path.join(folder, "git")
        with open(script, "w", encoding="utf-8") as f:
            f.write('#!/bin/sh\necho "$@" >> %s\nexec %s "$@"\n' % (log, shutil.which("git")))
        os.chmod(script, 0o755)
        env = dict(os.environ, PATH=folder + os.pathsep + os.environ["PATH"])
        result = run(hook, self.repo, command, env=env)
        called = open(log, encoding="utf-8").read() if os.path.exists(log) else ""
        return outcome(result), called

    def test_literal_builtins_the_hook_does_not_care_about_run_no_git_at_all(self):
        for hook in HOOK_NAMES:
            for command in ("git status", "git log --oneline -3", "git diff --stat", "git add -A && git status",
                            "git --attr-source HEAD status"):
                with self.subTest(hook=hook, command=command):
                    found, called = self.shim(command, hook)
                    self.assertIsNone(found)
                    self.assertEqual(called, "", "the hook ran git")

    def test_confirm_push_walks_the_command_once(self):
        script = (
            "import json, sys\nsys.path.insert(0, sys.argv[1])\nimport git_commands as g, confirm_push\n"
            "walks = []\norig = g.git_commands\n"
            "def counting(command, cwd=None):\n    walks.append(cwd)\n    return orig(command, cwd)\n"
            "g.git_commands = counting\nconfirm_push.main()\nprint(len([w for w in walks if w]), file=sys.stderr)\n")
        for command in ("git push origin develop", "P=push; git $P origin develop", "git status"):
            event = {"tool_name": "Bash", "cwd": self.repo, "tool_input": {"command": command}}
            result = subprocess.run([sys.executable, "-c", script, HOOKS], input=json.dumps(event),
                                    capture_output=True, text=True)
            with self.subTest(command=command):
                self.assertLessEqual(int(result.stderr.strip().splitlines()[-1]), 1, result.stderr)


class OneSharedFallbackModule(unittest.TestCase):
    def test_it_uses_only_the_standard_library_and_the_hooks_do_not_copy_it(self):
        with open(os.path.join(HOOKS, "fallback_words.py"), encoding="utf-8") as f:
            tree = ast.parse(f.read())
        imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        imported |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        self.assertLessEqual(imported, {"re"})
        for hook in HOOK_NAMES:
            with open(os.path.join(HOOKS, hook + ".py"), encoding="utf-8") as f:
                text = f.read()
            self.assertNotIn("def unquoted", text)
            self.assertNotIn("def relevant", text)


if __name__ == "__main__":
    unittest.main()
