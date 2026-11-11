import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "hooks"))

import git_commands  # noqa: E402
from git_commands import GitCommand, git_commands as commands_of, mentions, parse, segments  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
