import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "hooks"))

import git_commands  # noqa: E402
from git_commands import GitCommand, emit, git_commands as commands_of, mentions, parse, segments, unparsed_mentions  # noqa: E402


def only(command):
    found = commands_of(command)
    assert len(found) == 1, found
    return found[0]


class SegmentsTest(unittest.TestCase):
    def test_splits_a_compound_command(self):
        self.assertEqual(list(segments("a && b || c; d | e & f")), [["a"], ["b"], ["c"], ["d"], ["e"], ["f"]])

    def test_splits_on_a_new_line(self):
        self.assertEqual(list(segments("git status\ngit log")), [["git", "status"], ["git", "log"]])

    def test_separators_inside_quotes_stay(self):
        self.assertEqual(list(segments('git commit -m "a && b"')), [["git", "commit", "-m", "a && b"]])


class ParseTest(unittest.TestCase):
    def test_not_a_git_command_is_none(self):
        self.assertIsNone(parse(["ls", "-la"]))
        self.assertIsNone(parse([]))
        self.assertIsNone(parse(["FOO=1"]))
        self.assertIsNone(parse(["git"]))

    def test_basic_command(self):
        self.assertEqual(parse(["git", "status"]), GitCommand(None, "status", [], []))

    def test_git_is_matched_by_basename(self):
        self.assertEqual(parse(["/usr/bin/git", "log"]).subcommand, "log")

    def test_skips_environment_prefix(self):
        self.assertEqual(parse(["A=1", "B=2", "git", "log"]).subcommand, "log")

    def test_folder_from_dash_c_capital(self):
        command = parse(["git", "-C", "sub", "status"])
        self.assertEqual((command.folder, command.subcommand), ("sub", "status"))

    def test_global_options_with_a_value_are_skipped(self):
        command = parse(["git", "-c", "user.name=x", "--git-dir", "d", "--no-pager", "log"])
        self.assertEqual((command.folder, command.subcommand), (None, "log"))

    def test_long_option_with_equals(self):
        self.assertEqual(parse(["git", "commit", "--message=hello"]).options, [("--message", "hello")])

    def test_long_option_with_a_separate_value(self):
        self.assertEqual(parse(["git", "commit", "--message", "hello"]).options, [("--message", "hello")])

    def test_short_option_with_a_separate_value(self):
        self.assertEqual(parse(["git", "commit", "-m", "hello"]).options, [("-m", "hello")])

    def test_short_option_with_an_attached_value(self):
        self.assertEqual(parse(["git", "commit", "-mhello"]).options, [("-m", "hello")])

    def test_bundled_short_flags_end_in_a_value_option(self):
        self.assertEqual(parse(["git", "commit", "-am", "msg"]).options, [("-a", None), ("-m", "msg")])

    def test_bundled_short_flags_with_an_attached_value(self):
        self.assertEqual(parse(["git", "commit", "-ammsg"]).options, [("-a", None), ("-m", "msg")])

    def test_message_with_spaces_in_quotes(self):
        command = only('git commit -m "feat(x): add a thing" --no-verify')
        self.assertEqual(command.options, [("-m", "feat(x): add a thing"), ("--no-verify", None)])

    def test_multiple_messages_keep_their_order(self):
        command = only('git commit -m "title" -m "body"')
        self.assertEqual(command.options, [("-m", "title"), ("-m", "body")])

    def test_flags_have_no_value(self):
        self.assertEqual(parse(["git", "push", "--force", "-u"]).options, [("--force", None), ("-u", None)])

    def test_push_positionals_and_value_options(self):
        command = parse(["git", "push", "-o", "ci.skip", "origin", "main", "--tags"])
        self.assertEqual(command.options, [("-o", "ci.skip"), ("--tags", None)])
        self.assertEqual(command.args, ["origin", "main"])

    def test_branch_set_upstream_to_takes_a_value(self):
        self.assertEqual(parse(["git", "branch", "-u", "origin/x", "y"]).options, [("-u", "origin/x")])
        self.assertEqual(parse(["git", "branch", "-u", "origin/x", "y"]).args, ["y"])

    def test_branch_delete_takes_no_value(self):
        command = parse(["git", "branch", "-d", "old"])
        self.assertEqual((command.options, command.args), ([("-d", None)], ["old"]))

    def test_switch_and_checkout_create(self):
        self.assertEqual(parse(["git", "switch", "-c", "new", "main"]).options, [("-c", "new")])
        self.assertEqual(parse(["git", "checkout", "-b", "new"]).options, [("-b", "new")])
        self.assertEqual(parse(["git", "checkout", "-b", "new"]).args, [])

    def test_worktree_add_keeps_the_action_as_first_arg(self):
        command = parse(["git", "worktree", "add", "-b", "task/x", "../wt", "develop"])
        self.assertEqual(command.subcommand, "worktree")
        self.assertEqual(command.options, [("-b", "task/x")])
        self.assertEqual(command.args, ["add", "../wt", "develop"])

    def test_tag_message_and_rebase_onto(self):
        self.assertEqual(parse(["git", "tag", "-m", "m", "v1"]).options, [("-m", "m")])
        self.assertEqual(parse(["git", "rebase", "--onto", "a", "b"]).options, [("--onto", "a")])

    def test_merge_and_pull_strategies(self):
        self.assertEqual(parse(["git", "merge", "-s", "ours", "x"]).options, [("-s", "ours")])
        self.assertEqual(parse(["git", "pull", "-X", "theirs"]).options, [("-X", "theirs")])

    def test_double_dash_ends_the_options(self):
        command = parse(["git", "checkout", "--", "-weird", "file"])
        self.assertEqual((command.options, command.args), ([], ["-weird", "file"]))

    def test_trailing_comment_is_dropped(self):
        command = parse(["git", "commit", "-m", "x", "#", "a", "note"])
        self.assertEqual((command.options, command.args), ([("-m", "x")], []))
        self.assertEqual(parse(["git", "push", "origin", "#", "-f"]).args, ["origin"])

    def test_value_option_without_a_value_at_the_end(self):
        self.assertEqual(parse(["git", "commit", "-m"]).options, [("-m", None)])


