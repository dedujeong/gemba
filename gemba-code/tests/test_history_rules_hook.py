import json
import os
import subprocess
import sys
import tempfile
import unittest

from test_confirm_push_hook import GEMBA_CLAUDE_MD, decision, git, make_repo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "hooks", "history_rules.py")


def run_hook(repo, command, tool="Bash", env=None):
    """Runs the hook the way Claude Code does: JSON on stdin, in the project."""
    event = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {"command": command}, "cwd": repo}
    return subprocess.run([sys.executable, SCRIPT], input=json.dumps(event), cwd=repo,
                          capture_output=True, text=True, env=env)


class HookCase(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", self.repo])

    def outcome(self, command, repo=None):
        result = run_hook(repo or self.repo, command)
        self.assertEqual(result.returncode, 0, result.stderr)
        return decision(result)

    def denied(self, command, rule, repo=None):
        out = self.outcome(command, repo)
        self.assertIsNotNone(out, "the hook printed nothing for: " + command)
        self.assertEqual(out["hookEventName"], "PreToolUse")
        self.assertEqual(out["permissionDecision"], "deny", command)
        self.assertIn(f"Gemba rule ({rule})", out["permissionDecisionReason"], command)
        return out["permissionDecisionReason"]

    def asked(self, command, repo=None):
        out = self.outcome(command, repo)
        self.assertIsNotNone(out, "the hook printed nothing for: " + command)
        self.assertEqual(out["permissionDecision"], "ask", command)
        return out["permissionDecisionReason"]

    def passes(self, *commands, repo=None):
        for command in commands:
            result = run_hook(repo or self.repo, command)
            self.assertEqual((result.returncode, result.stdout), (0, ""), command)


class Merges(HookCase):
    def on(self, branch):
        git(self.repo, "checkout", "-q", "-B", branch)

    def test_a_merge_into_develop_without_no_ff_is_denied_and_names_the_rule(self):
        reason = self.denied("git merge story/ABC-1-export", "merges")
        self.assertIn("--no-ff", reason)

    def test_a_merge_into_main_without_no_ff_is_denied(self):
        self.on("main")
        self.denied("git merge develop", "merges")

    def test_a_fast_forward_only_merge_of_a_branch_is_denied(self):
        self.denied("git merge --ff-only story/ABC-1-export", "merges")

    def test_a_squash_merge_is_denied_even_with_no_ff(self):
        self.denied("git merge --squash story/ABC-1-export", "merges")
        self.denied("git merge --no-ff --squash story/ABC-1-export", "merges")

    def test_a_merge_with_its_own_message_is_denied(self):
        for command in ("git merge --no-ff -m 'my merge' story/ABC-1-export",
                        "git merge --no-ff --message='my merge' story/ABC-1-export",
                        "git merge --no-ff -F msg.txt story/ABC-1-export",
                        "git merge --no-ff --file msg.txt story/ABC-1-export"):
            self.denied(command, "merges")

    def test_a_merge_with_no_ff_and_the_default_message_passes(self):
        self.passes("git merge --no-ff story/ABC-1-export", "git merge --no-ff --no-edit story/ABC-1-export")

    def test_the_merge_is_read_in_a_compound_command_and_with_git_global_options(self):
        self.denied("git status && git merge story/ABC-1-export", "merges")
        self.denied("git -C . merge story/ABC-1-export", "merges")

    def test_a_merge_into_another_branch_passes(self):
        self.on("story/ABC-2-import")
        self.passes("git merge develop", "git merge --squash develop", "git merge -m x develop")

    def test_the_target_is_the_branch_the_command_has_switched_to(self):
        self.on("story/ABC-2-import")
        self.denied("git switch develop && git merge story/ABC-1-export", "merges")
        self.denied("git checkout develop && git merge story/ABC-1-export", "merges")
        self.passes("git switch develop && git merge --no-ff --no-edit story/ABC-1-export")

    def test_switching_away_from_develop_makes_the_merge_target_another_branch(self):
        self.passes("git switch -c story/ABC-2-import && git merge develop")

    def test_a_merge_after_a_switch_the_hook_cannot_follow_asks(self):
        self.on("story/ABC-2-import")
        self.assertIn("could not be told", self.asked("git switch - && git merge story/ABC-1-export"))

    def test_the_last_of_ff_and_no_ff_wins(self):
        self.denied("git merge --no-ff --ff story/ABC-1-export", "merges")
        self.denied("git merge --no-ff --ff-only story/ABC-1-export", "merges")
        self.passes("git merge --ff --no-ff story/ABC-1-export", "git merge --ff-only --no-ff story/ABC-1-export")

    def test_a_pull_of_another_branch_into_develop_or_main_is_a_merge_and_follows_its_rules(self):
        reason = self.denied("git pull origin story/ABC-1-export", "merges")
        self.assertIn("--no-ff", reason)
        self.denied("git pull origin refs/heads/story/ABC-1-export", "merges")
        self.denied("git pull --ff-only origin story/ABC-1-export", "merges")
        self.denied("git pull --squash", "merges")
        self.denied("git pull --squash origin develop", "merges")
        self.passes("git pull --no-ff --no-edit origin story/ABC-1-export")
        self.on("main")
        self.denied("git pull origin develop", "merges")
        self.passes("git pull origin main", "git pull")

    def test_a_pull_of_the_same_branch_or_into_another_branch_passes(self):
        self.passes("git pull", "git pull origin develop", "git pull --ff-only origin develop", "git pull upstream develop")
        self.on("story/ABC-2-import")
        self.passes("git pull origin develop", "git pull --squash origin develop")

    def test_a_pull_after_a_switch_the_hook_cannot_follow_asks(self):
        self.assertIn("could not be told", self.asked("git switch - && git pull"))

    def test_a_merge_that_is_aborted_continued_or_quit_passes(self):
        self.passes("git merge --abort", "git merge --continue", "git merge --quit")

    def test_bringing_develop_up_to_date_with_its_remote_passes(self):
        self.passes("git merge origin/develop", "git merge --ff-only origin/develop", "git merge --ff-only @{u}",
                    "git merge --ff-only", "git pull", "git pull origin develop", "git pull --ff-only")

    def test_bringing_main_up_to_date_passes_but_merging_the_other_remote_branch_does_not(self):
        self.on("main")
        self.passes("git merge --ff-only origin/main")
        self.denied("git merge origin/develop", "merges")

    def test_a_squash_is_denied_even_against_the_remote_branch(self):
        self.denied("git merge --squash origin/develop", "merges")

    def test_the_folder_of_dash_c_decides_the_branch(self):
        other = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", other])
        git(other, "checkout", "-q", "-b", "story/ABC-3-x")
        self.passes(f"git -C {other} merge develop")
        git(other, "checkout", "-q", "develop")
        self.denied(f"git -C {other} merge story/ABC-1-export", "merges")

    def test_a_project_without_the_gemba_section_prints_nothing(self):
        repo = make_repo(None)
        self.addCleanup(subprocess.run, ["rm", "-rf", repo])
        self.passes("git merge story/ABC-1-export", "bash -c 'git merge x'", repo=repo)

    def test_a_tool_that_is_not_bash_prints_nothing(self):
        result = run_hook(self.repo, "git merge story/ABC-1-export", tool="Read")
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_a_merge_the_parser_cannot_read_asks_with_a_generic_reason(self):
        for command in ("bash -c 'git merge story/ABC-1-export'", "sudo git merge story/ABC-1-export",
                        "if true; then git merge story/ABC-1-export; fi"):
            reason = self.asked(command)
            self.assertIn("could not read", reason, command)

    def test_a_wrapped_operation_is_not_hidden_by_a_readable_git_command_in_the_line(self):
        self.assertIn("could not read", self.asked("git status && bash -c 'git push --force origin develop'"))
        self.assertIn("could not read", self.asked("git tag v0.1.0 && bash -c 'git push --force origin develop'"))
        self.assertIn("could not read", self.asked("git fetch && sudo git merge story/ABC-1-export"))

    def test_a_readable_git_command_that_only_mentions_an_operation_prints_nothing(self):
        self.passes('git commit -m "fix the rebase check"', "git log --grep merge", 'git commit -m "fix the merge"',
                    "git log --oneline --grep 'force push'")

    def test_a_merge_still_asks_when_the_hook_cannot_run_git(self):
        result = run_hook(self.repo, "git merge story/ABC-1-export", env={"PATH": ""})
        out = decision(result)
        self.assertIsNotNone(out)
        self.assertEqual(out["permissionDecision"], "ask")

    def test_a_command_that_is_not_a_merge_prints_nothing_when_the_hook_cannot_run_git(self):
        result = run_hook(self.repo, "git status", env={"PATH": ""})
        self.assertEqual((result.returncode, result.stdout), (0, ""))


class Rebases(HookCase):
    def setUp(self):
        super().setUp()
        bare = tempfile.mkdtemp()
        self.addCleanup(subprocess.run, ["rm", "-rf", bare])
        git(bare, "init", "-q", "--bare")
        git(self.repo, "remote", "set-url", "origin", bare)
        git(self.repo, "push", "-q", "origin", "develop")
        git(self.repo, "checkout", "-q", "-b", "story/ABC-1-export")
        for name in ("one", "two"):
            git(self.repo, "commit", "-q", "--allow-empty", "-m", name)

    def test_a_rebase_is_denied_and_names_the_rule(self):
        reason = self.denied("git rebase develop", "rebase")
        self.assertIn("--autosquash", reason)

    def test_an_interactive_rebase_without_autosquash_is_denied(self):
        self.denied("git rebase -i develop", "rebase")
        self.denied("git rebase --no-autosquash develop", "rebase")

    def test_a_rebase_with_a_branch_name_or_onto_is_denied(self):
        self.denied("git rebase --onto main develop story/ABC-1-export", "rebase")

    def test_an_autosquash_rebase_over_commits_the_remote_does_not_have_passes(self):
        self.passes("git rebase -i --autosquash develop", "git rebase --autosquash develop",
                    "git -C . rebase --autosquash develop")

    def test_an_autosquash_rebase_over_commits_the_remote_has_is_denied(self):
        git(self.repo, "push", "-q", "origin", "story/ABC-1-export")
        self.denied("git rebase -i --autosquash develop", "rebase")

    def test_an_autosquash_rebase_over_some_commits_the_remote_has_is_denied(self):
        git(self.repo, "push", "-q", "origin", "HEAD~1:refs/heads/story/ABC-1-export")
        self.denied("git rebase -i --autosquash develop", "rebase")

    def test_an_autosquash_rebase_whose_range_cannot_be_read_is_denied(self):
        self.denied("git rebase -i --autosquash no-such-branch", "rebase")
        self.denied("git rebase -i --autosquash", "rebase")

    def test_an_autosquash_rebase_with_a_branch_name_reads_that_branch(self):
        git(self.repo, "push", "-q", "origin", "story/ABC-1-export")
        git(self.repo, "checkout", "-q", "-b", "story/ABC-2-other", "develop")
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "three")
        self.denied("git rebase -i --autosquash develop story/ABC-1-export", "rebase")
        self.passes("git rebase -i --autosquash develop story/ABC-2-other")

    def test_a_rebase_never_hands_a_revision_that_starts_with_a_dash_to_git(self):
        victim = os.path.join(self.repo, "victim.txt")
        with open(victim, "w", encoding="utf-8") as f:
            f.write("keep me")
        self.denied("git rebase --autosquash --root -- --output=victim.txt", "rebase")
        self.denied("git rebase --autosquash -- --output=victim.txt", "rebase")
        self.denied("git rebase --autosquash develop -- --output=victim.txt", "rebase")
        with open(victim, encoding="utf-8") as f:
            self.assertEqual(f.read(), "keep me")

    def test_a_root_autosquash_rebase_passes_when_no_commit_of_head_is_on_a_remote(self):
        local = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", local])
        git(local, "commit", "-q", "--allow-empty", "-m", "fixup! x")
        self.passes("git rebase -i --autosquash --root", "git rebase --root --autosquash", repo=local)

    def test_a_root_rebase_is_denied_without_autosquash_or_over_pushed_commits(self):
        local = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", local])
        self.denied("git rebase -i --root", "rebase", repo=local)
        self.denied("git rebase -i --autosquash --root", "rebase")  # develop is on the remote here
        git(self.repo, "checkout", "-q", "-b", "story/ABC-9-x", "develop")
        self.denied("git rebase -i --autosquash --root", "rebase")

    def test_onto_and_keep_base_still_read_the_range_from_the_upstream(self):
        self.passes("git rebase --keep-base --autosquash develop")
        git(self.repo, "push", "-q", "origin", "story/ABC-1-export")
        self.denied("git rebase --keep-base --autosquash develop", "rebase")
        self.denied("git rebase --onto main --autosquash develop", "rebase")

    def test_ending_a_rebase_passes(self):
        self.passes("git rebase --abort", "git rebase --continue", "git rebase --skip", "git rebase --quit")

    def test_a_pull_that_rebases_is_denied(self):
        for command in ("git pull --rebase", "git pull -r", "git pull --rebase=true origin develop",
                        "git pull --rebase=interactive", "git pull origin develop --rebase", "git pull -rq"):
            self.denied(command, "rebase")

    def test_a_pull_that_rebases_through_the_global_config_option_is_denied(self):
        for value in ("true", "merges", "interactive"):
            self.denied(f"git -c pull.rebase={value} pull", "rebase")
        self.denied("git -c pull.rebase=true -C . pull origin develop", "rebase")
        self.denied("git -c branch.story/ABC-1-export.rebase=true pull", "rebase")

    def test_a_pull_that_rebases_through_the_repository_config_is_denied(self):
        for value in ("true", "merges", "interactive"):
            git(self.repo, "config", "pull.rebase", value)
            self.denied("git pull", "rebase")
        git(self.repo, "config", "--unset", "pull.rebase")
        git(self.repo, "config", "branch.story/ABC-1-export.rebase", "true")
        self.denied("git pull origin develop", "rebase")

    def test_the_command_line_and_the_most_specific_config_win_over_a_rebasing_config(self):
        git(self.repo, "config", "pull.rebase", "true")
        self.passes("git pull --no-rebase", "git pull --rebase=false", "git -c pull.rebase=false pull",
                    "git pull --rebase --no-rebase")
        self.denied("git pull --no-rebase --rebase", "rebase")
        git(self.repo, "config", "branch.story/ABC-1-export.rebase", "false")
        self.passes("git pull")
        self.passes("git -c pull.rebase=true -c pull.rebase=false pull")

    def test_a_bare_config_key_means_true(self):
        self.denied("git -c pull.rebase pull", "rebase")
        self.denied("git -c branch.story/ABC-1-export.rebase pull", "rebase")
        self.passes("git -c pull.rebase pull --no-rebase")

    def test_the_rebase_option_value_uses_the_boolean_spellings_of_git(self):
        for value in ("false", "no", "off", "0", "FALSE"):
            self.passes(f"git pull --rebase={value}")
        for value in ("true", "yes", "on", "1", "merges", "interactive", "ON"):
            self.denied(f"git pull --rebase={value}", "rebase")

    def test_a_pull_with_a_config_that_does_not_rebase_passes(self):
        git(self.repo, "config", "pull.rebase", "false")
        self.passes("git pull", "git -c pull.rebase=false pull")

    def test_a_pull_that_does_not_rebase_passes(self):
        self.passes("git pull", "git pull --no-rebase", "git pull --rebase=false", "git pull origin develop")

    def test_a_rebase_the_parser_cannot_read_asks_with_a_generic_reason(self):
        for command in ("bash -c 'git rebase develop'", "sudo git pull --rebase", "if true; then git rebase -i develop; fi"):
            self.assertIn("could not read", self.asked(command), command)

    def test_a_pull_the_parser_cannot_read_that_does_not_rebase_prints_nothing(self):
        self.passes("bash -c 'git pull origin develop'")

    def test_a_project_without_the_gemba_section_prints_nothing(self):
        repo = make_repo(None)
        self.addCleanup(subprocess.run, ["rm", "-rf", repo])
        self.passes("git rebase develop", "git pull --rebase", repo=repo)


