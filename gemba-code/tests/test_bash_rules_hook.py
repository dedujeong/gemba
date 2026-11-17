import importlib
import json
import os
import re
import subprocess
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_confirm_push_hook import decision, git, make_repo  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, "hooks")
SCRIPT = os.path.join(HOOKS, "bash_rules.py")
RULES = ("confirm_push", "commit_rules", "branch_rules", "history_rules", "integration_rules")

CRASH = """
import sys
sys.path.insert(0, sys.argv[1])
import importlib
for name in sys.argv[2:]:
    def boom(*args):
        raise RuntimeError("forced crash")
    importlib.import_module(name).decide = boom
import bash_rules
bash_rules.main()
"""


def event_of(repo, command):
    return {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}, "cwd": repo}


def run_dispatcher(repo, command, script=SCRIPT, tool="Bash"):
    event = event_of(repo, command)
    event["tool_name"] = tool
    return subprocess.run([sys.executable, script], input=json.dumps(event), cwd=repo, capture_output=True, text=True)


def run_with_crashes(repo, command, *crashing):
    return subprocess.run([sys.executable, "-c", CRASH, HOOKS, *crashing], input=json.dumps(event_of(repo, command)),
                          cwd=repo, capture_output=True, text=True)


class OneAnswer(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", self.repo])

    def answer(self, command):
        result = run_dispatcher(self.repo, command)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLessEqual(len(result.stdout.strip().splitlines()), 1, "more than one JSON answer")
        return decision(result)

    def test_prints_nothing_for_a_command_no_rule_decides_on(self):
        self.assertEqual(run_dispatcher(self.repo, "ls").stdout, "")
        self.assertIsNone(self.answer("git status"))

    def test_prints_nothing_for_a_tool_that_is_not_bash_or_bad_input(self):
        self.assertEqual(run_dispatcher(self.repo, "git push origin develop", tool="Read").stdout, "")
        result = subprocess.run([sys.executable, SCRIPT], input="not json", capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout.strip()), (0, ""))

    def test_a_single_rule_decides_as_it_does_alone(self):
        out = self.answer("git push origin develop")
        self.assertEqual(out["permissionDecision"], "ask")
        self.assertIn("git push: develop to remote origin", out["permissionDecisionReason"])

    def test_deny_wins_over_ask_and_the_reasons_are_joined(self):
        # confirm_push asks about the push, history denies the force push.
        out = self.answer("git push --force origin develop")
        self.assertEqual(out["permissionDecision"], "deny")
        reason = out["permissionDecisionReason"]
        self.assertIn("Gemba rule (history): a force push rewrites the history of the remote", reason)
        self.assertIn("git push: develop to remote origin", reason)

    def test_several_denials_are_joined(self):
        git(self.repo, "checkout", "-q", "-b", "story/ABC-1-a")
        # commit rules: bad message, branch rules: bad name (denied both)
        out = self.answer('git commit -m "Bad message" && git switch -c wrong-name')
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("Gemba rule (commits)", out["permissionDecisionReason"])
        self.assertIn("Gemba rule (branches)", out["permissionDecisionReason"])

    def test_several_questions_are_asked_together(self):
        git(self.repo, "checkout", "-q", "-b", "story/ABC-1-a")
        out = self.answer("git push origin develop && git commit")
        self.assertEqual(out["permissionDecision"], "ask")
        self.assertIn("git push: develop", out["permissionDecisionReason"])
        self.assertIn("Gemba rule (commits)", out["permissionDecisionReason"])


