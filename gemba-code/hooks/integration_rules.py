#!/usr/bin/env python3
"""PreToolUse hook: a project with setup only pushes and merges what its `Integration` mode allows.

Reads the hook event from stdin. In a project whose CLAUDE.md has a `## Gemba` section it denies the
`git push`, the local `git merge` into develop or main and the `gh pr merge` that break the `Integration`
mode, and asks (generic reason) for a push or merge it cannot read. It prints nothing for what the mode
allows, so `confirm_push.py` still asks about every push. It never allows and never changes anything:
it only runs `git` to read the repository.
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


def mode_of(folder):
    return (integration_mode(folder) or "").strip().lower() or None


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
    else:
        main = [branch for branch in branches if branch in MAIN_BRANCHES]
        if main:
            return (f"Gemba rule (integration: pull request): develop and main are not pushed ({', '.join(main)})."
                    " Push the work branch and open a pull request; the maintainer merges it.")
    return None


def merge_problem(merge, mode):
    """Why a local `git merge` breaks the mode, or None."""
    if mode != "pull request" or {name for name, _ in merge.options} & {"--abort", "--continue", "--quit"}:
        return None
    branch = git_commands.current_branch(merge.folder)
    if branch in MAIN_BRANCHES:
        return (f"Gemba rule (integration: pull request): nothing is merged locally into {branch}."
                " Open a pull request from the work branch; the maintainer merges it.")
    return None


def gh_words(words):
    """The words of a `gh` command after its global options, or None when the segment is not `gh`."""
    i = 0
    while i < len(words) and re.fullmatch(r"\w+=.*", words[i]):
        i += 1
    if i >= len(words) or os.path.basename(words[i]) != "gh":
        return None
    rest = words[i + 1:]
    j = 0
    while j < len(rest) and rest[j].startswith("-"):
        j += 2 if rest[j] in ("-R", "--repo") else 1
    return rest[j:]


def is_pr_merge(words):
    rest = gh_words(words)
    return rest is not None and rest[:2] == ["pr", "merge"]


def pr_merge_problem(mode):
    if mode == "pull request":
        return ("Gemba rule (integration: pull request): gh pr merge is not run by Claude."
                " The maintainer merges the pull request.")
    return None


def decide(event):
    cwd = event.get("cwd") or os.getcwd()
    command = event.get("tool_input", {}).get("command", "")
    pushed = merged = False
    for found in git_commands.git_commands(command, cwd):
        if found.subcommand not in ("push", "merge"):
            continue
        pushed = pushed or found.subcommand == "push"
        merged = merged or found.subcommand == "merge"
        if not git_commands.in_gemba_project(found.folder, cwd):
            continue
        mode = mode_of(found.folder)
        check = push_problem if found.subcommand == "push" else merge_problem
        problem = check(found, mode)
        if problem:
            deny(problem)
            return
    pr_merged = False
    if git_commands.has_gemba(cwd):
        for words in git_commands.segments(command):
            if is_pr_merge(words):
                pr_merged = True
                problem = pr_merge_problem(mode_of(cwd))
                if problem:
                    deny(problem)
                    return
    # The parser reads only a `git` or `gh` at the start of a command. A wrapper (bash -c, sudo, a shell
    # keyword) hides it, so a command that mentions one asks with a generic reason. A local merge or a
    # pull request merge is only a rule in pull request mode, so only there is a hidden one asked about.
    if not git_commands.has_gemba(cwd):
        return
    hidden_push = not pushed and git_commands.mentions(command, "push")
    hidden_merge = (not merged and git_commands.mentions(command, "merge")) or (
        not pr_merged and re.search(r"\bgh\b.*\bpr\b.*\bmerge\b", command, re.DOTALL))
    if hidden_push or (hidden_merge and mode_of(cwd) != "merge"):
        ask(UNREADABLE)


UNREADABLE = ("Gemba rule (integration): this command contains a git push or a merge the hook could not read (a wrapper,"
              " a shell keyword or a quoted script), so it cannot check the integration mode. Confirm it.")


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") != "Bash":
        return
    command = event.get("tool_input", {}).get("command", "")
    if git_commands is None:
        if re.search(r"\bgit\b.*\b(push|merge)\b|\bgh\b.*\bpr\b.*\bmerge\b", command, re.DOTALL):
            ask(UNREADABLE)
        return
    try:
        decide(event)
    except Exception:
        # A crash exits non-zero and does not block, so the push would run unchecked: fail closed.
        if git_commands.mentions(command, "push") or git_commands.mentions(command, "merge") or re.search(
                r"\bgh\b.*\bpr\b.*\bmerge\b", command, re.DOTALL):
            ask(UNREADABLE)


if __name__ == "__main__":
    main()
