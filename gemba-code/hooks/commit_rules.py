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

git_commands = None  # imported by main() once the command is known to mention a commit

TYPES = ("build", "chore", "ci", "docs", "feat", "fix", "perf", "refactor", "revert", "style", "test")
HEADER = re.compile(r"(\w+)(?:\(([^)]*)\))?!?: \S.*", re.DOTALL)
MERGE = re.compile(r"Merge (?:branch|remote-tracking branch|tag|commit) '[^'\n]+'(?: of \S+)?(?: into \S*[^\s.])?"
                   r"|Merge pull request #\d+ from \S+")
REVERT = re.compile(r'Revert ".+"(\n\nThis reverts commit [0-9a-f]{7,40}\.)?')
FORMAT = "`<type>(<scope>): <description>`"
EXAMPLE = "for example `feat(hooks): block commit messages that break the commit format`"

PROTECTED_BRANCHES = ("main", "develop")
CREATES_COMMITS = ("commit", "revert", "cherry-pick", "am")
ENDS_WITHOUT_A_COMMIT = {"--abort", "--quit"}
EDITOR_FIXUPS = ("amend:", "reword:")
# Any git command that creates a commit, as whole words: the cheap test that skips every other command.
CREATING_WORDS = re.compile(r"\bgit\b.*(?<![\w-])(?:%s|merge\b.*--continue)(?![\w-])" % "|".join(map(re.escape, CREATES_COMMITS)), re.DOTALL)
BROKEN = "Gemba rule (commits): the hook could not check this commit. Confirm the commit message follows the commit rules."
REUSES_A_MESSAGE = {"--fixup", "--squash", "--no-edit", "-C", "--reuse-message"}
HAS_ITS_OWN_MESSAGE = {"-m", "--message", "-F", "--file", "-C", "--reuse-message", "--fixup", "--squash"}
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
    if message == "Initial commit" or MERGE.fullmatch(message) or re.fullmatch(r"(?:fixup|squash)! [^\n]+", message):
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
    if project and re.search(rf"\b(?i:{re.escape(project)})-\d+\b", message):
        return rule("the message has a Jira key", "Remove it: the branch and the work item link the commit, not the message")
    if scope == "":
        return rule("the scope is empty", "Name the scope, one of the project's Jira components, or remove the parentheses")
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


def branch_problem(commit, merging=None):
    """A (decision, reason) when the commit cannot land on the branch it runs on, or None. A folder or a
    branch the parser could not follow (a `cd` it cannot read, `switch -`) asks."""
    if commit.folder is None or commit.branch is None:
        return "ask", rule("the folder or the branch this command runs on could not be told",
                           "Run it from a plain folder, with one `cd` to a path or `-C`, so the hook can check that it is not main or develop")
    if commit.branch not in PROTECTED_BRANCHES:
        return None
    if merging is None:
        merging = bool(git_commands.git(commit.folder, "rev-parse", "-q", "--verify", "MERGE_HEAD"))
    if merging:
        return None  # concluding a merge
    return "deny", rule(f"the current branch is `{commit.branch}`, and nothing is committed on main or develop",
                        "Create a branch for the work item (`story/`, `task/`, `bug/` or `spike/`, then its key and a short name) and commit there")


def conclusion_problem(commit, merging):
    """A deny reason when a merge in progress is concluded with the message git prepared (`git commit` without
    a message, `--no-edit`, `merge --continue`): without the strip cleanup its `# Conflicts:` lines stay in it."""
    names = git_commands.option_names(commit)
    if not merging or ("--cleanup", "strip") in commit.options or names & HAS_ITS_OWN_MESSAGE:
        return None
    if commit.subcommand == "merge" and "--continue" not in names:
        return None
    return rule("concluding a merge this way keeps the `# Conflicts:` lines in the commit message",
                "Conclude it with `git commit --no-edit --cleanup=strip`")


