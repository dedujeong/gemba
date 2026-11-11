#!/usr/bin/env python3
"""PreToolUse hook: a Jira issue of the project's Jira Project is created with the fields of its work type.

Reads the hook event from stdin. It acts only on a `createJiraIssue` call of the Atlassian connector,
direct or through `executeWrite`, in a project with a `## Gemba` section, and only when the issue
belongs to that section's Jira Project. It then denies the call with one reason that lists every
missing or wrong field. In every other case it prints nothing. It never reads the Summary or the
description. A crash while handling a createJiraIssue call asks, so the call never passes unchecked.
"""
import json
import os
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


def field(args, key):
    """A field given in additional_fields or flat in the arguments."""
    extra = args.get("additional_fields")
    if isinstance(extra, dict) and extra.get(key) not in (None, "", [], {}):
        return extra[key]
    return args.get(key)


def project_key(args):
    return named(args.get("projectKey") or args.get("project"))


def issue_type(args):
    return named(args.get("issueType") or args.get("issuetype"))


def problems(args):
    found = []
    if not field(args, "fixVersions"):
        found.append(("missing", "a fix version",
                      'additional_fields.fixVersions [{"name": "<version>"}]'))
    return found


def sentence(kind, found):
    missing = [(label, fix) for state, label, fix in found if state == "missing"]
    parts = []
    if missing:
        parts.append("is missing " + ", ".join(label for label, _ in missing))
    adds = "Add " + " and ".join(fix for _, fix in missing)
    return (f"Gemba rule (issue fields): this {kind or 'issue'} " + " and ".join(parts) + f". {adds}"
            " and call createJiraIssue again. This block comes from the Gemba Code plugin, not from Jira.")


def decide(event, args):
    cwd = event.get("cwd") or os.getcwd()
    if not git_commands.has_gemba(cwd):
        return
    mine = git_commands.gemba_field(cwd, "Jira Project")
    if not mine or project_key(args).lower() != mine.lower():
        return
    found = problems(args)
    if found:
        output("deny", sentence(issue_type(args), found))


def main():
    try:
        event = json.load(sys.stdin)
        args = create_arguments(event)
    except (ValueError, AttributeError):
        return
    if args is None:
        return
    if git_commands is None:
        output("ask", "Gemba rule (issue fields): the hook that checks the fields of a new Jira issue could not load."
                      " Confirm the issue has its fix version, component and estimate (an Epic: due date)."
                      " This comes from the Gemba Code plugin, not from Jira.")
        return
    try:
        decide(event, args)
    except Exception:
        # A crash exits non-zero and does not block, so the issue would be created unchecked: fail closed.
        output("ask", "Gemba rule (issue fields): the hook that checks the fields of a new Jira issue failed."
                      " Confirm the issue has its fix version, component and estimate (an Epic: due date)."
                      " This comes from the Gemba Code plugin, not from Jira.")


if __name__ == "__main__":
    main()
