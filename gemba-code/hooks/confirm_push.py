#!/usr/bin/env python3
"""PreToolUse hook: every `git push` of a project with setup asks the maintainer first.

Reads the hook event from stdin. When a Bash command contains a `git push` and the
project's CLAUDE.md has a `## Gemba` section, it prints an `ask` decision whose reason
names the branch and the remote. In every other case it prints nothing, so the normal
permission flow is untouched. It never allows, never denies and never pushes.
"""
import json
import os
import re
import sys

git_commands = None  # imported by main() once the command is known to mention a push
MENTIONS_A_PUSH = re.compile(r"\bgit\b.*\bpush\b", re.DOTALL)
BROKEN = "git push: the confirmation hook could not read the branch and the remote. Confirm before anything reaches the remote."

WHOLE_PUSHES = (("--mirror", "every ref (mirror)"), ("--all", "all branches"), ("--tags", "all tags"))


def default_remote(folder, branch):
    for key in (f"branch.{branch}.pushRemote", "remote.pushDefault", f"branch.{branch}.remote"):
        value = git_commands.git(folder, "config", "--get", key)
        if value:
            return value
    return "origin"


def reason(push):
    folder = push.folder
    remote, refspecs = (push.args[0] if push.args else None), push.args[1:]
    flags = [name for name, value in push.options if value is None]
    branch = push.branch
    remote = remote or default_remote(folder, branch)
    whole = next((label for flag, label in WHOLE_PUSHES if flag in flags), None)
    target = ", ".join(refspecs) if refspecs else (whole or branch or "the current branch")
    url = "" if remote.startswith("-") else git_commands.git(folder, "remote", "get-url", "--push", remote)
    where = f"{remote} ({url})" if url else remote
    return f"git push: {target} to remote {where}. Confirm before anything reaches the remote."


WRAPPED = ("git push: this command contains a git push the hook could not read (a wrapper, a shell keyword"
           " or a quoted script). Confirm before anything reaches the remote.")


def decide(event):
    cwd = event.get("cwd") or os.getcwd()
    command = event.get("tool_input", {}).get("command", "")
    for push in (found for found in git_commands.git_commands(command, cwd) if found.subcommand == "push"):
        project = git_commands.project_of(push, cwd)
        if project == "unknown":  # a cd the parser could not follow
            return git_commands.emit("ask", "git push: the hook could not tell which folder this push runs in."
                                            " Confirm before anything reaches the remote.")
        if project == "yes":
            return git_commands.emit("ask", reason(push))
    # The parser reads only a `git` at the start of a command. A wrapper (bash -c, sudo, a shell
    # keyword) hides the push from it, so any such segment that mentions one asks with a generic reason.
    if git_commands.unparsed_mentions(command, "push") and git_commands.has_gemba(cwd):
        git_commands.emit("ask", WRAPPED)


def main():
    global git_commands
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") != "Bash":
        return
    if not MENTIONS_A_PUSH.search(event.get("tool_input", {}).get("command", "")):
        return  # not a push of any kind: skip the import and the parsing
    try:
        import git_commands
    except ImportError:  # a crash here would not block: ask for any command that mentions a push
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "ask",
            "permissionDecisionReason": "git push: the confirmation hook could not load its parser. Confirm before anything reaches the remote."}}))
        return
    git_commands.run_hook(decide, ("push",), BROKEN, event)


if __name__ == "__main__":
    main()
