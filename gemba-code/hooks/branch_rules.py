#!/usr/bin/env python3
"""PreToolUse hook: the branches of a project with setup follow the branch rules.

Reads the hook event from stdin. When a Bash command creates or renames a branch (`git switch -c`,
`git checkout -b`, `git branch <name>`, `git worktree add -b`, `git branch -m`) and the project's
CLAUDE.md has a `## Gemba` section, it denies a name that is not `<type>/<KEY>-<slug>` with type story,
task, bug or spike, and a new branch whose base is not `develop` (the start point, or the current branch
when there is none; a rename has no base). A command the parser cannot read asks with a generic reason.
In every other case it prints nothing, so the normal permission flow is untouched. It never allows.
"""
import json
import os
import re
import sys

try:
    import git_commands
except ImportError:  # a crash here would not block, so main() asks for any command that creates a branch
    git_commands = None

NAME = re.compile(r"(story|task|bug|spike)/[A-Z][A-Z0-9]*-\d+-[a-z0-9]+(-[a-z0-9]+)*")
BRANCH_MODES = {"-d", "-D", "--delete", "-m", "-M", "--move", "-c", "-C", "--copy", "-l", "--list", "-a", "--all",
                "-r", "--remotes", "-v", "-vv", "--verbose", "--contains", "--no-contains", "--merged",
                "--no-merged", "--show-current", "-u", "--set-upstream-to", "--unset-upstream",
                "--edit-description", "--points-at", "--sort", "--format"}
CREATING = (r"\bgit\b.*\b(switch\s+(-c|-C|--create|--force-create)|checkout\s+-[bB]"
            r"|worktree\s+add\b.*\s-[bB]\b|branch\s+-[mM]\b)")
CREATING_BRANCH_WORD = r"\bgit\b.*\bbranch\s+[^-\s]"
PREFIX = "Gemba rule (branches): "


def creations(command):
    """The (name, start, renamed) of every branch the git command creates or renames; start is None when it
    has none."""
    flags = {name for name, _ in command.options}
    if command.subcommand in ("switch", "checkout"):
        names = ("-c", "-C", "--create", "--force-create") if command.subcommand == "switch" else ("-b", "-B")
        name = next((value for option, value in command.options if option in names), None)
        return [(name, command.args[0] if command.args else None, False)] if name else []
    if command.subcommand == "worktree":
        if command.args[:1] != ["add"]:
            return []
        name = next((value for option, value in command.options if option in ("-b", "-B")), None)
        start = command.args[2] if len(command.args) > 2 else None
        return [(name, start, False)] if name else []
    if command.subcommand == "branch" and command.args:
        if flags & {"-m", "-M", "--move"}:
            return [(command.args[-1], None, True)]
        if not flags & BRANCH_MODES:
            return [(command.args[0], command.args[1] if len(command.args) > 1 else None, False)]
    return []


def wrong(name):
    return (f"{PREFIX}the branch name '{name}' is not <type>/<KEY>-<slug> with type story, task, bug or spike. "
            f"Name it story/ABC-12-short-slug from develop.")


def off_develop(start, folder):
    """What is wrong with the base of the new branch, or None when it is develop."""
    if start is not None:
        return None if start == "develop" else f"the branch starts from '{start}', not from develop"
    current = git_commands.current_branch(folder)
    if current == "develop":
        return None
    return f"the branch starts from '{current or 'a detached HEAD'}', not from develop"


def emit(decision, why):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": why,
    }}))


def decide(event):
    cwd = event.get("cwd") or os.getcwd()
    command = event.get("tool_input", {}).get("command", "")
    found = git_commands.git_commands(command, cwd)
    seen = False
    for git_command in found:
        for name, start, renamed in creations(git_command):
            seen = True
            if not git_commands.in_gemba_project(git_command.folder, cwd):
                continue
            if not NAME.fullmatch(name):
                emit("deny", wrong(name))
                return
            problem = None if renamed else off_develop(start, git_command.folder)
            if problem:
                emit("deny", f"{PREFIX}{problem}. Create it from develop: git switch -c {name} develop.")
                return
    if seen:
        return
    # The parser reads only a `git` at the start of a command. A wrapper (bash -c, sudo, a shell
    # keyword) hides the creation from it, so a command that looks like one asks with a generic reason.
    looks_like = re.search(CREATING, command, re.DOTALL) or (not found and re.search(CREATING_BRANCH_WORD, command, re.DOTALL))
    if looks_like and git_commands.has_gemba(cwd):
        emit("ask", f"{PREFIX}this command creates or renames a branch in a way the hook could not read "
                    "(a wrapper, a shell keyword or a quoted script). Confirm that the branch is named "
                    "<type>/<KEY>-<slug> and starts from develop.")


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") != "Bash":
        return
    command = event.get("tool_input", {}).get("command", "")
    if git_commands is None:
        if re.search(CREATING, command, re.DOTALL):
            emit("ask", f"{PREFIX}the branch hook could not load its parser. Confirm that the branch is named "
                        "<type>/<KEY>-<slug> and starts from develop.")
        return
    try:
        decide(event)
    except Exception:
        # A crash exits non-zero and does not block, so the branch would be made unchecked: fail closed.
        if re.search(CREATING, command, re.DOTALL) or re.search(CREATING_BRANCH_WORD, command, re.DOTALL):
            emit("ask", f"{PREFIX}the branch hook could not read this command. Confirm that the branch is named "
                        "<type>/<KEY>-<slug> and starts from develop.")


if __name__ == "__main__":
    main()
