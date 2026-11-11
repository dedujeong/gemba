#!/usr/bin/env python3
"""PreToolUse hook: a project with setup only pushes what its `Integration` mode allows.

Reads the hook event from stdin. In a project whose CLAUDE.md has a `## Gemba` section it denies the
`git push` that breaks the `Integration` mode, and asks (generic reason) for a push it cannot read.
It prints nothing for a push the mode allows, so `confirm_push.py` still asks. It never allows and
never runs anything but `git` to read the repository.
"""
import json
import os
import re
import sys

try:
    import git_commands
except ImportError:  # a crash here would not block, so main() asks for any command that mentions a push
    git_commands = None

MODES = ("merge", "pull request")
MAIN_BRANCHES = ("develop", "main")


def deny(why):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": why,
    }}))


def ask(why):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": why,
    }}))


def integration_mode(folder):
    """The value of `Integration` as written, or None when the line is missing."""
    return git_commands.gemba_field(folder, "Integration")


def is_a_tag(folder, name):
    return bool(git_commands.git(folder, "rev-parse", "--verify", "--quiet", f"refs/tags/{name}"))


def pushed_branches(push):
    """The branches a `git push` writes. Tag pushes and deletions write none. `--all` and `--mirror` are
    reported as `all branches`."""
    flags = {name for name, value in push.options if value is None}
    if flags & {"--delete", "-d"}:
        return []
    if flags & {"--all", "--mirror"}:
        return ["all branches"]
    refspecs = push.args[1:]
    if not refspecs:
        if "--tags" in flags:
            return []
        branch = git_commands.current_branch(push.folder)
        return [branch] if branch else []
    branches = []
    skip_next = False
    for refspec in refspecs:
        if skip_next:  # `git push origin tag v1`
            skip_next = False
            continue
        if refspec == "tag":
            skip_next = True
            continue
        refspec = refspec.lstrip("+")
        source, colon, destination = refspec.partition(":")
        if colon:
            if not source or not destination:  # `:branch` deletes it
                continue
            name = destination
        else:
            name = source
        if name.startswith("refs/tags/"):
            continue
        if name == "HEAD":
            name = git_commands.current_branch(push.folder)
        elif not colon and is_a_tag(push.folder, name):
            continue
        name = name.removeprefix("refs/heads/")
        if name:
            branches.append(name)
    return branches


def push_problem(push, mode):
    """Why the push breaks the mode, or None when the mode allows it."""
    branches = pushed_branches(push)
    if not branches:
        return None
    if mode not in MODES:
        if mode is None:
            return ("Gemba rule (integration: missing): the Integration line is missing in the Gemba section of CLAUDE.md,"
                    " so no branch can be pushed. Run setup to set it to merge or pull request.")
        return (f"Gemba rule (integration: invalid): the Integration value `{mode}` is missing or invalid in the Gemba section"
                " of CLAUDE.md (only merge or pull request), so no branch can be pushed. Run setup to set it.")
    if mode == "merge":
        work = [branch for branch in branches if branch not in MAIN_BRANCHES]
        if work:
            return (f"Gemba rule (integration: merge): work branches are not pushed, only develop and main ({', '.join(work)})."
                    " Merge the branch locally into develop and push develop.")
    return None


def decide(event):
    cwd = event.get("cwd") or os.getcwd()
    command = event.get("tool_input", {}).get("command", "")
    found = False
    for push in (c for c in git_commands.git_commands(command, cwd) if c.subcommand == "push"):
        found = True
        if not git_commands.in_gemba_project(push.folder, cwd):
            continue
        mode = (integration_mode(push.folder) or "").strip().lower() or None
        problem = push_problem(push, mode)
        if problem:
            deny(problem)
            return
    if found:
        return
    # The parser reads only a `git` at the start of a command. A wrapper (bash -c, sudo, a shell
    # keyword) hides the push from it, so any command that mentions one asks with a generic reason.
    if git_commands.mentions(command, "push") and git_commands.has_gemba(cwd):
        ask(UNREADABLE)


UNREADABLE = ("Gemba rule (integration): this command contains a git push the hook could not read (a wrapper, a shell"
              " keyword or a quoted script), so it cannot check the integration mode. Confirm it.")


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") != "Bash":
        return
    command = event.get("tool_input", {}).get("command", "")
    if git_commands is None:
        if re.search(r"\bgit\b.*\bpush\b", command, re.DOTALL):
            ask(UNREADABLE)
        return
    try:
        decide(event)
    except Exception:
        # A crash exits non-zero and does not block, so the push would run unchecked: fail closed.
        if git_commands.mentions(command, "push"):
            ask(UNREADABLE)


if __name__ == "__main__":
    main()
