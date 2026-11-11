#!/usr/bin/env python3
"""PreToolUse hook: the history rules of the method, for a project with setup.

Reads the hook event from stdin. When a Bash command does an operation that rewrites or loses
history (a merge that is not a `--no-ff` merge with Git's message, a rebase, a force push, the
forced deletion of a branch that is not a Spike's, a tag that is not a version) and the project's
CLAUDE.md has a `## Gemba` section, it prints a `deny` decision whose reason names the rule and
what to do. A command the parser cannot read asks instead, with a generic reason. In every other
case it prints nothing, so the normal permission flow is untouched. It never runs anything but `git`.
"""
import json
import os
import re
import sys

try:
    import git_commands
except ImportError:  # a crash here would not block, so main() asks for any command that looks like one of the operations
    git_commands = None

PROTECTED = ("develop", "main")
MERGE_ENDS = {"--abort", "--continue", "--quit"}
REBASE_ENDS = {"--abort", "--continue", "--skip", "--quit", "--edit-todo", "--show-current-patch"}

# What an operation looks like in the raw text of a command, for what the parser cannot read.
RAW_OPERATIONS = (
    r"\bgit\b.*\bmerge\b",
    r"\bgit\b.*\brebase\b",
    r"\bgit\b.*\bpull\b.*(--rebase|\s-\w*r)",
    r"\bgit\b.*\bpush\b.*(--force|\s-\w*f|\s\+)",
    r"\bgit\b.*\bbranch\b.*(--force|\s-\w*[Df])",
    r"\bgit\b.*\btag\b",
)


def looks_like_an_operation(command):
    return any(re.search(pattern, command, re.DOTALL) for pattern in RAW_OPERATIONS)


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


def rule(name, wrong, todo):
    return f"Gemba rule ({name}): {wrong}. {todo}."


def merge_problem(merge):
    """The reason a merge breaks the rules, or None."""
    names = {name for name, _ in merge.options}
    if names & MERGE_ENDS:
        return None
    target = git_commands.current_branch(merge.folder)
    if target not in PROTECTED:
        return None
    if "--squash" in names:
        return rule("merges", f"a squash merge into {target} loses the history of the branch",
                    "Merge with `git merge --no-ff <branch>` and Git's default message")
    updates_from_remote = all(arg in (f"origin/{target}", "@{u}", "@{upstream}") for arg in merge.args)
    if updates_from_remote:
        return None
    if "--no-ff" not in names:
        return rule("merges", f"a merge into {target} without --no-ff",
                    "Merge with `git merge --no-ff <branch>` so the branch stays in the history")
    if names & {"-m", "--message", "-F", "--file"}:
        return rule("merges", f"a merge into {target} with its own message",
                    "Merge with `git merge --no-ff <branch>` and keep Git's default message")
    return None


def count(folder, *revisions):
    """How many commits the revisions select, or None when git cannot tell."""
    out = git_commands.git(folder, "rev-list", "--count", *revisions)
    return int(out) if out.isdigit() else None


def rebase_problem(rebase):
    """The reason a rebase breaks the rules, or None. The only rebase allowed is `--autosquash`
    over commits the remote does not have."""
    names = {name for name, _ in rebase.options}
    if names & REBASE_ENDS:
        return None
    todo = "Do not rebase: merge instead. The only rebase allowed is `git rebase -i --autosquash <upstream>` over commits that are not pushed"
    if "--autosquash" not in names or "--no-autosquash" in names:
        return rule("rebase", "a rebase rewrites history", todo)
    upstream = rebase.args[0] if rebase.args else "@{u}"
    head = rebase.args[1] if len(rebase.args) > 1 else "HEAD"
    mine = count(rebase.folder, f"{upstream}..{head}")
    not_pushed = count(rebase.folder, f"{upstream}..{head}", "--not", "--remotes")
    if mine is None or not_pushed is None:
        return rule("rebase", f"the commits to rebase on {upstream} could not be read", todo)
    if mine != not_pushed:
        return rule("rebase", "the rebase rewrites commits the remote already has", todo)
    return None


