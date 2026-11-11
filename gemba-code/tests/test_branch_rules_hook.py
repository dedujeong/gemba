import json
import os
import subprocess
import sys
import unittest

from test_confirm_push_hook import GEMBA_CLAUDE_MD, git, make_repo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "hooks", "branch_rules.py")


def run_hook(repo, command, tool="Bash", env=None):
    """Runs the hook the way Claude Code does: JSON on stdin, in the project."""
    event = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {"command": command}, "cwd": repo}
    return subprocess.run([sys.executable, SCRIPT], input=json.dumps(event), cwd=repo,
                          capture_output=True, text=True, env=env)


def decision(result):
    if not result.stdout.strip():
        return None
    return json.loads(result.stdout)["hookSpecificOutput"]


class HookTestCase(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", self.repo])

    def decide(self, command, repo=None):
        result = run_hook(repo or self.repo, command)
        self.assertEqual(result.returncode, 0, result.stderr)
        out = decision(result)
        if out is not None:
            self.assertEqual(out["hookEventName"], "PreToolUse")
        return out

    def denied(self, command):
        out = self.decide(command)
        self.assertIsNotNone(out, "the hook printed nothing for: " + command)
        self.assertEqual(out["permissionDecision"], "deny", command)
        return out["permissionDecisionReason"]

    def asked(self, command):
        out = self.decide(command)
        self.assertIsNotNone(out, "the hook printed nothing for: " + command)
        self.assertEqual(out["permissionDecision"], "ask", command)
        return out["permissionDecisionReason"]

    def passes(self, command, repo=None):
        self.assertIsNone(self.decide(command, repo), command)


class BlocksABadName(HookTestCase):
    def test_every_way_to_create_a_branch_is_checked(self):
        for command in ("git switch -c feature/login", "git switch --create feature/login",
                        "git switch -C feature/login", "git switch --force-create feature/login",
                        "git checkout -b feature/login", "git checkout -B feature/login",
                        "git branch feature/login", "git branch feature/login develop",
                        "git worktree add -b feature/login ../w develop",
                        "git worktree add -B feature/login ../w develop",
                        "git -C . switch -c feature/login"):
            with self.subTest(command=command):
                self.denied(command)

    def test_a_rename_is_checked_by_its_new_name(self):
        for command in ("git branch -m feature/login", "git branch -M old feature/login",
                        "git branch -m story/ABC-1-a feature/login"):
            with self.subTest(command=command):
                self.denied(command)

    def test_the_reason_names_the_rule_and_says_what_to_do(self):
        reason = self.denied("git switch -c feature/login")
        self.assertTrue(reason.startswith("Gemba rule (branches): "), reason)
        self.assertIn("<type>/<KEY>-<slug>", reason)
        self.assertIn("story, task, bug or spike", reason)
        self.assertIn("feature/login", reason)
        self.assertIn("story/ABC-12-short-slug", reason)

    def test_every_name_that_breaks_the_form_is_denied(self):
        for name in ("main", "story/login", "story/ABC-login", "epic/ABC-1-login", "Story/ABC-1-login",
                     "story/abc-1-login", "story/ABC-1", "story/ABC-1-Login", "story/ABC-1-login-",
                     "story/ABC-1--login", "story/ABC-1-log_in", "story/ABC-1-login/extra", "story/1-login"):
            with self.subTest(name=name):
                self.denied(f"git switch -c {name}")

    def test_a_compound_command_is_denied_for_its_bad_branch(self):
        self.denied("git status && git checkout -b feature/login")


class PassesAValidName(HookTestCase):
    def test_valid_names_of_the_four_types_print_nothing(self):
        for name in ("story/ABC-12-login", "task/ABC-3-add-tests", "bug/AB2-45-fix-the-crash", "spike/ABC-9-try-x2"):
            with self.subTest(name=name):
                self.passes(f"git switch -c {name} develop")
                self.passes(f"git branch -m {name}")

    def test_commands_that_do_not_create_or_rename_a_branch_print_nothing(self):
        for command in ("git branch", "git branch --show-current", "git branch -a", "git branch -vv",
                        "git branch --list feature/*", "git branch -d feature/login", "git branch -D feature/login",
                        "git branch --contains abc123", "git branch -u origin/develop",
                        "git branch --set-upstream-to=origin/develop", "git branch -c old feature/login",
                        "git checkout develop", "git checkout feature/login", "git switch feature/login",
                        "git checkout -- file.txt", "git worktree add ../w develop", "git worktree list",
                        "git commit -m 'fix branch handling'", "git status"):
            with self.subTest(command=command):
                self.passes(command)

    def test_a_tool_that_is_not_bash_prints_nothing(self):
        result = run_hook(self.repo, "git switch -c feature/login", tool="Edit")
        self.assertEqual(result.stdout.strip(), "")

    def test_a_project_without_the_gemba_section_prints_nothing(self):
        other = make_repo(claude_md="# Notes\n")
        self.addCleanup(subprocess.run, ["rm", "-rf", other])
        self.passes("git switch -c feature/login", other)
        self.passes("bash -c 'git switch -c feature/login'", other)

    def test_the_project_is_found_from_a_subfolder(self):
        sub = os.path.join(self.repo, "src")
        os.mkdir(sub)
        out = decision(run_hook(sub, "git switch -c feature/login"))
        self.assertEqual(out["permissionDecision"], "deny")

    def test_a_project_without_setup_is_found_from_the_session_folder(self):
        other = make_repo(claude_md="# Notes\n")
        self.addCleanup(subprocess.run, ["rm", "-rf", other])
        event = {"tool_name": "Bash", "cwd": self.repo,
                 "tool_input": {"command": f"git -C {other} switch -c feature/login"}}
        result = subprocess.run([sys.executable, SCRIPT], input=json.dumps(event), capture_output=True, text=True)
        self.assertEqual(decision(result)["permissionDecision"], "deny")


class AsksWhenItCannotRead(HookTestCase):
    def test_a_wrapped_creation_asks_with_a_generic_reason(self):
        for command in ("bash -c 'git switch -c feature/login'", "sudo git checkout -b feature/login",
                        'bash -c "git branch feature/login"', "sh -c 'git branch -m new-name'",
                        "bash -c 'git worktree add -b x ../w develop'"):
            with self.subTest(command=command):
                reason = self.asked(command)
                self.assertTrue(reason.startswith("Gemba rule (branches): "), reason)
                self.assertIn("could not read", reason)

    def test_a_wrapped_command_that_does_not_create_a_branch_prints_nothing(self):
        for command in ("bash -c 'git branch --show-current'", "bash -c 'git status'", "sudo git branch -a"):
            with self.subTest(command=command):
                self.passes(command)

    def test_a_commit_message_that_mentions_a_branch_prints_nothing(self):
        self.passes("git commit -m 'fix branch handling'")

    def test_a_wrapped_creation_in_a_project_without_setup_prints_nothing(self):
        other = make_repo(claude_md=None)
        self.addCleanup(subprocess.run, ["rm", "-rf", other])
        self.passes("bash -c 'git switch -c feature/login'", other)

    def test_a_creation_still_asks_when_the_hook_cannot_run_git(self):
        result = subprocess.run(["/usr/bin/env", "-i", "PATH=/nonexistent", sys.executable, SCRIPT],
                                input=json.dumps({"tool_name": "Bash", "cwd": self.repo,
                                                  "tool_input": {"command": "git switch -c feature/login"}}),
                                capture_output=True, text=True)
        self.assertEqual(decision(result)["permissionDecision"], "ask")

    def test_a_crash_asks_for_a_creation_and_prints_nothing_otherwise(self):
        sitecustomize_dir = os.path.join(self.repo, "boom")
        os.mkdir(sitecustomize_dir)
        with open(os.path.join(sitecustomize_dir, "git_commands.py"), "w", encoding="utf-8") as f:
            f.write("def git_commands(*a, **k):\n    raise RuntimeError('boom')\n"
                    "def mentions(*a, **k):\n    raise RuntimeError('boom')\n")
        hooks = os.path.join(sitecustomize_dir, "branch_rules.py")
        with open(SCRIPT, encoding="utf-8") as f, open(hooks, "w", encoding="utf-8") as g:
            g.write(f.read())

        def run(command):
            event = {"tool_name": "Bash", "cwd": self.repo, "tool_input": {"command": command}}
            return subprocess.run([sys.executable, hooks], input=json.dumps(event), capture_output=True, text=True)
        self.assertEqual(decision(run("git switch -c feature/login"))["permissionDecision"], "ask")
        self.assertIsNone(decision(run("git status")))


class RegisteredInThePlugin(unittest.TestCase):
    def test_the_script_is_registered_for_bash_before_the_tool_runs(self):
        with open(os.path.join(ROOT, "hooks", "hooks.json"), encoding="utf-8") as f:
            entries = json.load(f)["hooks"]["PreToolUse"]
        commands = [(entry["matcher"], hook["command"]) for entry in entries for hook in entry["hooks"]]
        self.assertIn(("Bash", 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/branch_rules.py"'), commands)


if __name__ == "__main__":
    unittest.main()
