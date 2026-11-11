import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_confirm_push_hook import make_repo  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "hooks", "jira_issue_rules.py")
MATCHER = r"mcp__.*__(createJiraIssue|executeWrite)"
CLAUDE_CODE = "mcp__claude_ai_Atlassian_MCP__"
CLAUDE_AI = "mcp__Atlassian_MCP__"

VERSION = {"fixVersions": [{"name": "ABC v1.0.0"}]}


def direct(fields, issue_type="Story", project="ABC", prefix=CLAUDE_CODE):
    """A createJiraIssue call as the direct tool records it: flat arguments, extras in additional_fields."""
    tool_input = {"cloudId": "c1", "projectKey": project, "summary": "S", "issueType": issue_type}
    if fields is not None:
        tool_input["additional_fields"] = fields
    return prefix + "createJiraIssue", tool_input


def write_nested(fields, issue_type="Story", project="ABC", prefix=CLAUDE_AI):
    """The same call through executeWrite, with the extras inside additional_fields."""
    inputs = {"projectKey": project, "summary": "S", "issueType": issue_type}
    if fields is not None:
        inputs["additional_fields"] = fields
    return prefix + "executeWrite", {"cloudId": "c1", "name": "createJiraIssue", "inputs": inputs}


def write_flat(fields, issue_type="Story", project="ABC", prefix=CLAUDE_CODE):
    """executeWrite with the fields flat in inputs, the type as {"name": ..} and the project as {"key": ..}."""
    inputs = {"project": {"key": project}, "summary": "S", "issuetype": {"name": issue_type}}
    inputs.update(fields or {})
    return prefix + "executeWrite", {"cloudId": "c1", "name": "createJiraIssue", "inputs": inputs}


SHAPES = (direct, write_nested, write_flat)


def run_hook(repo, tool_name, tool_input):
    event = {"hook_event_name": "PreToolUse", "tool_name": tool_name, "tool_input": tool_input, "cwd": repo}
    return subprocess.run([sys.executable, SCRIPT], input=json.dumps(event), cwd=repo, capture_output=True, text=True)


def decision(result):
    if not result.stdout.strip():
        return None
    return json.loads(result.stdout)["hookSpecificOutput"]


class HookCase(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo()
        self.addCleanup(subprocess.run, ["rm", "-rf", self.repo])

    def run_call(self, call):
        result = run_hook(self.repo, *call)
        self.assertEqual(result.returncode, 0, result.stderr)
        return decision(result)

    def denied(self, call):
        out = self.run_call(call)
        self.assertIsNotNone(out, "the hook printed nothing")
        self.assertEqual(out["hookEventName"], "PreToolUse")
        self.assertEqual(out["permissionDecision"], "deny")
        return out["permissionDecisionReason"]

    def passes(self, call):
        self.assertIsNone(self.run_call(call))


class FixVersion(HookCase):
    def test_an_issue_without_additional_fields_is_denied_for_every_shape(self):
        for shape in SHAPES:
            with self.subTest(shape=shape.__name__):
                reason = self.denied(shape(None))
                self.assertIn("Gemba rule", reason)
                self.assertIn("fixVersions", reason)
                self.assertIn("fix version", reason)

    def test_an_empty_fix_version_list_is_denied(self):
        self.denied(direct({"fixVersions": []}))

    def test_the_reason_says_what_to_add_and_that_it_is_not_a_jira_error(self):
        reason = self.denied(direct(None))
        self.assertIn('additional_fields.fixVersions [{"name": "<version>"}]', reason)
        self.assertIn("call createJiraIssue again", reason)
        self.assertIn("Gemba Code plugin, not from Jira", reason)

    def test_an_issue_with_a_fix_version_is_not_denied_for_this_rule(self):
        for shape in SHAPES:
            with self.subTest(shape=shape.__name__):
                out = self.run_call(shape(dict(VERSION)))
                if out is not None:
                    self.assertNotIn("fixVersions", out["permissionDecisionReason"])

    def test_the_project_key_is_compared_ignoring_case(self):
        self.denied(direct(None, project="abc"))

    def test_an_issue_of_another_jira_project_is_not_checked(self):
        for shape in SHAPES:
            with self.subTest(shape=shape.__name__):
                self.passes(shape(None, project="OTHER"))

    def test_a_project_without_a_gemba_section_is_not_checked(self):
        self.repo = make_repo(claude_md="# Notes\n")
        self.passes(direct(None))

    def test_other_executeWrite_operations_print_nothing(self):
        tool, tool_input = write_nested(None)
        tool_input["name"] = "editJiraIssue"
        self.passes((tool, tool_input))

    def test_other_connector_tools_print_nothing(self):
        self.passes((CLAUDE_CODE + "getJiraIssue", {"cloudId": "c1", "issueIdOrKey": "ABC-1"}))
        self.passes((CLAUDE_CODE + "editJiraIssue", {"cloudId": "c1", "issueIdOrKey": "ABC-1"}))

    def test_non_json_input_prints_nothing(self):
        result = subprocess.run([sys.executable, SCRIPT], input="not json", capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout), (0, ""))


