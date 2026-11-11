import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_confirm_push_hook import decision, git, make_repo  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "hooks", "commit_rules.py")


def run_hook(repo, command, tool="Bash"):
    event = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {"command": command}, "cwd": repo}
    return subprocess.run([sys.executable, SCRIPT], input=json.dumps(event), cwd=repo,
                          capture_output=True, text=True)


class CommitRulesCase(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", self.repo])
        git(self.repo, "checkout", "-q", "-b", "story/ABC-1-export")

    def outcome(self, command, repo=None):
        result = run_hook(repo or self.repo, command)
        self.assertEqual(result.returncode, 0, result.stderr)
        out = decision(result)
        if out is not None:
            self.assertEqual(out["hookEventName"], "PreToolUse")
        return out

    def blocked(self, command):
        out = self.outcome(command)
        self.assertIsNotNone(out, "the hook printed nothing for: " + command)
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertTrue(out["permissionDecisionReason"].startswith("Gemba rule (commits): "))
        return out["permissionDecisionReason"]

    def asked(self, command):
        out = self.outcome(command)
        self.assertIsNotNone(out, "the hook printed nothing for: " + command)
        self.assertEqual(out["permissionDecision"], "ask")
        return out["permissionDecisionReason"]

    def passes(self, command, repo=None):
        self.assertIsNone(self.outcome(command, repo), "the hook should print nothing for: " + command)


class MessageFormat(CommitRulesCase):
    def test_a_message_without_type_and_scope_is_blocked_and_names_the_format(self):
        reason = self.blocked('git commit -m "add the export"')
        self.assertIn("<type>(<scope>): <description>", reason)

    def test_a_message_with_an_unknown_type_is_blocked_and_lists_the_types(self):
        reason = self.blocked('git commit -m "feature(export): add the export"')
        self.assertIn("type", reason)
        self.assertIn("feature", reason)
        self.assertIn("feat", reason)

    def test_a_message_with_an_uppercase_type_is_blocked(self):
        self.blocked('git commit -m "Feat(export): add the export"')

    def test_a_message_without_a_space_after_the_colon_is_blocked(self):
        self.blocked('git commit -m "feat(export):add the export"')


class MessageParts(CommitRulesCase):
    def test_a_message_with_two_messages_is_blocked_as_more_than_one_line(self):
        reason = self.blocked('git commit -m "feat(export): add the export" -m "More detail"')
        self.assertIn("one line", reason)

    def test_a_message_with_a_newline_is_blocked_as_more_than_one_line(self):
        reason = self.blocked('git commit -m "feat(export): add the export\n\nBody"')
        self.assertIn("one line", reason)

    def test_a_final_period_is_blocked_and_named(self):
        reason = self.blocked('git commit -m "feat(export): add the export."')
        self.assertIn("period", reason)

    def test_a_jira_key_is_blocked_and_named(self):
        reason = self.blocked('git commit -m "feat(export): add the export for ABC-12"')
        self.assertIn("Jira key", reason)

    def test_a_word_that_only_looks_like_a_key_passes(self):
        self.passes('git commit -m "fix(export): read the file as UTF-8 and hash it with SHA-256"')

    def test_a_jira_key_in_the_scope_is_blocked_and_named(self):
        reason = self.blocked('git commit -m "feat(ABC-12): add the export"')
        self.assertIn("Jira key", reason)

    def test_an_uppercase_scope_is_blocked_and_named(self):
        reason = self.blocked('git commit -m "feat(Export): add the export"')
        self.assertIn("lowercase", reason)

    def test_the_long_message_option_is_read_too(self):
        self.blocked('git commit --message="add the export"')
        self.blocked('git commit --message "feat(export): add the export."')

    def test_the_message_is_read_in_a_bundled_option_and_a_commit_in_another_folder(self):
        self.blocked('git commit -am "add the export"')
        self.blocked(f'git -C {self.repo} commit -m "add the export"')

    def test_a_chain_is_blocked_when_one_of_its_commits_breaks_a_rule(self):
        self.blocked('git add -A && git commit -m "add the export"')

    def test_the_reason_names_the_rule_and_how_to_fix_it(self):
        reason = self.blocked('git commit -m "feat(export): add the export."')
        self.assertIn("Gemba rule (commits): ", reason)
        self.assertIn("Remove the final period", reason)


class MessagesThatPass(CommitRulesCase):
    def test_messages_that_follow_the_rules_pass(self):
        for message in ("feat(export): add the export", "fix: handle an empty file", "chore(manifest): bump gemba-code to v0.1.0",
                        "feat(hooks)!: drop the old format", "refactor(hooks-core): split the parser", "docs(api): name GitHub"):
            with self.subTest(message=message):
                self.passes(f'git commit -m "{message}"')

    def test_a_single_quoted_message_passes(self):
        self.passes("git commit -m 'feat(export): add the export'")

    def test_initial_commit_passes(self):
        self.passes('git commit -m "Initial commit"')

    def test_a_merge_commit_message_passes(self):
        self.passes("git commit -m \"Merge branch 'story/ABC-1-export' into develop\"")

    def test_the_default_message_of_git_revert_passes(self):
        self.passes('git commit -m \'Revert "feat(export): add the export"\'')
        self.passes('git commit -m \'Revert "feat(export): add the export"\' -m "This reverts commit 1a2b3c4d."')

    def test_a_revert_with_any_other_second_paragraph_is_blocked(self):
        self.blocked('git commit -m \'Revert "feat(export): add the export"\' -m "Because it broke"')

    def test_a_fixup_or_a_squash_passes_without_a_message(self):
        self.passes("git commit --fixup HEAD")
        self.passes("git commit --fixup=abc1234")
        self.passes("git commit --squash HEAD~1")

    def test_a_fixup_message_passes(self):
        self.passes('git commit -m "fixup! feat(export): add the export"')

    def test_reusing_an_existing_message_passes(self):
        self.passes("git commit --amend --no-edit")
        self.passes("git commit -C HEAD")
        self.passes("git commit --reuse-message=HEAD")

    def test_other_git_commands_pass(self):
        self.passes("git status")
        self.passes('git log --grep "add the export"')


class MessagesThatCannotBeRead(CommitRulesCase):
    def assert_generic(self, command):
        reason = self.asked(command)
        self.assertIn("Gemba rule (commits): ", reason)
        self.assertIn("could not be read", reason)

    def test_a_message_from_a_file_asks(self):
        self.assert_generic("git commit -F message.txt")
        self.assert_generic("git commit --file=message.txt")
        self.assert_generic("git commit -t template.txt")

    def test_a_heredoc_or_a_substitution_asks(self):
        self.assert_generic('git commit -m "$(cat <<\'EOF\'\nfeat(export): add the export\nEOF\n)"')
        self.assert_generic('git commit -m "feat(export): `date`"')

    def test_a_wrapped_commit_asks(self):
        self.assert_generic("bash -c 'git commit -m \"add the export\"'")
        self.assert_generic('sudo git commit -m "add the export"')

    def test_a_commit_that_opens_an_editor_asks(self):
        self.assert_generic("git commit")
        self.assert_generic("git commit -a")


class ProtectedBranches(CommitRulesCase):
    def write_commit(self, name):
        with open(os.path.join(self.repo, name), "w", encoding="utf-8") as f:
            f.write(name)
        git(self.repo, "add", name)
        git(self.repo, "commit", "-q", "-m", "feat: add " + name)

    def test_a_commit_on_develop_is_blocked_and_names_the_branch(self):
        git(self.repo, "checkout", "-q", "develop")
        reason = self.blocked('git commit -m "feat(export): add the export"')
        self.assertIn("develop", reason)
        self.assertIn("branch", reason)

    def test_a_commit_on_main_is_blocked_and_names_the_branch(self):
        git(self.repo, "checkout", "-q", "-b", "main")
        reason = self.blocked('git commit -m "feat(export): add the export"')
        self.assertIn("main", reason)

    def test_a_fixup_and_an_unreadable_commit_on_develop_are_blocked_too(self):
        git(self.repo, "checkout", "-q", "develop")
        self.blocked("git commit --fixup HEAD")
        self.blocked("git commit -F message.txt")

    def test_the_branch_of_the_folder_the_commit_runs_in_is_the_one_that_counts(self):
        git(self.repo, "checkout", "-q", "develop")
        other = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", other])
        git(other, "checkout", "-q", "-b", "story/ABC-2-import")
        self.passes(f'git -C {other} commit -m "feat(export): add the export"', self.repo)
        self.blocked(f'git -C {self.repo} commit -m "feat(export): add the export"')

    def test_a_commit_that_concludes_a_merge_on_develop_passes(self):
        self.write_commit("export.txt")
        git(self.repo, "checkout", "-q", "develop")
        git(self.repo, "merge", "-q", "--no-ff", "--no-commit", "story/ABC-1-export")
        self.passes("git commit --no-edit")
        self.passes("git commit -m \"Merge branch 'story/ABC-1-export' into develop\"")

    def test_a_merge_does_not_excuse_a_message_that_breaks_the_rules(self):
        self.write_commit("export.txt")
        git(self.repo, "checkout", "-q", "develop")
        git(self.repo, "merge", "-q", "--no-ff", "--no-commit", "story/ABC-1-export")
        self.blocked('git commit -m "add the export."')

    def test_a_commit_on_a_detached_head_or_another_branch_passes(self):
        self.passes('git commit -m "feat(export): add the export"')
        git(self.repo, "checkout", "-q", "--detach")
        self.passes('git commit -m "feat(export): add the export"')

    def test_a_branch_that_only_contains_the_name_passes(self):
        git(self.repo, "checkout", "-q", "-b", "task/ABC-3-merge-develop-docs")
        self.passes('git commit -m "feat(export): add the export"')


class TrackedBranch(CommitRulesCase):
    def test_a_commit_after_a_checkout_of_develop_is_blocked(self):
        reason = self.blocked('git checkout develop && git commit -m "feat: x"')
        self.assertIn("develop", reason)
        self.blocked('git switch develop && git commit -m "feat: x"')

    def test_a_commit_on_a_new_work_branch_made_from_develop_passes(self):
        git(self.repo, "checkout", "-q", "develop")
        self.passes('git switch -c story/ABC-2-y && git commit -m "feat: y"')
        self.passes('git checkout -b story/ABC-2-y && git commit -m "feat: y"')

    def test_a_commit_after_leaving_a_protected_branch_passes_and_after_a_path_checkout_does_not(self):
        git(self.repo, "checkout", "-q", "develop")
        self.passes('git switch story/ABC-1-export && git commit -m "feat: x"')
        self.blocked('git checkout -- . && git commit -m "feat: x"')

    def test_a_commit_after_a_cd_to_a_folder_on_develop_is_blocked(self):
        other = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", other])
        self.blocked(f'cd {other} && git commit -m "feat: x"')

    def test_a_commit_when_the_folder_or_the_branch_cannot_be_told_asks(self):
        self.assertIn("could not", self.asked('cd && git commit -m "feat: x"'))
        self.asked('cd $DIR && git commit -m "feat: x"')
        self.asked('git switch - && git commit -m "feat: x"')

    def test_a_broken_message_after_an_unknown_folder_is_still_blocked(self):
        self.blocked('cd && git commit -m "add the export."')


class OtherCommitsOnProtectedBranches(CommitRulesCase):
    def test_revert_cherry_pick_and_am_are_blocked_on_develop_and_main(self):
        git(self.repo, "checkout", "-q", "develop")
        for command in ("git revert HEAD", "git cherry-pick abc1234", "git am patch.mbox", "git -C %s revert HEAD" % self.repo):
            with self.subTest(command=command):
                reason = self.blocked(command)
                self.assertIn("develop", reason)
        git(self.repo, "checkout", "-q", "-b", "main")
        self.blocked("git revert HEAD")

    def test_after_a_checkout_of_develop_they_are_blocked_too(self):
        self.blocked("git checkout develop && git cherry-pick abc1234")

    def test_finishing_or_leaving_the_operation_passes(self):
        git(self.repo, "checkout", "-q", "develop")
        for command in ("git revert --abort", "git revert --continue", "git cherry-pick --skip", "git cherry-pick --quit",
                        "git am --abort", "git am --continue", "git am --skip", "git revert -n HEAD"):
            with self.subTest(command=command):
                self.passes(command)

    def test_on_a_work_branch_they_pass(self):
        for command in ("git revert HEAD", "git revert --no-edit HEAD", "git cherry-pick abc1234", "git am patch.mbox"):
            with self.subTest(command=command):
                self.passes(command)

    def test_without_a_gemba_section_they_pass(self):
        repo = make_repo(claude_md=None)
        self.addCleanup(subprocess.run, ["rm", "-rf", repo])
        self.passes("git revert HEAD", repo)


class ProjectsWithoutGemba(CommitRulesCase):
    def setUp(self):
        self.repo = make_repo(claude_md=None)
        self.addCleanup(subprocess.run, ["rm", "-rf", self.repo])
        git(self.repo, "checkout", "-q", "-b", "story/ABC-1-export")

    def test_nothing_is_blocked_without_a_gemba_section(self):
        self.passes('git commit -m "add the export."')
        self.passes("git commit -F message.txt")
        self.passes("bash -c 'git commit -m x'")

    def test_a_commit_on_develop_passes_without_a_gemba_section(self):
        git(self.repo, "checkout", "-q", "develop")
        self.passes('git commit -m "feat(export): add the export"')

    def test_a_claude_md_without_the_section_blocks_nothing(self):
        other = make_repo(claude_md="## Notes\n\nNothing here.\n")
        self.addCleanup(subprocess.run, ["rm", "-rf", other])
        self.passes('git commit -m "add the export."', other)


class Robustness(CommitRulesCase):
    def test_other_tools_are_ignored(self):
        result = run_hook(self.repo, 'git commit -m "x"', tool="Edit")
        self.assertEqual(result.stdout.strip(), "")

    def test_bad_input_prints_nothing(self):
        result = subprocess.run([sys.executable, SCRIPT], input="not json", capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout.strip()), (0, ""))

    def test_the_script_is_registered_for_bash_before_the_tool_runs(self):
        with open(os.path.join(ROOT, "hooks", "hooks.json"), encoding="utf-8") as f:
            entries = json.load(f)["hooks"]["PreToolUse"]
        commands = [(entry["matcher"], hook["command"]) for entry in entries for hook in entry["hooks"]]
        self.assertIn(("Bash", 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/commit_rules.py"'), commands)

    def test_a_missing_parser_asks_for_a_commit_and_prints_nothing_otherwise(self):
        import shutil
        import tempfile
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        script = os.path.join(folder, "commit_rules.py")
        shutil.copy(SCRIPT, script)

        def run(command):
            event = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": self.repo}
            return subprocess.run([sys.executable, script], input=json.dumps(event), capture_output=True, text=True)

        self.assertEqual(json.loads(run('git commit -m "x"').stdout)["hookSpecificOutput"]["permissionDecision"], "ask")
        self.assertEqual(run("git status").stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