class ForcePushes(HookCase):
    def test_a_force_push_is_denied_and_names_the_rule(self):
        for command in ("git push --force origin develop", "git push -f origin develop", "git push origin develop -f",
                        "git push --force-with-lease origin develop", "git push --force-with-lease=develop origin develop",
                        "git push --force-if-includes origin develop", "git push -fu origin develop",
                        "git push origin +develop", "git push origin +develop:develop", "git push origin HEAD --force",
                        "git add . && git push -f", "git -C . push --force"):
            reason = self.denied(command, "history")
            self.assertIn("force", reason, command)

    def test_a_mirror_push_counts_as_forced(self):
        for command in ("git push --mirror", "git push --mirror origin", "git push origin --mirror"):
            self.assertIn("force", self.denied(command, "history"), command)

    def test_deleting_develop_or_main_on_the_remote_is_denied(self):
        for command in ("git push origin --delete develop", "git push origin :develop", "git push -d origin main",
                        "git push origin --delete refs/heads/main", "git push origin :refs/heads/develop",
                        "git push --delete origin story/ABC-1-export develop", "git push origin :story/ABC-1-export :main"):
            self.assertIn("lose", self.denied(command, "history"), command)

    def test_deleting_a_version_tag_on_the_remote_is_denied(self):
        for command in ("git push origin --delete v0.3.1", "git push origin :refs/tags/gemba-code--v0.1.0", "git push origin :v0.3.1",
                        "git push -d origin refs/tags/v1.2.3", "git push origin --delete gemba-product--v0.1.0"):
            self.assertIn("version", self.denied(command, "tags"), command)

    def test_deleting_other_remote_tags_passes(self):
        self.passes("git push origin --delete wip", "git push origin :refs/tags/wip", "git push origin :v1.2")

    def test_deleting_other_remote_branches_passes(self):
        self.passes("git push origin --delete story/ABC-1-export", "git push origin :story/ABC-1-export",
                    "git push -d origin task/ABC-2-x", "git push origin --delete feature/develop")

    def test_a_push_that_does_not_force_prints_nothing(self):
        self.passes("git push origin develop", "git push", "git push -u origin story/ABC-1-export",
                    "git push origin develop:develop", "git push origin --delete story/ABC-1-export",
                    "git push --tags", "git push origin 'v1+2'")

    def test_a_force_push_the_parser_cannot_read_asks_with_a_generic_reason(self):
        for command in ("bash -c 'git push --force origin develop'", "sudo git push -f", "sh -c 'git push origin +develop'"):
            self.assertIn("could not read", self.asked(command), command)

    def test_a_push_the_parser_cannot_read_that_does_not_force_prints_nothing(self):
        self.passes("bash -c 'git push origin develop'")

    def test_a_force_push_in_a_project_without_the_gemba_section_prints_nothing(self):
        repo = make_repo(None)
        self.addCleanup(subprocess.run, ["rm", "-rf", repo])
        self.passes("git push --force origin develop", repo=repo)


