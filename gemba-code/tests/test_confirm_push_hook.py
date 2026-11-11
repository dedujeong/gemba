import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "hooks", "confirm_push.py")

GEMBA_CLAUDE_MD = "## Gemba\n\n- Jira Project: ABC\n- Confluence Space: ABC\n- Integration: merge\n- Language: es-MX\n"


def git(repo, *args):
    subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True, text=True)


def make_repo(claude_md=GEMBA_CLAUDE_MD):
    """A repository on develop with an origin remote, and a CLAUDE.md when one is given."""
    repo = tempfile.mkdtemp()
    git(repo, "init", "-q", "-b", "develop")
    git(repo, "config", "user.email", "maintainer@example.com")
    git(repo, "config", "user.name", "Maintainer")
    git(repo, "remote", "add", "origin", "https://example.com/acme/app.git")
    if claude_md is not None:
        with open(os.path.join(repo, "CLAUDE.md"), "w", encoding="utf-8") as f:
            f.write(claude_md)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--allow-empty", "-m", "chore: start")
    return repo


def run_hook(repo, command, tool="Bash", env=None):
    """Runs the hook the way Claude Code does: JSON on stdin, in the project."""
    event = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {"command": command}, "cwd": repo}
    return subprocess.run([sys.executable, SCRIPT], input=json.dumps(event), cwd=repo,
                          capture_output=True, text=True, env=env)


def decision(result):
    """The hook output as the object Claude Code reads, or None when the hook printed nothing."""
    if not result.stdout.strip():
        return None
    return json.loads(result.stdout)["hookSpecificOutput"]