class OptionsFoundInReviewTest(unittest.TestCase):
    def test_branch_track_is_a_flag_and_keeps_the_branch_name(self):
        self.assertEqual(parse(["git", "branch", "-t", "new", "origin/main"]),
                         GitCommand(None, "branch", [("-t", None)], ["new", "origin/main"]))

    def test_pull_long_strategy_options_take_a_value(self):
        self.assertEqual(parse(["git", "pull", "--strategy", "ours", "--strategy-option", "theirs", "origin", "main"]),
                         GitCommand(None, "pull", [("--strategy", "ours"), ("--strategy-option", "theirs")], ["origin", "main"]))

    def test_commit_trailer_cleanup_and_pathspec_file_take_a_value(self):
        found = parse(["git", "commit", "--trailer", "Co: x", "--cleanup", "strip", "--pathspec-from-file", "f", "-m", "m"])
        self.assertEqual(found.options, [("--trailer", "Co: x"), ("--cleanup", "strip"), ("--pathspec-from-file", "f"), ("-m", "m")])
        self.assertEqual(found.args, [])

    def test_repeated_dash_c_folders_add_up_like_in_git(self):
        self.assertEqual(parse(["git", "-C", "a", "-C", "b", "push"]).folder, os.path.join("a", "b"))

    def test_an_absolute_dash_c_folder_replaces_the_one_before(self):
        self.assertEqual(parse(["git", "-C", "a", "-C", "/b", "push"]).folder, "/b")


class GitCommandsTest(unittest.TestCase):
    def test_every_git_segment_is_listed(self):
        found = commands_of("git add . && echo hi && git -C sub commit -m x")
        self.assertEqual([c.subcommand for c in found], ["add", "commit"])
        self.assertEqual(found[1].folder, "sub")

    def test_new_line_separated_commands(self):
        self.assertEqual([c.subcommand for c in commands_of("git add .\ngit commit -m x")], ["add", "commit"])

    def test_no_git_command(self):
        self.assertEqual(commands_of("ls && echo git commit"), [])


class ResolvedFoldersTest(unittest.TestCase):
    def test_with_cwd_the_folder_is_cwd_or_the_dash_c_folder_joined_to_it(self):
        found = commands_of("git status && git -C sub log", "/work")
        self.assertEqual([command.folder for command in found], ["/work", os.path.join("/work", "sub")])

    def test_an_absolute_dash_c_folder_stays_absolute(self):
        self.assertEqual(commands_of("git -C /other push", "/work")[0].folder, "/other")