def message_decision(commit, project):
    """A (decision, reason) for the message of a `git commit` that breaks a rule or cannot be read, or None."""
    names = git_commands.option_names(commit)
    if names & MESSAGE_FROM_A_FILE:
        return "ask", unreadable("it comes from a file")
    if any((value or "").startswith(EDITOR_FIXUPS) for name, value in commit.options if name == "--fixup"):
        return "ask", unreadable("a fixup with amend: or reword: opens an editor")
    messages = [value or "" for name, value in commit.options if name in ("-m", "--message")]
    if any("$" in message or "`" in message for message in messages):
        return "ask", unreadable("it has a variable, a substitution or a heredoc")
    if not messages:
        if names & REUSES_A_MESSAGE:
            return None
        return "ask", unreadable("the commit would open an editor")
    problem = messages_problem(messages, project)
    return ("deny", problem) if problem else None


def creates_no_commit(commit):
    names = git_commands.option_names(commit)
    if commit.subcommand == "commit":
        return False
    return bool(ENDS_WITHOUT_A_COMMIT & names) or (commit.subcommand != "am" and bool({"-n", "--no-commit"} & names))


def commit_problem(commit, folder, merging=None):
    """A (decision, reason) for a commit, revert, cherry-pick or am that breaks a rule or cannot be read, or
    None. A denial wins over a question."""
    if creates_no_commit(commit):
        return None
    if merging is None and commit.folder:
        merging = bool(git_commands.git(commit.folder, "rev-parse", "-q", "--verify", "MERGE_HEAD"))
    found = [branch_problem(commit, merging)]
    problem = conclusion_problem(commit, merging)
    if problem:
        found.append(("deny", problem))
    if commit.subcommand == "commit":
        found.append(message_decision(commit, git_commands.gemba_field(folder, "Jira Project")))
    found = [item for item in found if item]
    return next((item for item in found if item[0] == "deny"), found[0] if found else None)


def decide(event):
    cwd = event.get("cwd") or os.getcwd()
    command = event.get("tool_input", {}).get("command", "")
    asking = None
    merging = {}  # repository -> True after a `git merge` earlier in this command, False after merge --abort/--quit
    for commit in git_commands.git_commands(command, cwd):
        key = git_commands.repository_key(commit.folder) if commit.folder else None
        names = git_commands.option_names(commit)
        if commit.subcommand == "merge" and key and "--continue" not in names:
            merging[key] = not (ENDS_WITHOUT_A_COMMIT & names)
        if commit.subcommand not in CREATES_COMMITS and not (commit.subcommand == "merge" and "--continue" in names):
            continue
        if git_commands.project_of(commit, cwd) == "no":
            continue
        folder = commit.folder or cwd  # an unknown folder: the session's project holds the settings
        found = commit_problem(commit, folder, merging.get(key))
        if found and found[0] == "deny":
            return git_commands.emit(*found)
        asking = asking or found
    if asking:
        return git_commands.emit(*asking)
    # The parser reads only a `git` at the start of a command. A wrapper (bash -c, sudo, a shell
    # keyword) hides the commit from it, so any such segment that mentions one asks with a generic reason.
    if git_commands.unparsed_mentions(command, CREATES_COMMITS) and git_commands.has_gemba(cwd):
        git_commands.emit("ask", unreadable("it is wrapped (bash -c, sudo, a shell keyword or a quoted script)"))


def main():
    global git_commands
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") != "Bash":
        return
    if not CREATING_WORDS.search(event.get("tool_input", {}).get("command", "")):
        return  # no commit, revert, cherry-pick or am anywhere: skip the import and the parsing
    try:
        import git_commands
    except ImportError:  # a crash here would not block: ask for any command that mentions a commit
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "ask",
            "permissionDecisionReason": "Gemba rule (commits): the hook could not load its parser. Confirm the commit message follows the commit rules."}}))
        return
    git_commands.run_hook(decide, CREATING_WORDS, BROKEN, event)


if __name__ == "__main__":
    main()
