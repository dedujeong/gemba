import io
import json
import os
import subprocess
import sys
import unittest
from unittest import mock

from test_confirm_push_hook import make_repo, git, decision, run_hook as run_confirm_push

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "hooks", "integration_rules.py")


def claude_md(integration):
    line = "" if integration is None else f"- Integration: {integration}\n"
    return f"## Gemba\n\n- Jira Project: ABC\n- Confluence Space: ABC\n{line}- Language: es-MX\n"


def run_hook(repo, command, tool="Bash"):
    event = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {"command": command}, "cwd": repo}
    return subprocess.run([sys.executable, SCRIPT], input=json.dumps(event), cwd=repo, capture_output=True, text=True)


class HookCase(unittest.TestCase):
    integration = "merge"

    def setUp(self):
        self.repo = make_repo(claude_md(self.integration))
        self.addCleanup(subprocess.run, ["rm", "-rf", self.repo])

    def out(self, command):
        result = run_hook(self.repo, command)
        self.assertEqual(result.returncode, 0, result.stderr)
        return decision(result)

    def denied(self, command):
        out = self.out(command)
        self.assertIsNotNone(out, "the hook printed nothing for: " + command)
        self.assertEqual(out["hookEventName"], "PreToolUse")
        self.assertEqual(out["permissionDecision"], "deny", command)
        return out["permissionDecisionReason"]

    def asked(self, command):
        out = self.out(command)
        self.assertIsNotNone(out, "the hook printed nothing for: " + command)
        self.assertEqual(out["permissionDecision"], "ask", command)
        return out["permissionDecisionReason"]

    def passes(self, command):
        self.assertIsNone(self.out(command), "the hook should print nothing for: " + command)


class MergeModePushes(HookCase):
    def test_a_push_of_a_work_branch_is_denied_and_the_reason_names_the_rule(self):
        reason = self.denied("git push -u origin story/ABC-1-export")
        self.assertIn("Gemba rule (integration: merge)", reason)
        self.assertIn("story/ABC-1-export", reason)
        self.assertIn("develop", reason)

    def test_a_bare_push_from_a_work_branch_is_denied(self):
        git(self.repo, "checkout", "-q", "-b", "task/ABC-2-x")
        self.denied("git push")
        self.denied("git push origin")
        self.denied("git push origin HEAD")

    def test_refspecs_are_read_by_their_destination(self):
        self.denied("git push origin task/ABC-2-x:task/ABC-2-x")
        self.denied("git push origin develop:task/ABC-2-x")
        self.denied("git push origin HEAD:refs/heads/task/ABC-2-x")
        self.denied("git push origin +task/ABC-2-x")
        self.passes("git push origin task/ABC-2-x:develop")

    def test_all_and_mirror_push_work_branches(self):
        self.denied("git push --all origin")
        self.denied("git push --mirror origin")

    def test_develop_and_main_pass(self):
        self.passes("git push origin develop")
        self.passes("git push origin main")
        self.passes("git push -u origin develop")
        self.passes("git push")  # the repository is on develop

    def test_tags_and_deletions_are_not_branch_pushes(self):
        git(self.repo, "tag", "v1")
        self.passes("git push --tags origin")
        self.passes("git push origin refs/tags/v1")
        self.passes("git push origin v1")
        self.passes("git push origin tag v1")
        self.passes("git push origin --delete story/ABC-1-export")
        self.passes("git push origin :story/ABC-1-export")

    def test_the_folder_of_dash_c_decides_the_current_branch(self):
        other = make_repo(claude_md("merge"))
        self.addCleanup(subprocess.run, ["rm", "-rf", other])
        git(other, "checkout", "-q", "-b", "task/ABC-3-y")
        self.denied(f"git -C {other} push")

    def test_other_commands_and_tools_pass(self):
        self.passes("git status")
        self.passes("git merge story/ABC-1-export")
        self.assertIsNone(decision(run_hook(self.repo, "git push origin task/x", tool="Read")))

    def test_a_project_without_the_gemba_section_passes(self):
        repo = make_repo(None)
        self.addCleanup(subprocess.run, ["rm", "-rf", repo])
        self.assertIsNone(decision(run_hook(repo, "git push origin task/x")))


