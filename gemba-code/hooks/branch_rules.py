#!/usr/bin/env python3
"""PreToolUse hook: the branches of a project with setup follow the branch rules.

Reads the hook event from stdin. When a Bash command creates, copies or renames a branch (`git switch -c`,
`git checkout -b`, `git branch <name>`, `git branch -c|-m`, `git worktree add -b`, `--orphan`) and the
project's CLAUDE.md has a `## Gemba` section, it denies a name that is not `<type>/<KEY>-<slug>` with type
story, task, bug or spike, a new branch whose base is not the local `develop` (the start point, or the branch
checked out when the command runs, as the shared parser tracks it; an orphan branch has none), and the
rename of `develop` or `main` away. A folder or a branch the parser cannot follow, and a creation hidden in
a wrapper, ask. In every other case it prints nothing, so the normal permission flow is untouched. It never
allows.
"""
import json
import os
import re
import sys
from collections import namedtuple

git_commands = None  # imported by main() once the command is known to create a branch

NAME = re.compile(r"(story|task|bug|spike)/[A-Z][A-Z0-9]*-\d+-[a-z0-9]+(-[a-z0-9]+)*")
PROTECTED = ("main", "develop")
DEVELOP = ("develop", "refs/heads/develop")
CURRENT = ("HEAD", "@")
BRANCH_MODES = {"-d", "-D", "--delete", "-l", "--list", "-a", "--all", "-r", "--remotes", "-v", "-vv", "--verbose",
                "--contains", "--no-contains", "--merged", "--no-merged", "--show-current", "-u",
                "--set-upstream-to", "--unset-upstream", "--edit-description", "--points-at", "--sort", "--format"}
# The cheap test that skips every command with no git word that can make a branch, before the import; the parsed
# `creations()` decide what is one.
MENTIONS = re.compile(r"\bgit\b.*(?<![\w-])(?:branch|switch|checkout|worktree)(?![\w-])", re.DOTALL)
# A clear creation form, for a command the parser cannot read (a wrapper, a quoted script) and for the fallbacks
# when the parser does not load or crashes. `git branch` takes any leading options, except those of a mode
# that lists, deletes or edits.
_BRANCH_MODE = (r"-[dDlarvu]\S*|--(?:delete|list|all|remotes|verbose|show-current|contains|no-contains|merged"
                r"|no-merged|set-upstream-to|unset-upstream|edit-description|points-at|sort|format)(?![\w-])")
CREATING = re.compile(
    r"\bgit\b.*(?<![\w-])(?:"
    r"(?:switch|checkout)\s(?:.*\s)?-(?:[a-zA-Z]*[cCbB]|-create|-force-create|-orphan)(?![\w-])"
    r"|worktree\s+add\s(?:.*\s)?-[bB](?![\w-])"
    rf"|branch\s+(?:(?!{_BRANCH_MODE})-\S*\s+)*[^-\s]"
    r"|branch\s(?:.*\s)?(?:-[a-zA-Z]*[mMcC]|--move|--copy)(?![\w-])"
    r")", re.DOTALL)
PREFIX = "Gemba rule (branches): "
SUGGESTED = {"worktree": "git worktree add -b {name} <path> develop", "checkout": "git checkout -b {name} develop",
             "branch": "git branch {name} develop", "switch": "git switch -c {name} develop"}
BROKEN = PREFIX + "the branch hook could not read this command. Confirm that the branch is named <type>/<KEY>-<slug> and starts from develop."

# kind: "create" (a start point, or None for the current branch), "copy" (start = the old branch), "orphan"
# (no history) or "rename" (start = the old branch, None for the current one).
Creation = namedtuple("Creation", "name start kind")


def updates(command, cwd, name, forced):
    """True when the command only forces an existing branch to a new commit (`branch -f`, `checkout -B`,
    `switch -C`, `worktree add -B`): that is not a creation, and the history hook governs forced updates."""
    folder = command.folder or cwd
    return bool(forced and name and folder and git_commands.is_branch(folder, name))


def dwim_worktree(command, cwd, flags):
    """`git worktree add <path>` with no -b, no commit-ish and no --detach creates a branch named after the last
    component of the path from the current branch, unless that name is already a branch (git checks it out)."""
    if len(command.args) != 2 or flags & {"-d", "--detach"}:
        return []
    name = os.path.basename(command.args[1].rstrip("/"))
    folder = command.folder or cwd
    if not name or (folder and git_commands.is_branch(folder, name)):
        return []
    return [Creation(name, None, "create")]


def creations(command, cwd=None):
    """The Creation of every branch the git command creates, copies or renames."""
    flags = git_commands.option_names(command)
    options = dict(command.options)
    if command.subcommand in ("switch", "checkout"):
        orphan = options.get("--orphan")
        if orphan:
            return [Creation(orphan, None, "orphan")]
        names = ("-c", "-C", "--create", "--force-create") if command.subcommand == "switch" else ("-b", "-B")
        name = next((value for option, value in command.options if option in names and value), None)
        if updates(command, cwd, name, flags & {"-C", "--force-create", "-B"}):
            return []
        return [Creation(name, command.args[0] if command.args else None, "create")] if name else []
    if command.subcommand == "worktree":
        if command.args[:1] != ["add"]:
            return []
        name = next((value for option, value in command.options if option in ("-b", "-B") and value), None)
        if not name:
            return dwim_worktree(command, cwd, flags)
        if updates(command, cwd, name, "-B" in flags):
            return []
        return [Creation(name, command.args[2] if len(command.args) > 2 else None, "create")]
    if command.subcommand == "branch" and command.args:
        old = command.args[0] if len(command.args) > 1 else None
        if flags & {"-m", "-M", "--move"}:
            return [Creation(command.args[-1], old, "rename")]
        if flags & {"-c", "-C", "--copy"}:
            return [Creation(command.args[-1], old, "copy")]
        if not flags & BRANCH_MODES:
            if updates(command, cwd, command.args[0], flags & {"-f", "--force"}):
                return []
            return [Creation(command.args[0], command.args[1] if len(command.args) > 1 else None, "create")]
    return []