class MentionsTest(unittest.TestCase):
    def test_wrapped_command_is_mentioned(self):
        self.assertTrue(mentions('bash -c "git commit -m x"', "commit"))

    def test_other_subcommand_is_not(self):
        self.assertFalse(mentions('bash -c "git status"', "commit"))

    def test_across_lines(self):
        self.assertTrue(mentions("git add .\ngit commit", "commit"))

    def test_subcommand_is_a_whole_word(self):
        self.assertFalse(mentions("git recommit", "commit"))


def run(folder, *args):
    subprocess.run(["git", "-C", folder, *args], check=True, capture_output=True)


class RepoHelpersTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = os.path.realpath(self.tmp.name)
        run(self.repo, "init", "-q", "-b", "main")
        run(self.repo, "config", "user.email", "t@example.com")
        run(self.repo, "config", "user.name", "T")

    def write_claude(self, text):
        with open(os.path.join(self.repo, "CLAUDE.md"), "w", encoding="utf-8") as f:
            f.write(text)

    def test_git_returns_stdout_or_empty(self):
        self.assertEqual(git_commands.git(self.repo, "rev-parse", "--show-toplevel"), self.repo)
        self.assertEqual(git_commands.git(self.repo, "no-such-command"), "")

    def test_has_gemba(self):
        self.assertFalse(git_commands.has_gemba(self.repo))
        self.write_claude("## Gemba\n\n- Integration: merge\n")
        self.assertTrue(git_commands.has_gemba(self.repo))

    def test_gemba_field_reads_integration(self):
        self.write_claude("# P\n\n## Gemba\n\n- Jira Project: ABC\n- Integration: pull-request\n- Language: es-MX\n")
        self.assertEqual(git_commands.gemba_field(self.repo, "Integration"), "pull-request")
        self.assertEqual(git_commands.gemba_field(self.repo, "Jira Project"), "ABC")

    def test_gemba_field_missing_field_is_none(self):
        self.write_claude("## Gemba\n\n- Jira Project: ABC\n")
        self.assertIsNone(git_commands.gemba_field(self.repo, "Integration"))

    def test_gemba_field_outside_the_section_is_none(self):
        self.write_claude("## Other\n\n- Integration: merge\n\n## Gemba\n\n- Jira Project: ABC\n\n## After\n\n- Language: es-MX\n")
        self.assertIsNone(git_commands.gemba_field(self.repo, "Integration"))
        self.assertIsNone(git_commands.gemba_field(self.repo, "Language"))

    def test_gemba_field_without_claude_md_is_none(self):
        self.assertIsNone(git_commands.gemba_field(self.repo, "Integration"))

    def test_gemba_field_found_from_a_subfolder(self):
        self.write_claude("## Gemba\n\n- Integration: merge\n")
        sub = os.path.join(self.repo, "a", "b")
        os.makedirs(sub)
        self.assertEqual(git_commands.gemba_field(sub, "Integration"), "merge")

    def test_in_gemba_project_reads_the_command_folder_or_the_session_folder(self):
        self.write_claude("## Gemba\n\n- Jira Project: ABC\n")
        outside = tempfile.mkdtemp()
        self.addCleanup(subprocess.run, ["rm", "-rf", outside])
        self.assertTrue(git_commands.in_gemba_project(self.repo, outside))
        self.assertTrue(git_commands.in_gemba_project(outside, self.repo))
        self.assertFalse(git_commands.in_gemba_project(outside, outside))

    def test_current_branch(self):
        run(self.repo, "checkout", "-q", "-b", "task/ABC-1-x")
        self.assertEqual(git_commands.current_branch(self.repo), "task/ABC-1-x")