class MissingOrInvalidMode(HookCase):
    integration = None

    def test_a_missing_integration_denies_any_branch_push_and_says_so(self):
        for command in ("git push origin develop", "git push -u origin task/ABC-1-x", "git push"):
            reason = self.denied(command)
            self.assertIn("Gemba rule", reason)
            self.assertIn("Integration", reason)
            self.assertIn("missing", reason)
            self.assertIn("setup", reason)

    def test_a_tag_push_is_not_a_branch_push(self):
        self.passes("git push --tags origin")


class InvalidMode(MissingOrInvalidMode):
    integration = "squash"

    def test_an_invalid_value_is_reported_as_invalid(self):
        reason = self.denied("git push origin develop")
        self.assertIn("squash", reason)
        self.assertIn("missing or invalid", reason)


class ModeSpelling(HookCase):
    integration = "  Merge "

    def test_the_mode_is_compared_without_case_or_spaces(self):
        self.denied("git push origin task/x")
        self.passes("git push origin develop")


class PullRequestMode(HookCase):
    integration = "pull request"

    def test_a_push_of_develop_or_main_is_denied_and_the_reason_names_the_rule(self):
        reason = self.denied("git push origin develop")
        self.assertIn("Gemba rule (integration: pull request)", reason)
        self.assertIn("develop", reason)
        self.denied("git push origin main")
        self.denied("git push")  # the repository is on develop
        self.denied("git push origin HEAD:main")
        self.denied("git push origin task/ABC-1-x:develop")

    def test_a_push_of_a_work_branch_passes(self):
        self.passes("git push -u origin story/ABC-1-export")
        git(self.repo, "checkout", "-q", "-b", "task/ABC-2-x")
        self.passes("git push")
        self.passes("git push origin HEAD")

    def test_the_commands_of_the_close_skill_pass(self):
        self.passes("git switch develop")
        self.passes("git pull origin develop")
        self.passes("git pull")
        self.passes("git push origin --delete story/ABC-1-export")

    def test_a_merge_while_on_develop_or_main_is_denied(self):
        reason = self.denied("git merge --no-ff story/ABC-1-export")
        self.assertIn("Gemba rule (integration: pull request)", reason)
        self.assertIn("develop", reason)
        git(self.repo, "checkout", "-q", "-b", "main")
        self.denied("git merge task/ABC-1-x")

    def test_a_merge_into_a_work_branch_passes(self):
        git(self.repo, "checkout", "-q", "-b", "task/ABC-2-x")
        self.passes("git merge develop")
        self.passes("git merge --no-ff develop")

    def test_aborting_or_continuing_a_merge_passes_on_develop(self):
        for flag in ("--abort", "--continue", "--quit"):
            self.passes("git merge " + flag)

    def test_the_folder_of_dash_c_decides_the_branch_of_the_merge(self):
        other = make_repo(claude_md("pull request"))
        self.addCleanup(subprocess.run, ["rm", "-rf", other])
        git(self.repo, "checkout", "-q", "-b", "task/ABC-3-y")  # the session is on a work branch
        self.denied(f"git -C {other} merge task/x")  # the other folder is on develop
        git(other, "checkout", "-q", "-b", "task/ABC-4-z")
        self.passes(f"git -C {other} merge develop")

    def test_gh_pr_merge_is_denied_even_with_options_before_it(self):
        reason = self.denied("gh pr merge 12 --merge")
        self.assertIn("Gemba rule (integration: pull request)", reason)
        self.assertIn("gh pr merge", reason)
        self.denied("gh -R acme/app pr merge 3")
        self.denied("gh --repo acme/app pr merge 3 --squash")
        self.denied("git status && gh pr merge")

    def test_other_gh_commands_pass(self):
        self.passes("gh pr create --base develop --title x --body y")
        self.passes("gh pr view 3")
        self.passes("gh pr list --state merged")

    def test_a_wrapped_merge_or_pr_merge_asks_with_a_generic_reason(self):
        for command in ("bash -c 'git merge story/ABC-1-x'", "sudo git merge x", "bash -c 'gh pr merge 3'",
                        "sh -c \"gh -R a/b pr merge 3\""):
            self.assertIn("could not read", self.asked(command))

    def test_a_wrapped_push_still_asks(self):
        self.assertIn("could not read", self.asked("bash -c 'git push origin develop'"))