def pull_problem(pull):
    """The reason a pull breaks the rules, or None: `git pull --rebase` is a rebase."""
    for name, value in pull.options:
        if name in ("--rebase", "-r") and value != "false":
            return rule("rebase", "git pull --rebase rewrites history",
                        "Pull without rebasing: `git pull` or `git merge --ff-only origin/<branch>`")
    return None


FORCE_OPTIONS = {"--force", "-f", "--force-with-lease", "--force-if-includes"}


def push_problem(push):
    """The reason a push breaks the rules, or None: no force push, whatever its form."""
    forced = any(name in FORCE_OPTIONS for name, _ in push.options) or any(arg.startswith("+") for arg in push.args)
    if forced:
        return rule("history", "a force push rewrites the history of the remote",
                    "Push without --force, --force-with-lease or a `+` refspec; if the remote moved, merge it first")
    return None


def branch_problem(branch):
    """The reason a branch command breaks the rules, or None: only a Spike's branch is deleted by force."""
    names = {name for name, _ in branch.options}
    forced_delete = "-D" in names or (names & {"-d", "--delete"} and names & {"-f", "--force"})
    if not forced_delete:
        return None
    kept = [name for name in branch.args if not name.startswith("spike/")]
    if kept:
        return rule("history", f"a forced delete of {', '.join(kept)}, which is not a Spike's branch, can lose commits",
                    "Delete it with `git branch -d`, which refuses a branch that is not merged; only `spike/` branches are deleted with -D")
    return None


VERSION_TAG = re.compile(r"v\d+\.\d+\.\d+|[a-z0-9][a-z0-9-]*--v\d+\.\d+\.\d+")
TAG_NOT_CREATING = {"-l", "--list", "-d", "--delete", "-v", "--verify", "-n", "--contains", "--no-contains",
                    "--merged", "--no-merged", "--points-at", "--sort", "--format"}


def tag_problem(tag):
    """The reason a tag breaks the rules, or None: a tag is a version, `vX.Y.Z` or `<plugin>--vX.Y.Z`."""
    if not tag.args or {name for name, _ in tag.options} & TAG_NOT_CREATING:
        return None
    if VERSION_TAG.fullmatch(tag.args[0]):
        return None
    return rule("tags", f"the tag {tag.args[0]} is not a version",
                "Tag only versions, named vX.Y.Z or <plugin>--vX.Y.Z (for example gemba-product--v0.1.0)")


CHECKS = {"tag": tag_problem, "branch": branch_problem, "merge": merge_problem, "rebase": rebase_problem, "pull": pull_problem, "push": push_problem}


def decide(event):
    cwd = event.get("cwd") or os.getcwd()
    command = event.get("tool_input", {}).get("command", "")
    found = git_commands.git_commands(command, cwd)
    parsed = False
    for git_command in found:
        check = CHECKS.get(git_command.subcommand)
        if check is None:
            continue
        parsed = True
        if not git_commands.in_gemba_project(git_command.folder, cwd):
            continue
        problem = check(git_command)
        if problem:
            deny(problem)
            return
    # The parser reads only a `git` at the start of a command. A wrapper (bash -c, sudo, a shell
    # keyword) hides the operation from it, so a command that looks like one asks with a generic reason.
    if not parsed and looks_like_an_operation(command) and git_commands.has_gemba(cwd):
        ask("history rules: this command has a git operation the hook could not read (a wrapper, a shell"
            " keyword or a quoted script). Confirm that it does not rewrite or lose history.")


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") != "Bash":
        return
    command = event.get("tool_input", {}).get("command", "")
    if git_commands is None:
        if looks_like_an_operation(command):
            ask("history rules: the hook could not load its parser. Confirm that this command does not rewrite or lose history.")
        return
    try:
        decide(event)
    except Exception:
        # A crash exits non-zero and does not block, so the operation would run unchecked: fail closed.
        if looks_like_an_operation(command):
            ask("history rules: the hook could not read the repository. Confirm that this command does not rewrite or lose history.")


if __name__ == "__main__":
    main()