def wrong(name):
    return (f"{PREFIX}the branch name '{name}' is not <type>/<KEY>-<slug> with type story, task, bug or spike. "
            f"Name it story/ABC-12-short-slug from develop.")


def off_develop(creation, tracked):
    """What is wrong with the base of the new branch (None when it is the local develop), or "ask" when the
    tracked branch cannot be told and the base needs it."""
    start = creation.start
    if creation.kind == "orphan":
        return "an orphan branch has no history from develop, it starts from nothing"
    if start in DEVELOP:
        return None
    if start is None or start in CURRENT:
        if tracked is None:
            return "ask"
        if tracked == "develop":
            return None
        return f"the branch starts from '{tracked or 'a detached HEAD'}', not from develop"
    if start == "origin/develop":
        return "the branch starts from 'origin/develop', and the rule is the local develop, not the remote one"
    return f"the branch starts from '{start}', not from develop"


def how_to_start(creation, command, name):
    form = "switch" if creation.kind == "orphan" else command.subcommand
    return SUGGESTED[form].format(name=name)


def hint_unknown():
    return (PREFIX + "the folder or the branch this command runs on could not be told. Run it from a plain folder, "
            "with one `cd` to a path or `-C`, so the hook can check the branch name and that it starts from develop.")


def project_key(command, cwd):
    """The `Jira Project` of the project's Gemba section (the folder of the command first, then the session's),
    or None when it has no such field."""
    for folder in (command.folder, cwd):
        key = folder and git_commands.gemba_field(folder, "Jira Project")
        if key:
            return key
    return None


def check(command, creation, cwd=None):
    """A (decision, reason) for one creation, or None when it follows the rules."""
    if not NAME.fullmatch(creation.name):
        return "deny", wrong(creation.name)
    key = project_key(command, cwd)
    if key and not re.fullmatch(rf"[a-z]+/{re.escape(key)}-.*", creation.name):
        return "deny", (f"{PREFIX}the key in the branch name '{creation.name}' is not the Jira Project key '{key}' of "
                        f"this project. Name it story/{key}-12-short-slug from develop.")
    if creation.kind == "rename":
        old = creation.start if creation.start is not None else command.branch
        if old is None:
            return "ask", hint_unknown()
        if old in PROTECTED:
            return "deny", f"{PREFIX}this renames '{old}' away, and develop and main keep their names. Rename a work branch instead."
        return None
    tracked = command.branch
    if creation.kind == "copy" and creation.start is not None:
        creation = creation._replace(kind="create")  # the old branch is the start point
    problem = off_develop(creation, tracked)
    if problem == "ask":
        return "ask", hint_unknown()
    if problem:
        return "deny", f"{PREFIX}{problem}. Create it from develop: {how_to_start(creation, command, creation.name)}."
    return None


def decide(event):
    cwd = event.get("cwd") or os.getcwd()
    command = event.get("tool_input", {}).get("command", "")
    asking = None
    for git_command in git_commands.git_commands(command, cwd):
        for creation in creations(git_command, cwd):
            project = git_commands.project_of(git_command, cwd)
            if project == "no":
                continue
            found = ("ask", hint_unknown()) if project == "unknown" else check(git_command, creation, cwd)
            if found and found[0] == "deny":
                return git_commands.emit(*found)
            asking = asking or found
    if asking:
        return git_commands.emit(*asking)
    # The parser reads only a `git` at the start of a command. A wrapper (bash -c, sudo, a shell
    # keyword) hides the creation from it, so any such segment that looks like one asks with a generic reason.
    if git_commands.unparsed_mentions(command, CREATING) and git_commands.has_gemba(cwd):
        git_commands.emit("ask", PREFIX + "this command creates, copies or renames a branch in a way the hook could not read "
                          "(a wrapper, a shell keyword or a quoted script). Confirm that the branch is named "
                          "<type>/<KEY>-<slug> and starts from develop.")


def main():
    global git_commands
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") != "Bash":
        return
    command = event.get("tool_input", {}).get("command", "")
    if not MENTIONS.search(command):
        return  # nothing mentions a command that makes a branch: skip the import and the parsing
    try:
        import git_commands
    except ImportError:  # a crash here would not block: ask for a clear creation
        if CREATING.search(command):
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse", "permissionDecision": "ask",
                "permissionDecisionReason": PREFIX + "the branch hook could not load its parser. Confirm that the branch "
                                                     "is named <type>/<KEY>-<slug> and starts from develop."}}))
        return

    try:
        decide(event)
    except Exception:  # a crash exits non-zero, which does not block: ask for a clear creation, one layer only
        if CREATING.search(command):
            git_commands.emit("ask", BROKEN)


if __name__ == "__main__":
    main()
