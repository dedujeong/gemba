"""Every hook decides the project by the repository the command runs in, and the history and integration
hooks share one rule for syncing a branch with its own remote (GEMBA-184)."""
import json
import os
import subprocess
import sys
import unittest

from test_confirm_push_hook import decision, git, make_repo
from test_integration_rules_hook import claude_md

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(hook, folder, command):
    event = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}, "cwd": folder}
    result = subprocess.run([sys.executable, os.path.join(ROOT, "hooks", hook + ".py")], input=json.dumps(event),
                            cwd=folder, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return decision(result)


class Case(unittest.TestCase):
    def repo(self, claude=None, integration="merge"):
        folder = make_repo(claude_md(integration) if claude else None)
        self.addCleanup(subprocess.run, ["rm", "-rf", folder])
        return folder

    def verdict(self, hook, folder, command):
        out = run(hook, folder, command)
        return out and out["permissionDecision"]


class SessionFolderDoesNotDecideAnotherRepository(Case):
    def test_commit_history_and_branch_rules_skip_a_repository_without_a_gemba_section(self):
        session, other = self.repo(claude=True), self.repo()
        for hook, command in (("commit_rules", f"git -C {other} commit --allow-empty -m wip"),
                              ("commit_rules", f"cd {other} && git commit --allow-empty -m wip"),
                              ("history_rules", f"git -C {other} push --force origin main"),
                              ("history_rules", f"git -C {other} rebase main"),
                              ("branch_rules", f"git -C {other} switch -c wip"),
                              ("integration_rules", f"git -C {other} push origin wip"),
                              ("confirm_push", f"git -C {other} push origin wip")):
            self.assertIsNone(run(hook, session, command), (hook, command))

    def test_the_repository_with_a_gemba_section_is_still_checked_from_outside(self):
        session, project = self.repo(), self.repo(claude=True)
        self.assertEqual(self.verdict("commit_rules", session, f"git -C {project} commit --allow-empty -m wip"), "deny")


class GitDirAndWorkTreeBelongToTheRepositoryTheyName(Case):
    def test_a_force_push_through_git_dir_work_tree_or_the_env_is_checked_from_outside_the_project(self):
        session, project = self.repo(), self.repo(claude=True)
        for command in (f"git --git-dir={project}/.git push --force origin main",
                        f"git --git-dir {project}/.git push --force origin main",
                        f"git --work-tree={project} push --force origin main",
                        f"GIT_DIR={project}/.git git push --force origin main",
                        f"GIT_WORK_TREE={project} git push --force origin main",
                        f"cd {project} && git --git-dir=.git push --force origin main"):
            self.assertEqual(self.verdict("history_rules", session, command), "deny", command)

    def test_a_push_of_a_work_branch_through_git_dir_is_checked_by_the_integration_hook(self):
        session, project = self.repo(), self.repo(claude=True)
        self.assertEqual(self.verdict("integration_rules", session, f"git --git-dir={project}/.git push origin story/ABC-1-x"), "deny")

    def test_git_dir_of_an_unrelated_repository_is_not_checked_from_a_project(self):
        session, other = self.repo(claude=True), self.repo()
        self.assertIsNone(run("history_rules", session, f"git --git-dir={other}/.git push --force origin main"))
        self.assertIsNone(run("history_rules", session, f"GIT_DIR={other}/.git git push --force origin main"))


class GhPrMergeIsCheckedWhereItRuns(Case):
    def test_after_a_cd_into_the_project_it_is_denied_from_a_session_outside(self):
        session, project = self.repo(), self.repo(claude=True, integration="pull request")
        self.assertEqual(self.verdict("integration_rules", session, f"cd {project} && gh pr merge 3"), "deny")

    def test_after_a_cd_out_of_the_project_it_passes(self):
        session, other = self.repo(claude=True, integration="pull request"), self.repo()
        self.assertIsNone(run("integration_rules", session, f"cd {other} && gh pr merge 3"))

    def test_in_the_session_project_it_is_still_denied(self):
        session = self.repo(claude=True, integration="pull request")
        self.assertEqual(self.verdict("integration_rules", session, "gh pr merge 3"), "deny")


class SyncingWithItsOwnRemoteIsOneRule(Case):
    def setUp(self):
        self.project = self.repo(claude=True, integration="pull request")
        git(self.project, "remote", "add", "upstream", "https://example.com/acme/up.git")

    def test_any_configured_remote_or_the_upstream_syncs_in_both_hooks(self):
        for command in ("git merge --ff-only upstream/develop", "git merge upstream/develop", "git merge @{upstream}",
                        "git merge @{u}", "git pull upstream develop"):
            self.assertIsNone(run("history_rules", self.project, command), command)
        for command in ("git merge --ff-only upstream/develop", "git merge --ff-only @{upstream}", "git pull upstream develop"):
            self.assertIsNone(run("integration_rules", self.project, command), command)

    def test_a_pull_of_another_branch_keeps_its_real_remote(self):
        out = run("history_rules", self.project, "git pull upstream feature")
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIsNone(run("history_rules", self.project, "git pull"))

    def test_another_branch_of_the_remote_or_an_unknown_remote_does_not_sync(self):
        for command in ("git merge upstream/feature", "git merge nowhere/develop", "git pull nowhere develop"):
            self.assertEqual(self.verdict("history_rules", self.project, command), "deny", command)