class NewValueOptionsTest(unittest.TestCase):
    def test_worktree_reason_takes_a_value(self):
        found = parse(["git", "worktree", "lock", "--reason", "why", "../wt"])
        self.assertEqual((found.options, found.args), ([("--reason", "why")], ["lock", "../wt"]))

    def test_tag_listing_options_take_a_value(self):
        found = parse(["git", "tag", "--contains", "abc", "--sort", "v:refname", "--format", "%(refname)", "-l"])
        self.assertEqual(found.options, [("--contains", "abc"), ("--sort", "v:refname"), ("--format", "%(refname)"), ("-l", None)])
        self.assertEqual(found.args, [])
        for name in ("--cleanup", "--no-contains", "--points-at", "--merged", "--no-merged"):
            with self.subTest(name=name):
                self.assertEqual(parse(["git", "tag", name, "x", "v1"]).options, [(name, "x")])


def init_repo(branch="main"):
    folder = tempfile.mkdtemp()
    folder = os.path.realpath(folder)
    run(folder, "init", "-q", "-b", branch)
    run(folder, "config", "user.email", "t@example.com")
    run(folder, "config", "user.name", "T")
    run(folder, "commit", "-q", "--allow-empty", "-m", "start")
    return folder


class ContextTrackingTest(unittest.TestCase):
    def setUp(self):
        self.repo = init_repo()
        self.addCleanup(shutil.rmtree, self.repo)
        run(self.repo, "branch", "develop")
        os.makedirs(os.path.join(self.repo, "sub"))
        self.other = init_repo("other-main")
        self.addCleanup(shutil.rmtree, self.other)

    def folders(self, command, cwd=None):
        return [c.folder for c in commands_of(command, cwd or self.repo)]

    def branches(self, command, cwd=None):
        return [c.branch for c in commands_of(command, cwd or self.repo)]

    def test_the_branch_field_defaults_to_none_and_parse_keeps_working(self):
        self.assertIsNone(parse(["git", "status"]).branch)
        self.assertEqual(GitCommand(None, "status", [], []).branch, None)
        self.assertIsNone(commands_of("git status")[0].branch)

    def test_the_first_command_gets_the_real_branch_of_its_folder(self):
        self.assertEqual(self.branches("git status"), ["main"])
        self.assertEqual(self.branches(f"git -C {self.other} status"), ["other-main"])

    def test_a_detached_head_has_an_empty_branch(self):
        run(self.repo, "checkout", "-q", "--detach")
        self.assertEqual(self.branches("git status"), [""])

    def test_cd_changes_the_folder_of_the_later_commands(self):
        self.assertEqual(self.folders("cd sub && git status"), [os.path.join(self.repo, "sub")])
        self.assertEqual(self.folders(f"cd {self.other} && git status"), [self.other])
        self.assertEqual(self.branches(f"cd {self.other} && git status"), ["other-main"])

    def test_cd_is_relative_to_the_current_folder(self):
        found = self.folders("cd sub && cd .. && git status")
        self.assertEqual(found, [self.repo])

    def test_a_dash_c_folder_is_relative_to_the_folder_after_cd(self):
        self.assertEqual(self.folders(f"cd {self.repo} && git -C sub status"), [os.path.join(self.repo, "sub")])

    def test_commands_before_the_cd_keep_the_old_folder(self):
        self.assertEqual(self.folders(f"git status; cd {self.other}; git status"), [self.repo, self.other])

    def test_cd_alone_or_dash_makes_the_folder_unknown(self):
        self.assertEqual(self.folders("cd && git status"), [None])
        self.assertEqual(self.folders("cd - && git status"), [None])
        self.assertEqual(self.branches("cd && git status"), [None])

    def test_a_cd_with_a_variable_makes_the_folder_unknown(self):
        self.assertEqual(self.folders("cd $DIR && git status"), [None])

    def test_an_absolute_dash_c_folder_is_known_after_an_unknown_cd(self):
        self.assertEqual(self.folders(f"cd && git -C {self.other} status"), [self.other])
        self.assertEqual(self.folders("cd && git -C sub status"), [None])

    def test_a_cd_inside_a_subshell_ends_with_it(self):
        self.assertEqual(self.folders(f"(cd {self.other} && git status) && git log"), [self.other, self.repo])

    def test_a_cd_in_a_pipeline_or_in_the_background_does_not_change_the_folder(self):
        self.assertEqual(self.folders(f"cd {self.other} | git status"), [self.repo])
        self.assertEqual(self.folders(f"cd {self.other} & git status"), [self.repo])

    def test_switch_and_checkout_set_the_branch_of_later_commands(self):
        self.assertEqual(self.branches("git switch develop && git commit -m x"), ["main", "develop"])
        self.assertEqual(self.branches("git checkout develop && git commit -m x"), ["main", "develop"])
        self.assertEqual(self.branches("git switch develop; git status; git switch main; git status"),
                         ["main", "develop", "develop", "main"])

    def test_creating_a_branch_sets_it_to_the_new_name(self):
        self.assertEqual(self.branches("git switch -c story/A-1-x && git commit -m x"), ["main", "story/A-1-x"])
        self.assertEqual(self.branches("git switch -C story/A-1-x develop && git commit -m x"), ["main", "story/A-1-x"])
        self.assertEqual(self.branches("git checkout -b story/A-1-x && git commit -m x"), ["main", "story/A-1-x"])
        self.assertEqual(self.branches("git checkout -B story/A-1-x develop && git commit -m x"), ["main", "story/A-1-x"])

    def test_a_path_checkout_keeps_the_branch(self):
        self.assertEqual(self.branches("git checkout -- develop && git status"), ["main", "main"])
        self.assertEqual(self.branches("git checkout . && git status"), ["main", "main"])
        self.assertEqual(self.branches("git checkout sub && git status"), ["main", "main"])
        self.assertEqual(self.branches("git checkout develop -- sub && git status"), ["main", "main"])

    def test_switching_to_the_previous_branch_makes_it_unknown(self):
        self.assertEqual(self.branches("git switch - && git status"), ["main", None])
        self.assertEqual(self.branches("git checkout - && git status"), ["main", None])

    def test_a_detached_switch_has_an_empty_branch(self):
        self.assertEqual(self.branches("git switch --detach HEAD && git status"), ["main", ""])

    def test_a_switch_applies_to_the_folder_it_runs_in(self):
        found = self.branches(f"git -C {self.other} switch -c x && git status && git -C {self.other} status")
        self.assertEqual(found, ["other-main", "main", "x"])

    def test_a_switch_after_a_cd_applies_to_that_folder(self):
        found = self.branches(f"cd {self.other} && git switch -c x && git status && cd {self.repo} && git status")
        self.assertEqual(found, ["other-main", "x", "main"])

    def test_the_branch_is_read_once_per_folder(self):
        with mock.patch.object(git_commands, "current_branch", return_value="b") as read:
            commands_of("git status && git log && git -C /elsewhere log && git status", self.repo)
        self.assertEqual(read.call_count, 2)

    def test_without_cwd_the_branch_is_not_read(self):
        self.assertEqual([c.branch for c in commands_of("git switch -c x && git status")], [None, None])

    def test_an_unreadable_command_gives_no_commands(self):
        self.assertEqual(commands_of('git commit -m "unbalanced', self.repo), [])