class MergeModeKeepsMerging(HookCase):
    def test_local_merges_and_pr_merges_are_not_this_modes_business(self):
        self.passes("git merge --no-ff story/ABC-1-export")
        self.passes("gh pr merge 3")
        self.passes("bash -c 'git merge x'")


class AllowedPushKeepsItsConfirmation(HookCase):
    def test_an_allowed_push_prints_nothing_here_and_confirm_push_still_asks(self):
        self.passes("git push origin develop")
        result = run_confirm_push(self.repo, "git push origin develop")
        out = decision(result)
        self.assertEqual(out["permissionDecision"], "ask")


class UnreadableCommands(HookCase):
    def test_a_wrapped_push_asks_with_a_generic_reason(self):
        for command in ("bash -c 'git push origin task/x'", "sudo git push origin task/x",
                        "if true; then git push origin task/x; fi"):
            reason = self.asked(command)
            self.assertIn("could not read", reason)

    def test_a_wrapped_push_outside_a_gemba_project_passes(self):
        repo = make_repo(None)
        self.addCleanup(subprocess.run, ["rm", "-rf", repo])
        self.assertIsNone(decision(run_hook(repo, "bash -c 'git push origin task/x'")))

    def test_a_crash_asks_when_the_command_mentions_a_push(self):
        sys.path.insert(0, os.path.join(ROOT, "hooks"))
        self.addCleanup(sys.path.remove, os.path.join(ROOT, "hooks"))
        import integration_rules
        event = {"tool_name": "Bash", "tool_input": {"command": "git push origin develop"}, "cwd": self.repo}
        with mock.patch.object(integration_rules, "decide", side_effect=RuntimeError("boom")), \
                mock.patch("sys.stdin", io.StringIO(json.dumps(event))), \
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            integration_rules.main()
        self.assertEqual(json.loads(stdout.getvalue())["hookSpecificOutput"]["permissionDecision"], "ask")

    def test_a_crash_on_a_command_that_is_not_about_a_push_prints_nothing(self):
        sys.path.insert(0, os.path.join(ROOT, "hooks"))
        self.addCleanup(sys.path.remove, os.path.join(ROOT, "hooks"))
        import integration_rules
        event = {"tool_name": "Bash", "tool_input": {"command": "ls"}, "cwd": self.repo}
        with mock.patch.object(integration_rules, "decide", side_effect=RuntimeError("boom")), \
                mock.patch("sys.stdin", io.StringIO(json.dumps(event))), \
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            integration_rules.main()
        self.assertEqual(stdout.getvalue(), "")


def other_repo(case, integration="merge"):
    repo = make_repo(None if integration is None else claude_md(integration))
    case.addCleanup(subprocess.run, ["rm", "-rf", repo])
    return repo


class ReviewFindingsMergeMode(HookCase):
    def test_a_bare_push_follows_the_branch_the_command_switches_to(self):
        git(self.repo, "branch", "task/ABC-2-x")
        self.denied("git switch task/ABC-2-x && git push")
        self.denied("git checkout task/ABC-2-x && git push origin")
        git(self.repo, "checkout", "-q", "task/ABC-2-x")
        self.passes("git switch develop && git push")

    def test_a_push_to_an_unrelated_repository_without_gemba_prints_nothing(self):
        other = other_repo(self, None)
        git(other, "checkout", "-q", "-b", "task/x")
        self.passes(f"git -C {other} push origin task/x")
        self.passes(f"cd {other} && git push origin task/x")

    def test_the_mode_comes_from_the_repository_the_command_runs_in(self):
        other = other_repo(self, "pull request")
        self.denied(f"git -C {other} push origin develop")  # the session repository is in merge mode
        self.passes(f"git -C {other} push origin task/x")

    def test_repo_option_is_the_remote_and_every_positional_is_a_refspec(self):
        self.denied("git push --repo origin task/ABC-2-x")
        self.denied("git push --repo=origin task/ABC-2-x")
        self.passes("git push --repo origin develop")

    def test_at_is_an_alias_of_head(self):
        git(self.repo, "checkout", "-q", "-b", "task/ABC-2-x")
        self.denied("git push origin @")
        self.denied("git push origin @:task/ABC-3-y")
        self.passes("git push origin @:develop")

    def test_words_that_only_look_like_a_merge_or_a_push_do_not_ask(self):
        self.passes("git merge-base HEAD develop")
        self.passes("git commit -m 'merge notes' --allow-empty")
        self.passes("git commit -m 'push notes' --allow-empty")
        self.passes("git log --grep=push")

    def test_the_mode_is_read_once_per_repository(self):
        sys.path.insert(0, os.path.join(ROOT, "hooks"))
        self.addCleanup(sys.path.remove, os.path.join(ROOT, "hooks"))
        import integration_rules
        import git_commands
        event = {"tool_name": "Bash", "cwd": self.repo,
                 "tool_input": {"command": "git push origin develop && git push origin main && git push origin develop"}}
        with mock.patch.object(integration_rules, "git_commands", git_commands), \
                mock.patch.object(git_commands, "gemba_field", return_value="merge") as field, \
                mock.patch("sys.stdout", new_callable=io.StringIO):
            integration_rules.decide(event)
        self.assertEqual(field.call_count, 1)

    def test_gh_pr_merge_has_one_shared_pattern(self):
        with open(SCRIPT, encoding="utf-8") as f:
            self.assertEqual(f.read().count(r"\bgh\b"), 1)