class BranchDeletion(HookCase):
    def test_a_forced_delete_of_a_branch_that_is_not_a_spikes_is_denied_and_names_the_rule(self):
        for command in ("git branch -D story/ABC-1-export", "git branch -D develop", "git branch --delete --force story/ABC-1-export",
                        "git branch -d -f story/ABC-1-export", "git branch -df story/ABC-1-export", "git branch -fd story/ABC-1-export",
                        "git branch --force --delete story/ABC-1-export", "git -C . branch -D story/ABC-1-export",
                        "git checkout develop && git branch -D task/ABC-2-x"):
            reason = self.denied(command, "history")
            self.assertIn("spike/", reason, command)

    def test_a_forced_delete_of_several_branches_is_denied_when_any_is_not_a_spikes(self):
        self.denied("git branch -D spike/ABC-3-research story/ABC-1-export", "history")

    def test_a_forced_delete_of_a_spikes_branch_passes(self):
        self.passes("git branch -D spike/ABC-3-research", "git branch -D spike/ABC-3-a spike/ABC-4-b",
                    "git branch --delete --force spike/ABC-3-research")

    def test_a_plain_delete_or_another_branch_command_prints_nothing(self):
        self.passes("git branch -d story/ABC-1-export", "git branch --delete story/ABC-1-export", "git branch",
                    "git branch -a", "git branch story/ABC-5-new", "git branch -f story/ABC-1-export develop",
                    "git branch -m old new", "git branch --list 'spike/*'")

    def test_forcing_a_branch_onto_an_existing_one_is_denied_because_it_discards_commits(self):
        git(self.repo, "branch", "story/ABC-6-x")
        for command in ("git branch -f story/ABC-6-x develop", "git branch --force story/ABC-6-x", "git branch -f develop HEAD",
                        "git branch -M story/ABC-6-x", "git branch -M develop story/ABC-6-x", "git branch -C develop story/ABC-6-x",
                        "git branch -m -f develop story/ABC-6-x", "git branch --move --force develop story/ABC-6-x",
                        "git branch -mf develop story/ABC-6-x", "git branch --copy --force develop story/ABC-6-x",
                        "git branch -cf story/ABC-6-x"):
            self.assertIn("discard", self.denied(command, "history"), command)

    def test_forcing_a_branch_that_does_not_exist_or_renaming_without_force_passes(self):
        git(self.repo, "branch", "story/ABC-6-x")
        self.passes("git branch -f story/ABC-7-new develop", "git branch -M develop story/ABC-7-new",
                    "git branch -C develop story/ABC-7-new", "git branch -M story/ABC-7-new", "git branch -m develop story/ABC-8-y",
                    "git branch -m story/ABC-6-x story/ABC-9-z", "git branch -c develop story/ABC-8-y", "git branch -M develop")

    def test_a_forced_delete_the_parser_cannot_read_asks_with_a_generic_reason(self):
        for command in ("bash -c 'git branch -D story/ABC-1-export'", "sudo git branch -D story/ABC-1-export"):
            self.assertIn("could not read", self.asked(command), command)

    def test_a_delete_the_parser_cannot_read_that_is_not_forced_prints_nothing(self):
        self.passes("bash -c 'git branch -d story/ABC-1-export'")

    def test_a_forced_delete_in_a_project_without_the_gemba_section_prints_nothing(self):
        repo = make_repo(None)
        self.addCleanup(subprocess.run, ["rm", "-rf", repo])
        self.passes("git branch -D story/ABC-1-export", repo=repo)