class FailsClosed(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", self.repo])

    def test_a_crashing_rule_asks_for_what_it_checks_and_the_others_still_run(self):
        result = run_with_crashes(self.repo, "git push origin develop", "confirm_push")
        out = decision(result)
        self.assertEqual(out["permissionDecision"], "ask")
        self.assertIn("could not read the branch and the remote", out["permissionDecisionReason"])
        result = run_with_crashes(self.repo, "git push --force origin develop", "confirm_push")
        out = decision(result)
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("a force push rewrites the history", out["permissionDecisionReason"])
        self.assertIn("could not read the branch and the remote", out["permissionDecisionReason"])

    def test_a_crashing_rule_stays_quiet_for_a_command_it_does_not_check(self):
        self.assertEqual(run_with_crashes(self.repo, "git status", *RULES).stdout, "")
        self.assertEqual(run_with_crashes(self.repo, "ls", *RULES).stdout, "")
        git(self.repo, "checkout", "-q", "-b", "story/ABC-1-a")
        self.assertEqual(run_with_crashes(self.repo, 'git commit -m "feat(hooks): x"', "history_rules").stdout, "")

    def test_every_rule_that_crashes_asks_with_its_own_reason(self):
        for rule, command, prefix in (("commit_rules", "git commit -m 'x'", "Gemba rule (commits)"),
                                      ("branch_rules", "git switch -c a", "Gemba rule (branches)"),
                                      ("history_rules", "git rebase main", "Gemba rule (history)"),
                                      ("integration_rules", "gh pr merge 3", "Gemba rule (integration")):
            with self.subTest(rule=rule):
                out = decision(run_with_crashes(self.repo, command, rule))
                self.assertEqual(out["permissionDecision"], "ask")
                self.assertIn(prefix, out["permissionDecisionReason"])

    def test_a_missing_parser_asks_for_any_command_a_rule_would_check(self):
        import shutil
        import tempfile
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        for name in RULES + ("bash_rules", "fallback_words"):
            shutil.copy(os.path.join(HOOKS, name + ".py"), folder)
        script = os.path.join(folder, "bash_rules.py")
        for command, expected in (("git push origin develop", "ask"), ("git commit -m 'x'", "ask"),
                                  ("git switch -c a", "ask"), ("git rebase main", "ask"), ("gh pr merge 3", "ask"),
                                  ("git status", None), ("ls", None)):
            with self.subTest(command=command):
                out = decision(run_dispatcher(self.repo, command, script=script))
                self.assertEqual(out and out["permissionDecision"], expected)

    def test_a_missing_rule_asks_like_a_crash(self):
        import shutil
        import tempfile
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        for name in RULES + ("bash_rules", "fallback_words", "git_commands"):
            shutil.copy(os.path.join(HOOKS, name + ".py"), folder)
        os.remove(os.path.join(folder, "history_rules.py"))
        script = os.path.join(folder, "bash_rules.py")
        out = decision(run_dispatcher(self.repo, "git rebase main", script=script))
        self.assertEqual(out["permissionDecision"], "ask")
        self.assertIsNone(decision(run_dispatcher(self.repo, "git status", script=script)))


class EachRuleDecides(unittest.TestCase):
    """Every rule script keeps `decide(event) -> (decision, reason) | None` and its `main()`."""

    def setUp(self):
        self.repo = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", self.repo])
        sys.path.insert(0, HOOKS)
        self.addCleanup(sys.path.remove, HOOKS)
        self.git_commands = importlib.import_module("git_commands")

    def rule(self, name):
        module = importlib.import_module(name)
        module.git_commands = self.git_commands
        self.assertTrue(callable(module.main))
        return module

    def test_decide_returns_the_decision_and_prints_nothing(self):
        for name, command, expected in (("confirm_push", "git push origin develop", "ask"),
                                        ("history_rules", "git push --force origin develop", "deny"),
                                        ("integration_rules", "git push origin story/ABC-1-a", "deny"),
                                        ("commit_rules", 'git commit -m "Bad"', "deny"),
                                        ("branch_rules", "git switch -c wrong", "deny")):
            with self.subTest(rule=name), mock.patch("builtins.print") as printed:
                found = self.rule(name).decide(event_of(self.repo, command))
                self.assertEqual(found[0], expected)
                self.assertTrue(found[1])
                printed.assert_not_called()

    def test_decide_returns_none_when_the_rule_has_nothing_to_say(self):
        for name in RULES:
            with self.subTest(rule=name):
                self.assertIsNone(self.rule(name).decide(event_of(self.repo, "git status")))


class SharedConstants(unittest.TestCase):
    def test_the_protected_branches_live_in_one_place(self):
        sys.path.insert(0, HOOKS)
        self.addCleanup(sys.path.remove, HOOKS)
        fallback_words = importlib.import_module("fallback_words")
        git_commands = importlib.import_module("git_commands")
        self.assertEqual(set(git_commands.PROTECTED_BRANCHES), {"develop", "main"})
        self.assertIs(git_commands.PROTECTED_BRANCHES, fallback_words.PROTECTED_BRANCHES)
        for name in RULES:
            with open(os.path.join(HOOKS, name + ".py"), encoding="utf-8") as f:
                source = f.read()
            self.assertIsNone(re.search(r"""\(\s*["'](?:develop|main)["']\s*,\s*["'](?:develop|main)["']\s*\)""", source),
                              f"{name} repeats the protected branches")

    def test_the_remote_rule_is_read_from_git_commands_only(self):
        for name in RULES:
            with open(os.path.join(HOOKS, name + ".py"), encoding="utf-8") as f:
                source = f.read()
            self.assertNotIn("def syncs_with_its_remote", source, name)


class RelevancePatterns(unittest.TestCase):
    def test_every_rule_script_reads_the_pattern_the_dispatcher_falls_back_on(self):
        sys.path.insert(0, HOOKS)
        self.addCleanup(sys.path.remove, HOOKS)
        fallback_words = importlib.import_module("fallback_words")
        for name, attribute in (("confirm_push", "MENTIONS_A_PUSH"), ("commit_rules", "CREATING_WORDS"),
                                ("branch_rules", "CREATING"), ("history_rules", "OPERATION_WORDS"),
                                ("integration_rules", "RELEVANT")):
            with self.subTest(rule=name):
                self.assertEqual(getattr(importlib.import_module(name), attribute).pattern,
                                 fallback_words.RULES[name].pattern.pattern)


class FewGitCalls(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", self.repo])
        sys.path.insert(0, HOOKS)
        self.addCleanup(sys.path.remove, HOOKS)

    def calls(self, name, command):
        """The git processes one in-process decision spawns, with every repository cache empty."""
        git_commands = importlib.import_module("git_commands")
        for function in vars(git_commands).values():
            if hasattr(function, "cache_clear"):
                function.cache_clear()
        real = subprocess.run
        spawned = []

        def counting(args, *rest, **kwargs):
            spawned.append(args)
            return real(args, *rest, **kwargs)

        with mock.patch.object(git_commands.subprocess, "run", counting):
            if name == "bash_rules":
                importlib.import_module("bash_rules").decide(event_of(self.repo, command))
            else:
                module = importlib.import_module(name)
                module.git_commands = git_commands
                module.decide(event_of(self.repo, command))
        return len(spawned)

    def test_a_plain_git_status_spawns_at_most_the_git_calls_of_one_rule_set(self):
        one_rule_set = max(self.calls(name, "git status") for name in RULES)
        through_the_dispatcher = self.calls("bash_rules", "git status")
        self.assertLessEqual(through_the_dispatcher, one_rule_set)

    def test_a_command_spawns_no_more_git_calls_than_the_five_rules_share(self):
        command = "git push origin develop"
        alone = sum(self.calls(name, command) for name in RULES)
        self.assertLess(self.calls("bash_rules", command), alone)


class RegisteredInThePlugin(unittest.TestCase):
    def bash_commands(self):
        with open(os.path.join(HOOKS, "hooks.json"), encoding="utf-8") as f:
            entries = json.load(f)["hooks"]["PreToolUse"]
        return [h["command"] for e in entries if e.get("matcher") == "Bash" for h in e["hooks"] if h["type"] == "command"]

    def test_one_python_process_runs_every_bash_rule(self):
        self.assertEqual(self.bash_commands(), ['python3 "${CLAUDE_PLUGIN_ROOT}/hooks/bash_rules.py"'])

    def test_the_dispatcher_runs_every_rule_script(self):
        with open(SCRIPT, encoding="utf-8") as f:
            source = f.read()
        for name in RULES:
            self.assertIn(f'"{name}"', source)

    def test_the_mcp_entry_and_session_start_stay(self):
        with open(os.path.join(HOOKS, "hooks.json"), encoding="utf-8") as f:
            hooks = json.load(f)["hooks"]
        self.assertIn("SessionStart", hooks)
        matchers = [e["matcher"] for e in hooks["PreToolUse"]]
        self.assertIn("mcp__.*__(createJiraIssue|executeWrite)", matchers)


if __name__ == "__main__":
    unittest.main()
