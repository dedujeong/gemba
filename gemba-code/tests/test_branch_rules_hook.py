import json
import os
import shutil
import subprocess
import sys
import tempfile
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

    def test_a_branch_creation_with_any_leading_option_is_checked(self):
        for option in ("--no-track", "--track=direct", "--track=inherit", "--create-reflog", "--recurse-submodules",
                       "--no-color", "--color=never", "--no-create-reflog", "-t", "--no-recurse-submodules"):
            for command in (f"git branch {option} feature/login", f"git branch {option} feature/login develop",
                            f"git -C . branch {option} feature/login"):
                with self.subTest(command=command):
                    self.assertIn("feature/login", self.denied(command))
            with self.subTest(option=option):
                self.passes(f"git branch {option} story/ABC-2-b develop")

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


class TheKeyIsTheProjectKey(HookTestCase):
    def test_a_key_that_is_not_the_jira_project_is_denied(self):
        for command in ("git switch -c story/XYZ-1-a develop", "git branch task/AB-2-b develop",
                        "git checkout -b bug/ABCD-3-c develop", "git worktree add -b spike/ABC2-4-d ../w develop"):
            with self.subTest(command=command):
                reason = self.denied(command)
                self.assertIn("Jira Project", reason)
                self.assertIn("ABC", reason)

    def test_the_key_of_the_project_passes(self):
        self.passes("git switch -c story/ABC-1-a develop")

    def test_without_the_field_any_key_is_accepted(self):
        other = make_repo(claude_md="## Gemba\n\n- Language: es-MX\n")
        self.addCleanup(subprocess.run, ["rm", "-rf", other])
        self.passes("git switch -c story/XYZ-1-a develop", other)
        self.denied_in(other, "git switch -c feature/x develop")

    def test_the_case_of_the_field_is_the_one_written(self):
        other = make_repo(claude_md="## Gemba\n\n- Jira Project: Abc\n")
        self.addCleanup(subprocess.run, ["rm", "-rf", other])
        self.denied_in(other, "git switch -c story/ABC-1-a develop")

    def denied_in(self, repo, command):
        out = self.decide(command, repo)
        self.assertIsNotNone(out, command)
        self.assertEqual(out["permissionDecision"], "deny", command)


