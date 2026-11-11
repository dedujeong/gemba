import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, "hooks")

CRASH = """
import json, sys
sys.path.insert(0, sys.argv[1])
import importlib
module = importlib.import_module(sys.argv[2])
def boom(*args):
    raise RuntimeError("forced crash")
module.decide = boom
module.main()
"""


def crash_decision(hook, command):
    event = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}, "cwd": HOOKS}
    result = subprocess.run([sys.executable, "-c", CRASH, HOOKS, hook], input=json.dumps(event),
                            capture_output=True, text=True)
    return json.loads(result.stdout)["hookSpecificOutput"] if result.stdout else None


class CrashAsks(unittest.TestCase):
    def assertAsks(self, hook, command):
        out = crash_decision(hook, command)
        self.assertIsNotNone(out, f"{hook} printed nothing when it crashed on: {command}")
        self.assertEqual(out["permissionDecision"], "ask", command)

    def test_confirm_push(self):
        self.assertAsks("confirm_push", "git push origin develop")

    def test_commit_rules(self):
        self.assertAsks("commit_rules", "git commit -m 'x'")

    def test_commit_rules_merge_continue(self):
        self.assertAsks("commit_rules", "git merge --continue")

    def test_branch_rules(self):
        self.assertAsks("branch_rules", "git switch -c feature/GEMBA-1-x")

    def test_history_rules(self):
        self.assertAsks("history_rules", "git rebase main")

    def test_integration_rules_push(self):
        self.assertAsks("integration_rules", "git push origin develop")

    def test_integration_rules_gh_pr_merge(self):
        self.assertAsks("integration_rules", "gh pr merge 12")

    def test_a_crash_on_an_unrelated_command_stays_quiet(self):
        self.assertIsNone(crash_decision("commit_rules", "git status"))


if __name__ == "__main__":
    unittest.main()