class UnparsedMentionsTest(unittest.TestCase):
    def test_a_wrapped_command_is_found(self):
        self.assertTrue(unparsed_mentions("bash -c 'git push --force'", "push"))
        self.assertTrue(unparsed_mentions('sudo git commit -m "x"', "commit"))
        self.assertTrue(unparsed_mentions("if true; then git push; fi", "push"))

    def test_the_arguments_of_a_parsed_command_are_not_searched(self):
        self.assertFalse(unparsed_mentions('git commit -m "fix the merge"', "merge"))
        self.assertFalse(unparsed_mentions("git log --grep commit", "commit"))
        self.assertFalse(unparsed_mentions("git commit-graph write", "commit"))
        self.assertFalse(unparsed_mentions("git rev-parse HEAD^{commit}", "commit"))
        self.assertFalse(unparsed_mentions('git commit -m "git push now"', "push"))

    def test_a_wrapped_command_next_to_a_parsed_one_is_found(self):
        self.assertTrue(unparsed_mentions("git status && bash -c 'git push --force'", "push"))

    def test_a_hyphenated_name_is_not_the_subcommand(self):
        self.assertFalse(unparsed_mentions("bash -c 'git commit-graph write'", "commit"))

    def test_a_compiled_pattern_is_used_as_it_is(self):
        pattern = re.compile(r"\bgit\b.*--force")
        self.assertTrue(unparsed_mentions("bash -c 'git push --force'", pattern))
        self.assertFalse(unparsed_mentions("git push --force", pattern))

    def test_an_unreadable_command_is_searched_whole(self):
        self.assertTrue(unparsed_mentions('git commit -m "unbalanced', "commit"))
        self.assertTrue(unparsed_mentions("echo 'x; git push", "push"))
        self.assertFalse(unparsed_mentions('git status "unbalanced', "push"))


