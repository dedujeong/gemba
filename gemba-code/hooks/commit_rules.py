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
CREATES_COMMITS = ("commit", "revert", "cherry-pick", "am")
ENDS_THE_OPERATION = {"--abort", "--continue", "--skip", "--quit"}
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


def branch_problem(commit):
    """A (decision, reason) when the commit cannot land on the branch it runs on, or None. A folder or a
    branch the parser could not follow (a `cd` it cannot read, `switch -`) asks."""
    if commit.folder is None or commit.branch is None:
        return "ask", rule("the folder or the branch this command runs on could not be told",
                           "Run it from a plain folder, with one `cd` to a path or `-C`, so the hook can check that it is not main or develop")
    if commit.branch not in PROTECTED_BRANCHES:
        return None
    if git_commands.git(commit.folder, "rev-parse", "-q", "--verify", "MERGE_HEAD"):
        return None  # concluding a merge
    return "deny", rule(f"the current branch is `{commit.branch}`, and nothing is committed on main or develop",
                        "Create a branch for the work item (`story/`, `task/`, `bug/` or `spike/`, then its key and a short name) and commit there")


def message_decision(commit, project):
    """A (decision, reason) for the message of a `git commit` that breaks a rule or cannot be read, or None."""
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
    problem = messages_problem(messages, project)
    return ("deny", problem) if problem else None


def creates_no_commit(commit):
    names = {name for name, _ in commit.options}
    if commit.subcommand == "commit":
        return False
    return bool(ENDS_THE_OPERATION & names) or (commit.subcommand != "am" and bool({"-n", "--no-commit"} & names))


def commit_problem(commit, folder):
    """A (decision, reason) for a commit, revert, cherry-pick or am that breaks a rule or cannot be read, or
    None. A denial wins over a question."""
    if creates_no_commit(commit):
        return None
    found = [branch_problem(commit)]
    if commit.subcommand == "commit":
        found.append(message_decision(commit, git_commands.gemba_field(folder, "Jira Project")))
    found = [item for item in found if item]
    return next((item for item in found if item[0] == "deny"), found[0] if found else None)


def decide(event):
    cwd = event.get("cwd") or os.getcwd()
    command = event.get("tool_input", {}).get("command", "")
    asking = None
    commits = [found for found in git_commands.git_commands(command, cwd) if found.subcommand == "commit"]
    for commit in git_commands.git_commands(command, cwd):
        if commit.subcommand not in CREATES_COMMITS:
            continue
        folder = commit.folder or cwd  # an unknown folder: the session's project decides whether the rules apply
        if not git_commands.in_gemba_project(folder, cwd):
            continue
        found = commit_problem(commit, folder)
        if found and found[0] == "deny":
            return git_commands.emit(*found)
        asking = asking or found
    if asking:
        return git_commands.emit(*asking)
    # The parser reads only a `git` at the start of a command. A wrapper (bash -c, sudo, a shell
    # keyword) hides the commit from it, so any such segment that mentions one asks with a generic reason.
    if not commits and git_commands.mentions(command, "commit") and git_commands.has_gemba(cwd):
        git_commands.emit("ask", unreadable("it is wrapped (bash -c, sudo, a shell keyword or a quoted script)"))


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
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse", "permissionDecision": "ask",
                "permissionDecisionReason": "Gemba rule (commits): the hook could not load its parser. Confirm the commit message follows the commit rules."}}))
        return
    try:
        decide(event)
    except Exception:
        # A crash exits non-zero and does not block, so the commit would run unchecked: fail closed.
        if git_commands.mentions(command, "commit"):
            git_commands.emit("ask", "Gemba rule (commits): the hook could not check this commit. Confirm the commit message follows the commit rules.")


if __name__ == "__main__":
    main()