GOOD = {**VERSION, "components": [{"name": "hooks"}], "timetracking": {"originalEstimate": "3h"}}


class ComponentAndEstimate(HookCase):
    def test_a_complete_issue_passes_for_every_shape_and_type(self):
        for shape in SHAPES:
            for kind in ("Story", "Task", "Bug", "Spike"):
                with self.subTest(shape=shape.__name__, kind=kind):
                    self.passes(shape(dict(GOOD), issue_type=kind))

    def test_an_issue_without_a_component_is_denied(self):
        for shape in SHAPES:
            with self.subTest(shape=shape.__name__):
                fields = {k: v for k, v in GOOD.items() if k != "components"}
                reason = self.denied(shape(fields))
                self.assertIn("component", reason)
                self.assertIn('additional_fields.components [{"name": "<component>"}]', reason)
                self.assertNotIn("fixVersions [", reason)
                self.assertNotIn("originalEstimate", reason)

    def test_an_empty_component_list_is_denied(self):
        self.denied(direct({**GOOD, "components": []}))

    def test_an_issue_without_an_estimate_is_denied(self):
        for shape in SHAPES:
            with self.subTest(shape=shape.__name__):
                fields = {k: v for k, v in GOOD.items() if k != "timetracking"}
                reason = self.denied(shape(fields))
                self.assertIn("estimate", reason)
                self.assertIn('additional_fields.timetracking {"originalEstimate": "<estimate>"}', reason)

    def test_a_timetracking_without_original_estimate_is_denied(self):
        self.denied(direct({**GOOD, "timetracking": {"remainingEstimate": "1h"}}))

    def test_a_component_in_uppercase_is_denied_and_the_reason_gives_the_lowercase_name(self):
        for shape in SHAPES:
            with self.subTest(shape=shape.__name__):
                reason = self.denied(shape({**GOOD, "components": [{"name": "Hooks"}]}))
                self.assertIn("Hooks", reason)
                self.assertIn("lowercase", reason)
                self.assertIn('"hooks"', reason)

    def test_a_component_given_as_a_string_is_read_too(self):
        self.passes(direct({**GOOD, "components": ["hooks"]}))
        self.denied(direct({**GOOD, "components": ["HOOKS"]}))

    def test_every_problem_is_listed_in_one_reason(self):
        reason = self.denied(direct(None))
        for word in ("fixVersions", "components", "timetracking"):
            self.assertIn(word, reason)

    def test_the_summary_and_the_description_are_never_read(self):
        tool, tool_input = direct(dict(GOOD))
        tool_input["summary"] = {"not": "a string"}
        tool_input["description"] = 12
        self.passes((tool, tool_input))


EPIC = {**VERSION, "duedate": "2026-12-31"}


class EpicFields(HookCase):
    def test_an_epic_with_a_fix_version_and_a_due_date_passes_for_every_shape(self):
        for shape in SHAPES:
            with self.subTest(shape=shape.__name__):
                self.passes(shape(dict(EPIC), issue_type="Epic"))

    def test_an_epic_with_a_component_is_denied(self):
        for shape in SHAPES:
            with self.subTest(shape=shape.__name__):
                reason = self.denied(shape({**EPIC, "components": [{"name": "hooks"}]}, issue_type="Epic"))
                self.assertIn("Epic", reason)
                self.assertIn("component", reason)
                self.assertIn("must not", reason)
                self.assertIn("Remove additional_fields.components", reason)
                self.assertNotIn("duedate", reason)

    def test_an_epic_with_an_estimate_is_denied(self):
        for shape in SHAPES:
            with self.subTest(shape=shape.__name__):
                reason = self.denied(shape({**EPIC, "timetracking": {"originalEstimate": "3h"}}, issue_type="Epic"))
                self.assertIn("estimate", reason)
                self.assertIn("Remove additional_fields.timetracking", reason)

    def test_an_epic_without_a_due_date_is_denied(self):
        for shape in SHAPES:
            with self.subTest(shape=shape.__name__):
                reason = self.denied(shape(dict(VERSION), issue_type="Epic"))
                self.assertIn("due date", reason)
                self.assertIn('additional_fields.duedate "<YYYY-MM-DD>"', reason)

    def test_an_epic_without_a_fix_version_is_still_denied(self):
        self.assertIn("fixVersions", self.denied(direct({"duedate": "2026-12-31"}, issue_type="Epic")))

    def test_an_epic_does_not_need_a_component_or_an_estimate(self):
        reason = self.denied(direct(None, issue_type="Epic"))
        self.assertNotIn("is missing a component", reason)
        self.assertNotIn("is missing an estimate", reason)

    def test_every_epic_problem_is_listed_in_one_reason(self):
        fields = {"components": [{"name": "hooks"}], "timetracking": {"originalEstimate": "3h"}}
        reason = self.denied(direct(fields, issue_type="epic"))
        for word in ("fixVersions", "components", "timetracking", "duedate"):
            self.assertIn(word, reason)

    def test_a_due_date_on_another_type_is_not_checked(self):
        self.passes(direct({**GOOD, "duedate": "2026-12-31"}))
        self.passes(direct(dict(GOOD)))