class EmitTest(unittest.TestCase):
    def test_prints_the_pretooluse_decision(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            emit("deny", "because")
        self.assertEqual(json.loads(out.getvalue()), {"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "because"}})


class SecondReviewTest(unittest.TestCase):
    def setUp(self):
        self.repo = init_repo()
        self.addCleanup(shutil.rmtree, self.repo)
        run(self.repo, "branch", "develop")
        os.makedirs(os.path.join(self.repo, "sub"))

    def branches(self, command):
        return [c.branch for c in commands_of(command, self.repo)]

    def test_the_tracked_branch_belongs_to_the_repository_not_the_folder(self):
        self.assertEqual(self.branches("git switch develop && git -C sub status"), ["main", "develop"])
        self.assertEqual(self.branches("git switch develop && cd sub && git status"), ["main", "develop"])
        self.assertEqual(self.branches("cd sub && git switch develop && cd .. && git status"), ["main", "develop"])

    def test_another_repository_keeps_its_own_branch(self):
        other = init_repo("other-main")
        self.addCleanup(shutil.rmtree, other)
        self.assertEqual(self.branches(f"git switch develop && git -C {other} status"), ["main", "other-main"])

    def test_track_options_are_flags(self):
        self.assertEqual(parse(["git", "checkout", "-t", "origin/x"]), GitCommand(None, "checkout", [("-t", None)], ["origin/x"]))
        self.assertEqual(parse(["git", "checkout", "--track", "origin/x"]).options, [("--track", None)])
        self.assertEqual(parse(["git", "switch", "--track=direct", "origin/x"]).options, [("--track", "direct")])
        self.assertEqual(parse(["git", "switch", "--track", "origin/x"]).args, ["origin/x"])

    def test_tracking_a_remote_branch_checks_out_the_local_branch(self):
        self.assertEqual(self.branches("git checkout -t origin/feat && git status"), ["main", "feat"])
        self.assertEqual(self.branches("git checkout --track origin/story/A-1-x && git status"), ["main", "story/A-1-x"])
        self.assertEqual(self.branches("git switch --track origin/feat && git status"), ["main", "feat"])
        self.assertEqual(self.branches("git switch -t origin/develop && git status"), ["main", "develop"])

    def test_a_new_name_wins_over_the_tracked_one(self):
        self.assertEqual(self.branches("git checkout -b mine -t origin/develop && git status"), ["main", "mine"])

    def test_the_claude_md_is_read_once_per_repository(self):
        with open(os.path.join(self.repo, "CLAUDE.md"), "w", encoding="utf-8") as f:
            f.write("## Gemba\n\n- Jira Project: ABC\n")
        self.assertEqual(git_commands.gemba_field(self.repo, "Jira Project"), "ABC")
        with mock.patch.object(git_commands, "git", side_effect=AssertionError("git ran")), \
                mock.patch("builtins.open", side_effect=AssertionError("file read")):
            self.assertEqual(git_commands.gemba_field(self.repo, "Jira Project"), "ABC")
            self.assertTrue(git_commands.has_gemba(self.repo))

    def test_a_changed_claude_md_is_read_again(self):
        path = os.path.join(self.repo, "CLAUDE.md")
        self.assertFalse(git_commands.has_gemba(self.repo))
        with open(path, "w", encoding="utf-8") as f:
            f.write("## Gemba\n")
        self.assertTrue(git_commands.has_gemba(self.repo))

    def test_the_repository_key_is_the_same_from_every_folder_of_it(self):
        self.assertEqual(git_commands.repository_key(self.repo), git_commands.repository_key(os.path.join(self.repo, "sub")))
        other = init_repo()
        self.addCleanup(shutil.rmtree, other)
        self.assertNotEqual(git_commands.repository_key(self.repo), git_commands.repository_key(other))


if __name__ == "__main__":
    unittest.main()
