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

git_commands = None  # imported by main() once the command is known to mention an operation

PROTECTED = ("develop", "main")
FAST_FORWARD_OPTIONS = ("--ff", "--no-ff", "--ff-only")
MERGE_ENDS = {"--abort", "--continue", "--quit"}
REBASE_ENDS = {"--abort", "--continue", "--skip", "--quit", "--edit-todo", "--show-current-patch"}
OPERATIONS = ("merge", "rebase", "pull", "push", "branch", "tag")
# Any git command with one of the operations, as whole words: the cheap test that skips every other command.
OPERATION_WORDS = re.compile(r"\bgit\b.*(?<![\w-])(?:%s)(?![\w-])" % "|".join(OPERATIONS), re.DOTALL)
BROKEN = ("Gemba rule (history): the hook could not read the repository. "
          "Confirm that this command does not rewrite or lose history.")
UNKNOWN = ("Gemba rule (history): the folder or the branch this command runs on could not be told. Run it from a plain "
           "folder, with one `cd` to a path or `-C`, so the hook can check that it does not rewrite or lose history.")
WRAPPED = ("Gemba rule (history): this command has a git operation the hook could not read (a wrapper, a shell"
           " keyword or a quoted script). Confirm that it does not rewrite or lose history.")

# What an operation looks like in a segment the parser cannot read (bash -c, sudo, a shell keyword).
WRAPPED_OPERATIONS = re.compile("|".join("(?:%s)" % pattern for pattern in (
    r"\bgit\b.*(?<![\w-])(?:merge|rebase|tag)(?![\w-])",
    r"\bgit\b.*\bpull\b.*(--rebase|\s-\w*r)",
    r"\bgit\b.*\bpush\b.*(--force|--mirror|--delete|\s-\w*[fd]|\s[+:])",
    r"\bgit\b.*\bbranch\b.*(--force|\s-\w*[DfMC])",
)), re.DOTALL)


def rule(name, wrong, todo):
    return f"Gemba rule ({name}): {wrong}. {todo}."


def merge_problem(merge):
    """The reason a merge breaks the rules, or None."""
    names = {name for name, _ in merge.options}
    if names & MERGE_ENDS:
        return None
    target = merge.branch
    if target not in PROTECTED:
        return None
    if "--squash" in names:
        return rule("merges", f"a squash merge into {target} loses the history of the branch",
                    "Merge with `git merge --no-ff <branch>` and Git's default message")
    updates_from_remote = all(arg in (f"origin/{target}", "@{u}", "@{upstream}") for arg in merge.args)
    if updates_from_remote:
        return None
    last = [name for name, _ in merge.options if name in FAST_FORWARD_OPTIONS]
    if not last or last[-1] != "--no-ff":
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
    if "--root" in names:  # every commit of the branch is rebased: `<branch>` is the only argument
        upstream = "the root"
        revisions = [rebase.args[0] if rebase.args else "HEAD"]
    else:
        upstream = rebase.args[0] if rebase.args else "@{u}"
        revisions = [f"{upstream}..{rebase.args[1] if len(rebase.args) > 1 else 'HEAD'}"]
    mine = count(rebase.folder, *revisions)
    not_pushed = count(rebase.folder, *revisions, "--not", "--remotes")
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
    asking = False
    for git_command in git_commands.git_commands(command, cwd):
        check = CHECKS.get(git_command.subcommand)
        if check is None:
            continue
        project = git_commands.project_of(git_command, cwd)
        if project == "no":
            continue
        if project == "unknown" or (git_command.subcommand == "merge" and git_command.branch is None):
            asking = True  # a folder or a branch the parser could not follow: ask, do not decide
            continue
        problem = check(git_command)
        if problem:
            return git_commands.emit("deny", problem)
    if asking:
        return git_commands.emit("ask", UNKNOWN)
    # The parser reads only a `git` at the start of a command. A wrapper (bash -c, sudo, a shell
    # keyword) hides the operation from it, so a segment that looks like one asks with a generic reason.
    if git_commands.unparsed_mentions(command, WRAPPED_OPERATIONS) and git_commands.has_gemba(cwd):
        git_commands.emit("ask", WRAPPED)


def main():
    global git_commands
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") != "Bash":
        return
    if not OPERATION_WORDS.search(event.get("tool_input", {}).get("command", "")):
        return  # no merge, rebase, pull, push, branch or tag anywhere: skip the import and the parsing
    try:
        import git_commands
    except ImportError:  # a crash here would not block: ask for any command that mentions an operation
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "ask",
            "permissionDecisionReason": "Gemba rule (history): the hook could not load its parser. Confirm that this command does not rewrite or lose history."}}))
        return
    git_commands.run_hook(decide, OPERATIONS, BROKEN, event)


if __name__ == "__main__":
    main()
