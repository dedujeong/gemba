#!/usr/bin/env python3
"""PreToolUse hook: a Jira issue of the project's Jira Project is created with the fields of its work type.

Reads the hook event from stdin. It acts only on a `createJiraIssue` call of the Atlassian connector,
direct or through `executeWrite`, in a project with a `## Gemba` section, and only when the issue
belongs to that section's Jira Project. It then denies the call with one reason that lists every
missing or wrong field. In every other case it prints nothing. It never reads the Summary or the
description. A crash while handling a createJiraIssue call asks, so the call never passes unchecked.
"""
import datetime
import json
import os
import re
import sys

try:
    import git_commands
except ImportError:  # a crash here would not block, so main() asks for any createJiraIssue call
    git_commands = None


def output(decision, why):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": why,
    }}))


def ask(why):
    output("ask", f"Gemba rule (issue fields): {why} Confirm the issue has its fix version, component and estimate"
                  " (an Epic: due date). This comes from the Gemba Code plugin, not from Jira.")


class Unreadable(Exception):
    """The call carries something the hook cannot read, so it cannot check it."""


def load(value):
    """A JSON object given as a dict or as a JSON-encoded string; None is an empty object."""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            raise Unreadable("the hook could not read the arguments of the call, which are not valid JSON.")
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise Unreadable("the hook could not read the arguments of the call.")
    return value


def lenient(value):
    """Like load, but anything that is not a JSON object is an empty one, so the call still ends in an ask."""
    try:
        return load(value)
    except Unreadable:
        return {}


def create_arguments(event):
    """The arguments of a createJiraIssue call, direct or inside executeWrite, or None for any other call."""
    name = event.get("tool_name") or ""
    tool_input = event.get("tool_input") or {}
    if name.endswith("__createJiraIssue"):
        return tool_input
    if name.endswith("__executeWrite") and tool_input.get("name") == "createJiraIssue":
        return tool_input.get("inputs") or {}
    return None


def named(value):
    """The text of a Jira value given as a string or as {"name": ..} / {"key": ..}."""
    if isinstance(value, dict):
        value = value.get("name") or value.get("key")
    return value.strip() if isinstance(value, str) else ""


def key_of(value):
    """The text of a project given as a key or as {"key": ..}."""
    if isinstance(value, dict):
        value = value.get("key")
    return value.strip() if isinstance(value, str) else ""


class Issue:
    """The fields of the call, read from one place only: the REST-style `fields` object when the call has
    one, otherwise additional_fields and then the flat arguments. `prefix` names that place in the hints."""

    def __init__(self, flat):
        rest = flat.get("fields")
        if rest not in (None, "", [], {}):
            self.sources, self.prefix = [load(rest)], "fields"
        else:
            self.sources, self.prefix = [load(flat.get("additional_fields")), flat], "additional_fields"

    def get(self, *keys):
        for source in self.sources:
            for key in keys:
                if source.get(key) not in (None, "", [], {}):
                    return source[key]
        return None

    def kind(self):
        kind = named(self.get("issueType", "issuetype", "issueTypeName"))
        if not kind:
            raise Unreadable("the hook could not tell the work type of the issue.")
        return kind

    def component_names(self):
        """The names of the components that are present; one given only by id has the name ''."""
        value = self.get("components")
        names = []
        for item in value if isinstance(value, list) else []:
            if named(item):
                names.append(named(item))
            elif isinstance(item, dict) and str(item.get("id") or "").strip():
                names.append("")  # present, but its case cannot be checked
        return names

    def has_fix_versions(self):
        """True when fixVersions is a list whose every entry has a name or an id, or is a non-empty string."""
        value = self.get("fixVersions")
        if not isinstance(value, list) or not value:
            return False
        for item in value:
            if isinstance(item, dict):
                item = item.get("name") or item.get("id")
            if isinstance(item, int) and not isinstance(item, bool):
                item = str(item)
            if not isinstance(item, str) or not item.strip():
                return False
        return True

    def has_estimate(self):
        """An original estimate given as text or a positive number, in seconds, or as timeoriginalestimate."""
        tracking = self.get("timetracking")
        if isinstance(tracking, dict):
            original = tracking.get("originalEstimate")
            if positive(original) or (isinstance(original, str) and original.strip()):
                return True
            if positive(tracking.get("originalEstimateSeconds")):
                return True
        return positive(self.get("timeoriginalestimate"))


def positive(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def valid_due_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def epic_problems(issue):
    found = []
    at = issue.prefix
    if issue.component_names():
        found.append(("has a component, which an Epic must not have", f"Remove {at}.components"))
    if issue.has_estimate():
        found.append(("has an estimate, which an Epic must not have", f"Remove {at}.timetracking"))
    due = issue.get("duedate")
    if not due:
        found.append(("is missing a due date", f'Add {at}.duedate "<YYYY-MM-DD>"'))
    elif not valid_due_date(due):
        found.append(("has a due date that is not in the form YYYY-MM-DD", f'Use {at}.duedate "<YYYY-MM-DD>"'))
    return found


def other_problems(issue):
    found = []
    at = issue.prefix
    names = issue.component_names()
    if not names:
        found.append(("is missing a component", f'Add {at}.components [{{"name": "<component>"}}]'))
    for name in names:
        if name != name.lower():
            found.append((f'has the component "{name}", which is not lowercase',
                          f'Use {at}.components [{{"name": "{name.lower()}"}}] (lowercase)'))
    if not issue.has_estimate():
        found.append(("is missing an estimate", f'Add {at}.timetracking {{"originalEstimate": "<estimate>"}}'))
    return found


def problems(issue, kind):
    """What the issue lacks or has wrong, as (clause about the issue, how to fix it) pairs."""
    found = []
    if not issue.has_fix_versions():
        found.append(("is missing a fix version", f'Add {issue.prefix}.fixVersions [{{"name": "<version>"}}]'))
    rules = epic_problems if kind.lower() == "epic" else other_problems
    return found + rules(issue)


def sentence(kind, found):
    clauses = "; ".join(clause for clause, _ in found)
    fixes = ". ".join(fix for _, fix in found)
    return (f"Gemba rule (issue fields): this {kind or 'issue'} {clauses}. {fixes}."
            " Then call createJiraIssue again. This block comes from the Gemba Code plugin, not from Jira.")


def decide(event, args):
    cwd = event.get("cwd") or os.getcwd()
    mine = git_commands.gemba_field(cwd, "Jira Project")
    if not mine:  # no Gemba section, or none with a Jira Project: not a Gemba project
        return
    flat = lenient(args)
    key = key_of(flat.get("projectKey") or flat.get("project"))
    if key and key.lower() != mine.lower():
        return  # another project: nothing else is parsed
    issue = Issue(flat)
    key = key or key_of(issue.get("projectKey", "project"))
    if not key:
        raise Unreadable("the hook could not tell the project of the issue.")
    if key.lower() != mine.lower():
        return
    kind = issue.kind()
    found = problems(issue, kind)
    if found:
        output("deny", sentence(kind, found))


def main():
    try:
        event = json.load(sys.stdin)
        args = create_arguments(event)
    except (ValueError, AttributeError):
        return
    if args is None:
        return
    if git_commands is None:
        ask("the hook that checks the fields of a new Jira issue could not load.")
        return
    try:
        decide(event, args)
    except Unreadable as why:
        ask(str(why))
    except Exception:
        # A crash exits non-zero and does not block, so the issue would be created unchecked: fail closed.
        ask("the hook that checks the fields of a new Jira issue failed.")


if __name__ == "__main__":
    main()
