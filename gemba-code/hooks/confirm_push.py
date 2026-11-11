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

try:
    import git_commands
except ImportError:  # a crash here would not block, so main() asks for any command that mentions a push
    git_commands = None

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
    branch = git_commands.current_branch(folder)
    remote = remote or default_remote(folder, branch)
    whole = next((label for flag, label in WHOLE_PUSHES if flag in flags), None)
    target = ", ".join(refspecs) if refspecs else (whole or branch or "the current branch")
    url = git_commands.git(folder, "remote", "get-url", "--push", remote)
    where = f"{remote} ({url})" if url else remote
    return f"git push: {target} to remote {where}. Confirm before anything reaches the remote."


def ask(why):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": why,
    }}))


def decide(event):
    cwd = event.get("cwd") or os.getcwd()
    command = event.get("tool_input", {}).get("command", "")
    push = next((found for found in git_commands.git_commands(command, cwd) if found.subcommand == "push"), None)
    if push is not None:
        if git_commands.in_gemba_project(push.folder, cwd):
            ask(reason(push))
        return
    # The parser reads only a `git` at the start of a command. A wrapper (bash -c, sudo, a shell
    # keyword) hides the push from it, so any command that mentions one asks with a generic reason.
    if git_commands.mentions(command, "push") and git_commands.has_gemba(cwd):
        ask("git push: this command contains a git push the hook could not read (a wrapper, a shell keyword"
            " or a quoted script). Confirm before anything reaches the remote.")


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") != "Bash":
        return
    if git_commands is None:
        if re.search(r"\bgit\b.*\bpush\b", event.get("tool_input", {}).get("command", ""), re.DOTALL):
            ask("git push: the confirmation hook could not load its parser. Confirm before anything reaches the remote.")
        return
    try:
        decide(event)
    except Exception:
        # A crash exits non-zero and does not block, so the push would run unasked: fail closed.
        if git_commands.mentions(event.get("tool_input", {}).get("command", ""), "push"):
            ask("git push: the confirmation hook could not read the branch and the remote. Confirm before anything reaches the remote.")


if __name__ == "__main__":
    main()