def call_direct(tool_input):
    return CLAUDE_CODE + "createJiraIssue", {"cloudId": "c1", **tool_input}


def call_write(inputs, prefix=CLAUDE_CODE):
    return prefix + "executeWrite", {"cloudId": "c1", "name": "createJiraIssue", "inputs": inputs}


class RealCallShapes(HookCase):
    def asked(self, call):
        out = self.run_call(call)
        self.assertIsNotNone(out, "the hook printed nothing")
        self.assertEqual(out["permissionDecision"], "ask")
        self.assertIn("Gemba Code plugin, not from Jira", out["permissionDecisionReason"])
        return out["permissionDecisionReason"]

    def test_the_work_type_is_read_from_issueTypeName(self):
        reason = self.denied(call_direct({"projectKey": "ABC", "issueTypeName": "Epic", "additional_fields": dict(VERSION)}))
        self.assertIn("due date", reason)
        self.passes(call_direct({"projectKey": "ABC", "issueTypeName": "Epic", "additional_fields": dict(EPIC)}))
        self.passes(call_direct({"projectKey": "ABC", "issueTypeName": "Story", "additional_fields": dict(GOOD)}))

    def test_additional_fields_given_as_a_json_string_are_read(self):
        base = {"projectKey": "ABC", "issueType": "Story"}
        self.passes(call_direct({**base, "additional_fields": json.dumps(GOOD)}))
        self.assertIn("component", self.denied(call_direct({**base, "additional_fields": json.dumps(VERSION)})))

    def test_additional_fields_that_do_not_parse_ask(self):
        self.asked(call_direct({"projectKey": "ABC", "issueType": "Story", "additional_fields": "{not json"}))

    def test_executeWrite_inputs_given_as_a_json_string_are_read(self):
        inputs = {"projectKey": "ABC", "issueType": "Story", "additional_fields": dict(GOOD)}
        self.passes(call_write(json.dumps(inputs)))
        inputs["additional_fields"] = dict(VERSION)
        self.assertIn("component", self.denied(call_write(json.dumps(inputs))))

    def test_executeWrite_inputs_that_do_not_parse_ask(self):
        self.asked(call_write("{not json"))

    def test_unreadable_arguments_of_another_project_session_are_not_asked(self):
        self.repo = make_repo(claude_md="# Notes\n")
        self.passes(call_write("{not json"))


class FailsClosed(unittest.TestCase):
    def alone(self, tool_name, tool_input):
        """Runs a copy of the script with no git_commands next to it, so its import fails."""
        folder = tempfile.mkdtemp()
        self.addCleanup(subprocess.run, ["rm", "-rf", folder])
        script = os.path.join(folder, "jira_issue_rules.py")
        shutil.copy(SCRIPT, script)
        event = {"hook_event_name": "PreToolUse", "tool_name": tool_name, "tool_input": tool_input, "cwd": folder}
        return subprocess.run([sys.executable, script], input=json.dumps(event), cwd=folder, capture_output=True, text=True)

    def test_a_create_call_asks_when_the_parser_cannot_be_loaded(self):
        for shape in (direct, write_nested):
            with self.subTest(shape=shape.__name__):
                result = self.alone(*shape(None))
                self.assertEqual(result.returncode, 0, result.stderr)
                out = decision(result)
                self.assertEqual(out["permissionDecision"], "ask")
                self.assertIn("Gemba Code plugin, not from Jira", out["permissionDecisionReason"])

    def test_any_other_call_prints_nothing_when_the_parser_cannot_be_loaded(self):
        self.assertEqual(self.alone(CLAUDE_CODE + "getJiraIssue", {"cloudId": "c1"}).stdout, "")
        tool, tool_input = write_nested(None)
        tool_input["name"] = "editJiraIssue"
        self.assertEqual(self.alone(tool, tool_input).stdout, "")


class RegisteredInThePlugin(unittest.TestCase):
    def entries(self):
        with open(os.path.join(ROOT, "hooks", "hooks.json"), encoding="utf-8") as f:
            return json.load(f)["hooks"]["PreToolUse"]

    def test_the_script_is_registered_with_the_connector_matcher(self):
        entries = [e for e in self.entries() if e.get("matcher") == MATCHER]
        commands = [h["command"] for e in entries for h in e["hooks"] if h["type"] == "command"]
        self.assertEqual(commands, ['python3 "${CLAUDE_PLUGIN_ROOT}/hooks/jira_issue_rules.py"'])

    def test_the_matcher_covers_both_hosts_and_only_the_write_tools(self):
        for prefix in (CLAUDE_CODE, CLAUDE_AI):
            for name in ("createJiraIssue", "executeWrite"):
                self.assertTrue(re.fullmatch(MATCHER, prefix + name), prefix + name)
        for other in ("mcp__x__getJiraIssue", CLAUDE_CODE + "editJiraIssue", "Bash"):
            self.assertFalse(re.fullmatch(MATCHER, other), other)


if __name__ == "__main__":
    unittest.main()