class AsksOnEveryPush(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", self.repo])

    def asked(self, command):
        result = run_hook(self.repo, command)
        self.assertEqual(result.returncode, 0, result.stderr)
        out = decision(result)
        self.assertIsNotNone(out, "the hook printed nothing for: " + command)
        self.assertEqual(out["hookEventName"], "PreToolUse")
        self.assertEqual(out["permissionDecision"], "ask")
        return out["permissionDecisionReason"]

    def test_a_push_with_remote_and_branch_asks_and_names_both(self):
        reason = self.asked("git push origin develop")
        self.assertIn("origin", reason)
        self.assertIn("develop", reason)

    def test_a_push_that_sets_the_upstream_names_the_remote_and_the_branch(self):
        reason = self.asked("git push -u origin story/ABC-1-export")
        self.assertIn("origin", reason)
        self.assertIn("story/ABC-1-export", reason)

    def test_a_bare_push_names_the_current_branch_and_the_remote_it_is_configured_to_push_to(self):
        git(self.repo, "checkout", "-q", "-b", "story/ABC-2-import")
        git(self.repo, "remote", "add", "mirror", "https://example.com/acme/mirror.git")
        git(self.repo, "config", "branch.story/ABC-2-import.remote", "mirror")
        reason = self.asked("git push")
        self.assertIn("story/ABC-2-import", reason)
        self.assertIn("mirror", reason)

    def test_a_bare_push_with_no_configured_remote_names_origin(self):
        reason = self.asked("git push")
        self.assertIn("origin", reason)
        self.assertIn("develop", reason)

    def test_a_push_inside_a_compound_command_asks(self):
        reason = self.asked("git add . && git commit -m 'chore: x' && git push origin develop")
        self.assertIn("develop", reason)

    def test_a_push_with_git_global_options_asks(self):
        self.asked("git -C . push origin develop")
        self.asked("git -c push.default=current push")

    def test_a_push_that_deletes_a_remote_branch_asks(self):
        self.assertIn("story/ABC-3-old", self.asked("git push origin --delete story/ABC-3-old"))

    def test_a_push_on_a_later_line_asks(self):
        self.assertIn("develop", self.asked("git status\ngit push origin develop"))

    def test_a_hash_inside_a_word_does_not_hide_a_later_push(self):
        self.assertIn("develop", self.asked("echo issue#12 && git push origin develop"))

    def test_a_trailing_comment_is_not_taken_for_a_refspec(self):
        reason = self.asked("git push origin develop # sends the work")
        self.assertIn("develop", reason)
        self.assertNotIn("sends", reason)

    def test_a_push_of_everything_says_so_and_not_the_current_branch(self):
        self.assertIn("all branches", self.asked("git push --all origin"))
        self.assertIn("all tags", self.asked("git push --tags"))
        self.assertIn("mirror", self.asked("git push --mirror origin"))

    def test_the_decision_is_never_allow_and_the_hook_pushes_nothing(self):
        bare = tempfile.mkdtemp()
        self.addCleanup(subprocess.run, ["rm", "-rf", bare])
        git(bare, "init", "-q", "--bare")
        git(self.repo, "remote", "set-url", "origin", bare)
        for command in ("git push origin develop", "git push", "git push --force origin develop"):
            result = run_hook(self.repo, command)
            self.assertNotIn('"allow"', result.stdout)
            self.assertNotIn('"deny"', result.stdout)
        refs = subprocess.run(["git", "-C", bare, "for-each-ref"], capture_output=True, text=True, check=True)
        self.assertEqual(refs.stdout, "", "the hook must not push anything to the remote")


class FailsClosed(unittest.TestCase):
    def run_without_git(self, command):
        repo = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", repo])
        return run_hook(repo, command, env={"PATH": ""})

    def test_a_push_still_asks_when_the_hook_cannot_run_git(self):
        result = self.run_without_git("git push origin develop")
        self.assertEqual(result.returncode, 0, result.stderr)
        out = decision(result)
        self.assertIsNotNone(out, "a hook that fails must not let the push through unasked")
        self.assertEqual(out["permissionDecision"], "ask")
        self.assertIn("git push", out["permissionDecisionReason"])

    def test_a_command_that_is_not_a_push_still_prints_nothing_when_the_hook_cannot_run_git(self):
        result = self.run_without_git("git status")
        self.assertEqual((result.returncode, result.stdout), (0, ""))


class AsksOnWhatItCannotParse(unittest.TestCase):
    """A push the parser cannot read (a wrapper, a shell keyword, a quoted script) still asks, with a generic reason."""

    WRAPPED = (
        "bash -c 'git push origin develop'",
        "sh -c \"git push\"",
        "sudo git push origin develop",
        "env GIT_TRACE=1 git push origin develop",
        "timeout 30 git push origin develop",
        "command git push origin develop",
        "time git push origin develop",
        "if true; then git push origin develop; fi",
        "{ git push origin develop; }",
        "! git push origin develop",
        "echo `git push origin develop`",
        "xargs -I{} git push origin {} <<< develop",
    )

    def setUp(self):
        self.repo = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", self.repo])

    def test_a_wrapped_push_asks_with_a_generic_reason(self):
        for command in self.WRAPPED:
            result = run_hook(self.repo, command)
            self.assertEqual(result.returncode, 0, command)
            out = decision(result)
            self.assertIsNotNone(out, "the hook printed nothing for: " + command)
            self.assertEqual(out["permissionDecision"], "ask", command)
            self.assertIn("git push", out["permissionDecisionReason"], command)

    def test_a_command_that_only_mentions_git_push_asks_too(self):
        out = decision(run_hook(self.repo, "echo git push"))
        self.assertEqual(out["permissionDecision"], "ask")

    def test_a_push_the_parser_reads_keeps_its_precise_reason(self):
        reason = decision(run_hook(self.repo, "git push origin develop"))["permissionDecisionReason"]
        self.assertIn("develop", reason)
        self.assertNotIn("could not read", reason)

    def test_a_wrapped_push_in_a_project_without_the_gemba_section_prints_nothing(self):
        repo = make_repo(None)
        self.addCleanup(subprocess.run, ["rm", "-rf", repo])
        result = run_hook(repo, "bash -c 'git push origin develop'")
        self.assertEqual((result.returncode, result.stdout), (0, ""))


class StaysOutOfTheWay(unittest.TestCase):
    def test_a_command_that_is_not_a_push_prints_nothing(self):
        repo = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", repo])
        for command in ("git status", "git pull origin develop", "git log --oneline -3", "ls"):
            result = run_hook(repo, command)
            self.assertEqual((result.returncode, result.stdout), (0, ""), command)

    def test_a_tool_that_is_not_bash_prints_nothing(self):
        repo = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", repo])
        result = run_hook(repo, "git push origin develop", tool="Read")
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_a_project_without_the_gemba_section_prints_nothing(self):
        for claude_md in (None, "## Notes\n\nNothing about the method.\n"):
            repo = make_repo(claude_md)
            self.addCleanup(subprocess.run, ["rm", "-rf", repo])
            result = run_hook(repo, "git push origin develop")
            self.assertEqual((result.returncode, result.stdout), (0, ""), repr(claude_md))

    def test_the_project_is_found_from_a_subfolder(self):
        repo = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", repo])
        sub = os.path.join(repo, "docs")
        os.mkdir(sub)
        out = decision(run_hook(sub, "git push origin develop"))
        self.assertEqual(out["permissionDecision"], "ask")


class DeclinedPushRule(unittest.TestCase):
    def merges(self):
        with open(os.path.join(ROOT, "references", "context.md"), encoding="utf-8") as f:
            return f.read().split("## Merges")[1].split("## Commits")[0]

    def test_the_method_says_every_git_push_asks_the_maintainer_with_the_branch_and_the_remote(self):
        text = self.merges()
        self.assertIn("every `git push` asks the maintainer", text)
        self.assertIn("the branch and the remote", text)

    def test_a_declined_push_is_not_retried_by_another_route_and_what_was_left_is_said(self):
        text = self.merges()
        self.assertIn("If the maintainer declines, nothing is pushed", text)
        self.assertIn("do not retry it with another command, another remote or another tool", text)
        self.assertIn("say what was left unpushed", text)


class RegisteredInThePlugin(unittest.TestCase):
    def pre_tool_use(self):
        with open(os.path.join(ROOT, "hooks", "hooks.json"), encoding="utf-8") as f:
            return json.load(f)["hooks"]["PreToolUse"]

    def test_the_script_is_registered_for_bash_before_the_tool_runs(self):
        entries = [e for e in self.pre_tool_use() if e.get("matcher") == "Bash"]
        commands = [h["command"] for e in entries for h in e["hooks"] if h["type"] == "command"]
        self.assertEqual(commands.count('python3 "${CLAUDE_PLUGIN_ROOT}/hooks/confirm_push.py"'), 1)

    def test_the_session_start_hook_is_still_there(self):
        with open(os.path.join(ROOT, "hooks", "hooks.json"), encoding="utf-8") as f:
            self.assertIn("SessionStart", json.load(f)["hooks"])


if __name__ == "__main__":
    unittest.main()