class Tags(HookCase):
    def test_a_tag_that_is_not_a_version_is_denied_and_names_the_rule(self):
        for command in ("git tag release", "git tag v1.0", "git tag 1.2.3", "git tag v1.2.3-rc1", "git tag V1.2.3",
                        "git tag -a v1.2 -m 'x'", "git tag -m 'x' -a latest develop", "git tag -f v1", "git tag -s backup",
                        "git tag gemba-code-v0.1.0", "git tag Gemba--v0.1.0", "git tag gemba--v0.1", "git tag gemba-product--v1.2.3.4",
                        "git tag v1.2.3-rc1 develop", "git status && git tag wip", "git -C . tag wip"):
            reason = self.denied(command, "tags")
            self.assertIn("vX.Y.Z", reason, command)

    def test_a_version_tag_passes(self):
        self.passes("git tag v0.1.0", "git tag v10.20.30 main", "git tag -a v1.2.3 -m 'Release'", "git tag -m x -a v1.2.3",
                    "git tag gemba-code--v0.1.0", "git tag gemba-product--v1.2.3 main", "git tag -a gemba-design--v0.0.1 -m 'x'",
                    "git tag -f v1.2.3")

    def test_moving_an_existing_tag_is_denied(self):
        git(self.repo, "tag", "v1.2.3")
        git(self.repo, "tag", "gemba-code--v0.1.0")
        for command in ("git tag -f v1.2.3", "git tag --force v1.2.3 develop", "git tag -fa v1.2.3 -m x",
                        "git tag -a -f gemba-code--v0.1.0 -m x", "git tag -f -s v1.2.3"):
            self.assertIn("moves", self.denied(command, "tags"), command)

    def test_forcing_a_version_tag_that_does_not_exist_yet_passes(self):
        git(self.repo, "tag", "v1.2.3")
        self.passes("git tag -f v1.2.4", "git tag --force gemba-code--v0.2.0 develop")

    def test_deleting_a_version_tag_is_denied(self):
        for command in ("git tag -d v1.2.3", "git tag --delete gemba-product--v0.1.0", "git tag -d wip v1.2.3",
                        "git tag -d v1.2.3 && git push origin :refs/tags/v1.2.3"):
            self.assertIn("version", self.denied(command, "tags"), command)

    def test_deleting_a_tag_that_is_not_a_version_passes(self):
        self.passes("git tag -d wip", "git tag --delete wip other", "git tag -d v1.2")

    def test_listing_deleting_and_verifying_tags_print_nothing(self):
        self.passes("git tag", "git tag -l", "git tag --list 'v*'", "git tag -l 'wip*'", "git tag -n", "git tag -d wip",
                    "git tag --delete wip", "git tag -v wip", "git tag --verify wip", "git tag --contains develop",
                    "git tag --points-at HEAD", "git tag --merged develop", "git tag --sort=-creatordate")

    def test_a_tag_the_parser_cannot_read_asks_with_a_generic_reason(self):
        for command in ("bash -c 'git tag wip'", "sudo git tag wip", "if true; then git tag wip; fi"):
            self.assertIn("could not read", self.asked(command), command)

    def test_a_tag_in_a_project_without_the_gemba_section_prints_nothing(self):
        repo = make_repo(None)
        self.addCleanup(subprocess.run, ["rm", "-rf", repo])
        self.passes("git tag wip", "bash -c 'git tag wip'", repo=repo)


class RegisteredInThePlugin(unittest.TestCase):
    def test_the_script_is_registered_as_its_own_bash_hook_before_the_tool_runs(self):
        with open(os.path.join(ROOT, "hooks", "hooks.json"), encoding="utf-8") as f:
            entries = json.load(f)["hooks"]["PreToolUse"]
        commands = [h["command"] for e in entries if e.get("matcher") == "Bash" for h in e["hooks"]]
        self.assertIn('python3 "${CLAUDE_PLUGIN_ROOT}/hooks/history_rules.py"', commands)


if __name__ == "__main__":
    unittest.main()
