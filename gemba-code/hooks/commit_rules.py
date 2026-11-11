#!/usr/bin/env python3
"""PreToolUse hook: every `git commit` of a project with setup follows the commit rules.

Reads the hook event from stdin. When a Bash command contains a `git commit` and the project's
CLAUDE.md has a `## Gemba` section, it checks the message against the rules of references/context.md
(Commits). A message that breaks one is denied with the rule it breaks; a message the hook cannot
read from the command asks for confirmation. In every other case it prints nothing, so the normal
permission flow is untouched. It never allows and never commits.
"""
import json
import os
import re
import sys

try:
    import git_commands
except ImportError:  # a crash here would not block, so main() asks for any command that mentions a commit
    git_commands = None

TYPES = ("build", "chore", "ci", "docs", "feat", "fix", "perf", "refactor", "revert", "style", "test")
HEADER = re.compile(r"(\w+)(?:\(([^)]*)\))?!?: \S.*", re.DOTALL)
ANY_JIRA_KEY = r"[A-Z][A-Z0-9]+"
REVERT = re.compile(r'Revert ".+"(\n\nThis reverts commit [0-9a-f]{7,40}\.)?')
FORMAT = "`<type>(<scope>): <description>`"
EXAMPLE = "for example `feat(hooks): block commit messages that break the commit format`"

PROTECTED_BRANCHES = ("main", "develop")
REUSES_A_MESSAGE = {"--fixup", "--squash", "--no-edit", "-C", "--reuse-message"}
MESSAGE_FROM_A_FILE = {"-F", "--file", "-t", "--template"}


def rule(problem, fix):
    return f"Gemba rule (commits): {problem}. {fix}."


def unreadable(why):
    return rule(f"the commit message could not be read from the command ({why})",
                f"Write it with -m as one line, {FORMAT}, so the hook can check it")


def message_problem(message, project=None):
    """The reason a message breaks the rules, or None when it follows them. `project` is the Jira
    Project of the Gemba section: only its keys count, so words like UTF-8 are not taken for one."""
    message = message.rstrip("\n")
    if message == "Initial commit" or message.startswith(("Merge ", "fixup! ", "squash! ")):
        return None
    if REVERT.fullmatch(message):
        return None
    if "\n" in message:
        return rule("the message has more than one line (a body or a footer)",
                    f"Use one line only, {FORMAT}, with no body and no footer")
    header = HEADER.fullmatch(message)
    if header is None:
        return rule(f"the message is not {FORMAT}", f"Start it with a type and a colon, {EXAMPLE}")
    kind, scope = header.group(1), header.group(2)
    if kind not in TYPES:
        return rule(f"`{kind}` is not an allowed type", f"Use one of {', '.join(TYPES)}, {EXAMPLE}")
    if re.search(rf"\b{re.escape(project) if project else ANY_JIRA_KEY}-\d+\b", message):
        return rule("the message has a Jira key", "Remove it: the branch and the work item link the commit, not the message")
    if scope is not None and not re.fullmatch(r"[a-z0-9-]+", scope):
        return rule(f"the scope `{scope}` is not in lowercase", "Write the scope in lowercase, one of the project's Jira components")
    if message.endswith("."):
        return rule("the description ends with a period", "Remove the final period")
    return None


def messages_problem(messages, project=None):
    if len(messages) > 1:
        full = "\n\n".join(messages)
        return message_problem(full, project) if REVERT.fullmatch(full) else rule(
            "the message has more than one line (several -m options make a body)",
            f"Use one -m with one line, {FORMAT}, and no body")
    return message_problem(messages[0], project)


def branch_problem(folder):
    """The reason a commit cannot land on the folder's branch, or None."""
    branch = git_commands.current_branch(folder)
    if branch not in PROTECTED_BRANCHES:
        return None
    if git_commands.git(folder, "rev-parse", "-q", "--verify", "MERGE_HEAD"):
        return None  # concluding a merge
    return rule(f"the current branch is `{branch}`, and nothing is committed on main or develop",
                "Create a branch for the work item (`story/`, `task/`, `bug/` or `spike/`, then its key and a short name) and commit there")


def commit_problem(commit):
    """A (decision, reason) for a commit that breaks a rule or cannot be read, or None."""
    problem = branch_problem(commit.folder)
    if problem:
        return "deny", problem
    names = {name for name, _ in commit.options}
    if names & MESSAGE_FROM_A_FILE:
        return "ask", unreadable("it comes from a file")
    messages = [value or "" for name, value in commit.options if name in ("-m", "--message")]
    if any("$(" in message or "`" in message for message in messages):
        return "ask", unreadable("it comes from a substitution or a heredoc")
    if names & REUSES_A_MESSAGE:
        return None
    if not messages:
        return "ask", unreadable("the commit would open an editor")
    problem = messages_problem(messages, git_commands.gemba_field(commit.folder, "Jira Project"))
    return ("deny", problem) if problem else None


def output(decision, why):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": why,
    }}))


def decide(event):
    cwd = event.get("cwd") or os.getcwd()
    command = event.get("tool_input", {}).get("command", "")
    commits = [found for found in git_commands.git_commands(command, cwd) if found.subcommand == "commit"]
    asking = None
    for commit in commits:
        if not git_commands.in_gemba_project(commit.folder, cwd):
            continue
        found = commit_problem(commit)
        if found and found[0] == "deny":
            return output(*found)
        asking = asking or found
    if asking:
        return output(*asking)
    # The parser reads only a `git` at the start of a command. A wrapper (bash -c, sudo, a shell
    # keyword) hides the commit from it, so any command that mentions one asks with a generic reason.
    if not commits and git_commands.mentions(command, "commit") and git_commands.has_gemba(cwd):
        output("ask", unreadable("it is wrapped (bash -c, sudo, a shell keyword or a quoted script)"))


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") != "Bash":
        return
    command = event.get("tool_input", {}).get("command", "")
    if git_commands is None:
        if re.search(r"\bgit\b.*\bcommit\b", command, re.DOTALL):
            output("ask", "Gemba rule (commits): the hook could not load its parser. Confirm the commit message follows the commit rules.")
        return
    try:
        decide(event)
    except Exception:
        # A crash exits non-zero and does not block, so the commit would run unchecked: fail closed.
        if git_commands.mentions(command, "commit"):
            output("ask", "Gemba rule (commits): the hook could not check this commit. Confirm the commit message follows the commit rules.")


if __name__ == "__main__":
    main()