class ReviewFindingsPullRequestMode(HookCase):
    integration = "pull request"

    def test_all_and_mirror_include_develop_and_main(self):
        reason = self.denied("git push --all origin")
        self.assertIn("pull request", reason)
        self.denied("git push --mirror origin")
        self.denied("git push origin --all")

    def test_a_local_merge_follows_the_branch_the_command_switches_to(self):
        git(self.repo, "branch", "task/ABC-2-x")
        self.denied("git switch develop && git merge task/ABC-2-x")
        git(self.repo, "checkout", "-q", "task/ABC-2-x")
        self.denied("git checkout develop && git merge task/ABC-3-y")
        self.passes("git merge develop")

    def test_a_bare_push_follows_the_branch_the_command_switches_to(self):
        git(self.repo, "branch", "task/ABC-2-x")
        git(self.repo, "checkout", "-q", "task/ABC-2-x")
        self.denied("git checkout develop && git push")
        self.denied("git switch develop && git push origin HEAD")
        self.passes("git push")

    def test_the_repo_option_and_at_name_develop_too(self):
        self.denied("git push --repo origin develop")
        self.denied("git push origin @")  # the repository is on develop

    def test_pulling_another_branch_into_develop_or_main_is_a_local_merge(self):
        reason = self.denied("git pull origin task/ABC-2-x")
        self.assertIn("Gemba rule (integration: pull request)", reason)
        self.denied("git pull --no-rebase origin story/ABC-1-export")
        self.denied("git pull origin main")  # the repository is on develop
        git(self.repo, "checkout", "-q", "-b", "main")
        self.denied("git pull origin develop")

    def test_pulling_the_same_branch_or_pulling_on_a_work_branch_passes(self):
        self.passes("git pull")
        self.passes("git pull origin develop")
        self.passes("git pull --ff-only origin develop")
        git(self.repo, "checkout", "-q", "-b", "task/ABC-2-x")
        self.passes("git pull origin develop")
        self.passes("git pull origin task/ABC-2-x")

    def test_a_wrapped_pull_asks_and_a_merge_base_does_not(self):
        self.assertIn("could not read", self.asked("bash -c 'git pull origin task/x'"))
        self.passes("git merge-base HEAD develop")
        self.passes("git commit -m 'merge notes' --allow-empty")

    def test_an_unknown_folder_asks(self):
        self.assertIn("could not read", self.asked("cd $SOMEWHERE && git merge task/x"))
        self.assertIn("could not read", self.asked("cd $SOMEWHERE && git push origin task/x"))


class RegisteredInThePlugin(unittest.TestCase):
    def test_the_script_is_registered_for_bash_before_the_tool_runs(self):
        with open(os.path.join(ROOT, "hooks", "hooks.json"), encoding="utf-8") as f:
            entries = [e for e in json.load(f)["hooks"]["PreToolUse"] if e.get("matcher") == "Bash"]
        commands = [h["command"] for e in entries for h in e["hooks"] if h["type"] == "command"]
        self.assertIn('python3 "${CLAUDE_PLUGIN_ROOT}/hooks/integration_rules.py"', commands)


if __name__ == "__main__":
    unittest.main()
