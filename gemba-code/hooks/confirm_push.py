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
import shlex
import subprocess
import sys

OPTIONS_WITH_A_VALUE = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}
SEPARATORS = "();<>|&\n"
MENTIONS_A_PUSH = re.compile(r"\bgit\b.*\bpush\b", re.DOTALL)
WHOLE_PUSHES = (("--mirror", "every ref (mirror)"), ("--all", "all branches"), ("--tags", "all tags"))
GLOBAL_OPTIONS_WITH_A_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}


def segments(command):
    """The commands joined by &&, ||, ;, |, & or a new line as lists of words."""
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=SEPARATORS)
        lexer.whitespace_split = True
        lexer.whitespace = " \t\r"  # a new line separates commands
        lexer.commenters = ""  # bash starts a comment only at the start of a word, shlex also inside one
        words = list(lexer)
    except ValueError:
        words = command.split()
    current = []
    for word in words:
        if set(word) <= set(SEPARATORS):
            if current:
                yield current
            current = []
        else:
            current.append(word)
    if current:
        yield current


def parse_push(words):
    """(folder, remote, refspecs, flags) when the words are a git push, otherwise None."""
    i = 0
    while i < len(words) and re.fullmatch(r"\w+=.*", words[i]):
        i += 1
    if i >= len(words) or os.path.basename(words[i]) != "git":
        return None
    i += 1
    folder = None
    while i < len(words) and words[i].startswith("-"):
        option = words[i]
        if option in GLOBAL_OPTIONS_WITH_A_VALUE:
            if option == "-C" and i + 1 < len(words):
                folder = words[i + 1]
            i += 2
        else:
            i += 1
    if i >= len(words) or words[i] != "push":
        return None
    positionals, flags = [], []
    i += 1
    while i < len(words) and not words[i].startswith("#"):
        if words[i] in OPTIONS_WITH_A_VALUE:
            i += 2
        elif words[i].startswith("-"):
            flags.append(words[i])
            i += 1
        else:
            positionals.append(words[i])
            i += 1
    return folder, (positionals[0] if positionals else None), positionals[1:], flags


def git(folder, *args):
    result = subprocess.run(["git", "-C", folder, *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def has_gemba(folder):
    top = git(folder, "rev-parse", "--show-toplevel") or folder
    try:
        with open(os.path.join(top, "CLAUDE.md"), encoding="utf-8") as f:
            return re.search(r"^## Gemba\s*$", f.read(), re.MULTILINE) is not None
    except OSError:
        return False


def default_remote(folder, branch):
    for key in (f"branch.{branch}.pushRemote", "remote.pushDefault", f"branch.{branch}.remote"):
        value = git(folder, "config", "--get", key)
        if value:
            return value
    return "origin"


def reason(folder, remote, refspecs, flags):
    branch = git(folder, "branch", "--show-current")
    remote = remote or default_remote(folder, branch)
    whole = next((label for flag, label in WHOLE_PUSHES if flag in flags), None)
    target = ", ".join(refspecs) if refspecs else (whole or branch or "the current branch")
    url = git(folder, "remote", "get-url", "--push", remote)
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
    for words in segments(command):
        push = parse_push(words)
        if push is None:
            continue
        folder = os.path.join(cwd, push[0]) if push[0] else cwd
        if not has_gemba(cwd):
            return
        ask(reason(folder, *push[1:]))
        return
    # The parser reads only a `git` at the start of a command. A wrapper (bash -c, sudo, a shell
    # keyword) hides the push from it, so any command that mentions one asks with a generic reason.
    if MENTIONS_A_PUSH.search(command) and has_gemba(cwd):
        ask("git push: this command contains a git push the hook could not read (a wrapper, a shell keyword"
            " or a quoted script). Confirm before anything reaches the remote.")


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") != "Bash":
        return
    try:
        decide(event)
    except Exception:
        # A crash exits non-zero and does not block, so the push would run unasked: fail closed.
        if MENTIONS_A_PUSH.search(event.get("tool_input", {}).get("command", "")):
            ask("git push: the confirmation hook could not read the branch and the remote. Confirm before anything reaches the remote.")


if __name__ == "__main__":
    main()