class PassesAValidName(HookTestCase):
    def test_valid_names_of_the_four_types_print_nothing(self):
        for name in ("story/ABC-12-login", "task/ABC-3-add-tests", "bug/ABC-45-fix-the-crash", "spike/ABC-9-try-x2"):
            with self.subTest(name=name):
                self.passes(f"git switch -c {name} develop")
                self.passes(f"git branch -c develop {name}")

    def test_commands_that_do_not_create_or_rename_a_branch_print_nothing(self):
        for command in ("git branch", "git branch --show-current", "git branch -a", "git branch -vv",
                        "git branch --list feature/*", "git branch -d feature/login", "git branch -D feature/login",
                        "git branch --contains abc123", "git branch -u origin/develop",
                        "git branch --set-upstream-to=origin/develop",
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

    def test_a_repository_without_setup_is_not_checked_even_when_the_session_folder_has_setup(self):
        other = make_repo(claude_md="# Notes\n")
        self.addCleanup(subprocess.run, ["rm", "-rf", other])
        event = {"tool_name": "Bash", "cwd": self.repo,
                 "tool_input": {"command": f"git -C {other} switch -c feature/login"}}
        result = subprocess.run([sys.executable, SCRIPT], input=json.dumps(event), capture_output=True, text=True)
        self.assertIsNone(decision(result))


class AsksWhenItCannotRead(HookTestCase):
    def test_a_wrapped_creation_asks_with_a_generic_reason(self):
        for command in ("bash -c 'git switch -c feature/login'", "sudo git checkout -b feature/login",
                        'bash -c "git branch feature/login"', "sh -c 'git branch -m new-name'",
                        "bash -c 'git worktree add -b x ../w develop'"):
            with self.subTest(command=command):
                reason = self.asked(command)
                self.assertTrue(reason.startswith("Gemba rule (branches): "), reason)
                self.assertIn("could not read", reason)

    def test_a_wrapped_creation_with_leading_options_asks_and_a_wrapped_listing_does_not(self):
        for command in ("bash -c 'git branch --no-track feature/login'", "sudo git branch --track=direct x develop"):
            with self.subTest(command=command):
                self.asked(command)
        for command in ("bash -c 'git branch --no-color'", "bash -c 'git branch --list x'", "sudo git branch -d x",
                        "bash -c 'git branch --sort=-committerdate'", "bash -c 'git checkout develop'"):
            with self.subTest(command=command):
                self.passes(command)

    def test_a_wrapped_creation_after_another_command_asks_and_a_commit_message_does_not(self):
        self.asked("git status; bash -c 'git branch badname'")
        self.passes("git commit -m 'fix branch handling'")
        self.passes("git status; bash -c 'git branch --show-current'")

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
            with open(os.path.join(ROOT, "hooks", "git_commands.py"), encoding="utf-8") as real:
                f.write(real.read())
            f.write("\n\ndef git_commands(*a, **k):\n    raise RuntimeError('boom')\n")
        hooks = os.path.join(sitecustomize_dir, "branch_rules.py")
        shutil.copy(os.path.join(ROOT, "hooks", "fallback_words.py"), sitecustomize_dir)
        with open(SCRIPT, encoding="utf-8") as f, open(hooks, "w", encoding="utf-8") as g:
            g.write(f.read())

        def run(command):
            event = {"tool_name": "Bash", "cwd": self.repo, "tool_input": {"command": command}}
            return subprocess.run([sys.executable, hooks], input=json.dumps(event), capture_output=True, text=True)
        self.assertEqual(decision(run("git switch -c feature/login"))["permissionDecision"], "ask")
        self.assertIsNone(decision(run("git status")))


class FallbacksMatchTheSameCreations(HookTestCase):
    def standalone(self, command):
        """The hook alone in a folder: its parser module cannot be imported."""
        folder = tempfile.mkdtemp(dir=self.repo)
        hook = os.path.join(folder, "branch_rules.py")
        shutil.copy(os.path.join(ROOT, "hooks", "fallback_words.py"), folder)
        with open(SCRIPT, encoding="utf-8") as f, open(hook, "w", encoding="utf-8") as g:
            g.write(f.read())
        event = {"tool_name": "Bash", "cwd": self.repo, "tool_input": {"command": command}}
        return subprocess.run([sys.executable, hook], input=json.dumps(event), capture_output=True, text=True)

    def crashing(self, command):
        folder = tempfile.mkdtemp(dir=self.repo)
        with open(os.path.join(ROOT, "hooks", "git_commands.py"), encoding="utf-8") as real, \
                open(os.path.join(folder, "git_commands.py"), "w", encoding="utf-8") as f:
            f.write(real.read() + "\n\ndef git_commands(*a, **k):\n    raise RuntimeError('boom')\n")
        shutil.copy(os.path.join(ROOT, "hooks", "fallback_words.py"), folder)
        with open(SCRIPT, encoding="utf-8") as f, open(os.path.join(folder, "branch_rules.py"), "w", encoding="utf-8") as g:
            g.write(f.read())
        event = {"tool_name": "Bash", "cwd": self.repo, "tool_input": {"command": command}}
        return subprocess.run([sys.executable, os.path.join(folder, "branch_rules.py")], input=json.dumps(event),
                              capture_output=True, text=True)

    CREATIONS = ("git switch -c x", "git checkout -b x", "git branch x", "git branch -m x", "git branch -c old x",
                 "git worktree add -b x ../w", "git switch --orphan x", "git branch -f x develop",
                 "git checkout --orphan x")
    OTHERS = ("git status", "git branch -a", "git branch --show-current", "git branch -d x", "git switch develop")

    def test_the_import_error_and_the_crash_ask_for_the_same_creations(self):
        for command in self.CREATIONS:
            with self.subTest(command=command):
                self.assertEqual(decision(self.standalone(command))["permissionDecision"], "ask")
                self.assertEqual(decision(self.crashing(command))["permissionDecision"], "ask")
        for command in self.OTHERS:
            with self.subTest(command=command):
                self.assertIsNone(decision(self.standalone(command)))
                self.assertIsNone(decision(self.crashing(command)))


class BlocksABaseThatIsNotDevelop(HookTestCase):
    def test_a_start_point_that_is_not_develop_is_denied_in_every_form(self):
        for start in ("main", "origin/develop", "story/ABC-1-a", "abc1234"):
            for command in (f"git switch -c story/ABC-2-b {start}", f"git checkout -b story/ABC-2-b {start}",
                            f"git branch story/ABC-2-b {start}",
                            f"git worktree add -b story/ABC-2-b ../w {start}"):
                with self.subTest(command=command):
                    reason = self.denied(command)
                    self.assertTrue(reason.startswith("Gemba rule (branches): "), reason)
                    self.assertIn("develop", reason)
                    self.assertIn(start, reason)

    def test_without_a_start_point_the_current_branch_must_be_develop(self):
        git(self.repo, "checkout", "-q", "-b", "story/ABC-1-a")
        for command in ("git switch -c story/ABC-2-b", "git checkout -b story/ABC-2-b", "git branch story/ABC-2-b",
                        "git worktree add -b story/ABC-2-b ../w"):
            with self.subTest(command=command):
                reason = self.denied(command)
                self.assertIn("story/ABC-1-a", reason)
                self.assertIn("develop", reason)

    def test_a_detached_head_is_not_develop(self):
        git(self.repo, "checkout", "-q", "--detach")
        self.assertIn("develop", self.denied("git switch -c story/ABC-2-b"))

    def test_the_folder_of_dash_c_is_the_one_checked(self):
        other = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", other])
        git(other, "checkout", "-q", "-b", "task/ABC-5-x")
        self.denied(f"git -C {other} switch -c story/ABC-2-b")
        self.passes(f"git -C {self.repo} switch -c story/ABC-2-b", other)

    def test_a_name_that_breaks_the_form_is_denied_for_the_name_first(self):
        self.assertIn("is not <type>/<KEY>-<slug>", self.denied("git switch -c feature/login main"))


class PassesDevelopAsBase(HookTestCase):
    def test_a_valid_name_from_develop_passes_in_every_form(self):
        for command in ("git switch -c story/ABC-2-b", "git switch -c story/ABC-2-b develop",
                        "git switch -C story/ABC-2-b develop", "git checkout -b task/ABC-2-b develop",
                        "git checkout -B bug/ABC-2-b", "git branch story/ABC-2-b", "git branch story/ABC-2-b develop",
                        "git branch -f story/ABC-2-b develop", "git branch --track story/ABC-2-b develop",
                        "git worktree add -b story/ABC-2-b ../w develop", "git worktree add -b story/ABC-2-b ../w",
                        "git -C . switch -c story/ABC-2-b"):
            with self.subTest(command=command):
                self.passes(command)

    def test_a_spike_worktree_from_develop_passes_inside_the_worktree_too(self):
        worktree = os.path.join(self.repo, ".claude", "worktrees", "ABC-9-try")
        git(self.repo, "worktree", "add", "-q", "-b", "spike/ABC-9-try", worktree, "develop")
        self.passes("git worktree add -b spike/ABC-10-other ../ABC-10-other develop", worktree)
        self.passes("git switch -c task/ABC-11-x develop", worktree)
        self.passes(f"git -C {self.repo} worktree add -b spike/ABC-12-y .claude/worktrees/ABC-12-y develop", worktree)
        self.passes(f"git -C {self.repo} switch -c story/ABC-13-z", worktree)

    def test_the_spike_worktree_command_of_the_implement_skill_passes(self):
        self.passes("git worktree add -b spike/ABC-9-try .claude/worktrees/ABC-9-try develop")

    def test_a_rename_has_no_base_check(self):
        git(self.repo, "checkout", "-q", "-b", "story/ABC-1-a")
        self.passes("git branch -m story/ABC-1-b")
        self.passes("git branch -M story/ABC-1-a story/ABC-1-b")


class TheBaseIsTheTrackedBranch(HookTestCase):
    def test_a_switch_to_develop_before_the_creation_makes_develop_the_base(self):
        git(self.repo, "checkout", "-q", "-b", "story/ABC-1-a")
        self.passes("git switch develop && git switch -c story/ABC-2-b")
        self.passes("git checkout develop && git checkout -b story/ABC-2-b")
        self.passes("git checkout develop; git branch story/ABC-2-b")
        self.passes("git switch develop && git worktree add -b story/ABC-2-b ../w")
        self.denied("git switch -c story/ABC-2-b")

    def test_a_switch_away_from_develop_before_the_creation_makes_it_the_wrong_base(self):
        git(self.repo, "branch", "story/ABC-1-a")
        self.assertIn("story/ABC-1-a", self.denied("git switch story/ABC-1-a && git switch -c story/ABC-2-b"))

    def test_a_cd_before_the_command_is_followed(self):
        other = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", other])
        git(other, "checkout", "-q", "-b", "task/ABC-5-x")
        self.denied(f"cd {other} && git switch -c story/ABC-2-b")
        self.passes(f"cd {self.repo} && git switch -c story/ABC-2-b", other)

    def test_a_folder_or_a_branch_that_cannot_be_told_asks(self):
        self.asked("cd $SOMEWHERE && git switch -c story/ABC-2-b")
        self.asked("git switch - && git switch -c story/ABC-2-b")

    def test_head_and_at_are_develop_only_when_the_tracked_branch_is_develop(self):
        self.passes("git switch -c story/ABC-2-b HEAD")
        self.passes("git switch -c story/ABC-2-b @")
        self.passes("git worktree add -b story/ABC-2-b ../w HEAD")
        git(self.repo, "checkout", "-q", "-b", "story/ABC-1-a")
        self.denied("git switch -c story/ABC-2-b HEAD")
        self.denied("git switch -c story/ABC-2-b @")
        self.passes("git switch develop && git switch -c story/ABC-2-b HEAD")

    def test_the_other_spellings_of_the_local_develop_pass(self):
        git(self.repo, "checkout", "-q", "-b", "story/ABC-1-a")
        for command in ("git switch -c story/ABC-2-b refs/heads/develop", "git branch story/ABC-2-b refs/heads/develop",
                        "git worktree add -b story/ABC-2-b ../w refs/heads/develop"):
            with self.subTest(command=command):
                self.passes(command)

    def test_origin_develop_is_denied_and_the_reason_says_the_rule_is_the_local_develop(self):
        reason = self.denied("git switch -c story/ABC-2-b origin/develop")
        self.assertIn("origin/develop", reason)
        self.assertIn("local develop", reason)

    def test_a_worktree_with_the_lock_and_a_reason_passes(self):
        self.passes("git worktree add --lock --reason wip -b spike/ABC-1-x ../w develop")
        self.denied("git worktree add --lock --reason wip -b spike/ABC-1-x ../w main")


class CopiesOrphansAndRenames(HookTestCase):
    def test_a_copy_is_checked_by_its_new_name(self):
        for flag in ("-c", "-C", "--copy"):
            for command in (f"git branch {flag} old feature/login", f"git branch {flag} feature/login"):
                with self.subTest(command=command):
                    self.assertIn("feature/login", self.denied(command))

    def test_a_copy_is_based_on_the_old_branch_or_the_current_one(self):
        self.passes("git branch -c develop story/ABC-2-b")
        self.passes("git branch --copy story/ABC-2-b")
        self.assertIn("main", self.denied("git branch -c main story/ABC-2-b"))
        git(self.repo, "checkout", "-q", "-b", "story/ABC-1-a")
        self.assertIn("story/ABC-1-a", self.denied("git branch -C story/ABC-2-b"))
        self.passes("git branch -c develop story/ABC-2-b")

    def test_an_orphan_branch_is_checked_by_name_and_denied_as_not_from_develop(self):
        for command in ("git switch --orphan feature/x", "git checkout --orphan feature/x"):
            with self.subTest(command=command):
                self.assertIn("feature/x", self.denied(command))
        for command in ("git switch --orphan story/ABC-2-b", "git checkout --orphan story/ABC-2-b",
                        "git checkout --orphan story/ABC-2-b develop"):
            with self.subTest(command=command):
                reason = self.denied(command)
                self.assertIn("orphan", reason)
                self.assertIn("develop", reason)

    def test_renaming_develop_or_main_away_is_denied(self):
        git(self.repo, "branch", "main")
        for command in ("git branch -m develop story/ABC-2-b", "git branch -M main story/ABC-2-b",
                        "git branch --move develop story/ABC-2-b", "git branch -m story/ABC-2-b"):
            with self.subTest(command=command):
                self.assertIn("rename", self.denied(command))
        git(self.repo, "checkout", "-q", "main")
        self.assertIn("main", self.denied("git branch -m story/ABC-2-b"))

    def test_renaming_another_branch_still_passes(self):
        git(self.repo, "checkout", "-q", "-b", "story/ABC-1-a")
        self.passes("git branch -m story/ABC-1-b")
        self.passes("git branch -m story/ABC-1-a story/ABC-1-b")
        self.passes("git branch -m task/ABC-1-a task/ABC-1-b")


class WorktreesWithoutADashB(HookTestCase):
    def test_the_branch_named_after_the_path_is_checked_like_a_creation(self):
        reason = self.denied("git worktree add ../feature-login")
        self.assertIn("feature-login", reason)
        self.assertIn("<type>/<KEY>-<slug>", reason)
        self.assertIn("feature-login", self.denied("git worktree add .claude/worktrees/feature-login/"))

    def test_a_commit_ish_a_detached_worktree_or_an_existing_branch_is_not_a_creation(self):
        git(self.repo, "branch", "existing")
        for command in ("git worktree add ../w develop", "git worktree add ../w main", "git worktree add --detach ../w",
                        "git worktree add -d ../w", "git worktree add ../existing", "git worktree add -f ../w HEAD",
                        "git worktree list", "git worktree remove ../w"):
            with self.subTest(command=command):
                self.passes(command)


class WorktreeOrphans(HookTestCase):
    def test_an_orphan_worktree_is_checked_by_name_and_denied_as_not_from_develop(self):
        self.assertIn("feature/x", self.denied("git worktree add --orphan -b feature/x ../w"))
        reason = self.denied("git worktree add --orphan -b story/ABC-2-b ../w")
        self.assertIn("orphan", reason)
        self.assertIn("develop", reason)
        self.assertIn("git worktree add -b story/ABC-2-b <path> develop", reason)

    def test_an_orphan_worktree_with_the_option_after_the_path_is_denied_too(self):
        self.assertIn("orphan", self.denied("git worktree add -b story/ABC-2-b ../w --orphan"))


class ForcedUpdatesOfAnExistingBranch(HookTestCase):
    def test_a_forced_update_of_an_existing_branch_is_not_a_creation(self):
        git(self.repo, "branch", "feature/old")
        git(self.repo, "branch", "story/ABC-1-a")
        for command in ("git branch -f feature/old main", "git branch --force story/ABC-1-a origin/develop",
                        "git checkout -B feature/old main", "git switch -C feature/old main",
                        "git switch --force-create story/ABC-1-a main", "git worktree add -B feature/old ../w main"):
            with self.subTest(command=command):
                self.passes(command)

    def test_the_same_commands_on_a_branch_that_does_not_exist_are_creations(self):
        for command in ("git branch -f feature/new main", "git checkout -B feature/new develop",
                        "git switch -C story/ABC-2-b main", "git worktree add -B story/ABC-2-b ../w main"):
            with self.subTest(command=command):
                self.denied(command)

    def test_a_lowercase_b_still_checks_a_name_that_exists_as_a_creation_error(self):
        git(self.repo, "branch", "feature/old")
        self.denied("git checkout -b feature/old main")  # git itself refuses, the hook still checks it


class TheReasonSuggestsTheSameForm(HookTestCase):
    def test_each_form_is_suggested_back(self):
        git(self.repo, "checkout", "-q", "-b", "story/ABC-1-a")
        for command, suggestion in (
                ("git worktree add -b story/ABC-2-b ../w", "git worktree add -b story/ABC-2-b <path> develop"),
                ("git checkout -b story/ABC-2-b", "git checkout -b story/ABC-2-b develop"),
                ("git branch story/ABC-2-b", "git branch story/ABC-2-b develop"),
                ("git switch -c story/ABC-2-b", "git switch -c story/ABC-2-b develop")):
            with self.subTest(command=command):
                self.assertIn(suggestion, self.denied(command))


class RegisteredInThePlugin(unittest.TestCase):
    def test_the_dispatcher_registered_for_bash_runs_the_script_before_the_tool_runs(self):
        with open(os.path.join(ROOT, "hooks", "hooks.json"), encoding="utf-8") as f:
            entries = json.load(f)["hooks"]["PreToolUse"]
        commands = [(entry["matcher"], hook["command"]) for entry in entries for hook in entry["hooks"]]
        self.assertIn(("Bash", 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/bash_rules.py"'), commands)
        with open(os.path.join(ROOT, "hooks", "bash_rules.py"), encoding="utf-8") as f:
            self.assertIn('"branch_rules"', f.read())


if __name__ == "__main__":
    unittest.main()
