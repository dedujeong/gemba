#!/usr/bin/env python3
"""PreToolUse hook: the history rules of the method, for a project with setup.

Reads the hook event from stdin (alone, or through `bash_rules.py`, which calls `decide(event)`
for the answer `(decision, reason)` or None). When a Bash command does an operation that rewrites or loses
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

import fallback_words  # before git_commands: it still loads when the parser does not

git_commands = None  # imported by main() once the command is known to mention an operation

PROTECTED = fallback_words.PROTECTED_BRANCHES
FAST_FORWARD_OPTIONS = ("--ff", "--no-ff", "--ff-only")
MERGE_ENDS = {"--abort", "--continue", "--quit"}
REBASE_ENDS = {"--abort", "--continue", "--skip", "--quit", "--edit-todo", "--show-current-patch"}
OPERATIONS = fallback_words.OPERATIONS
OPERATION_WORDS = fallback_words.OPERATION_WORDS  # any git command with one of the operations: the cheap test that skips the others
BROKEN = fallback_words.RULES["history_rules"].broken
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
    names = git_commands.option_names(merge)
    if names & MERGE_ENDS:
        return None
    target = merge.branch
    if target not in PROTECTED:
        return None
    if "--squash" in names:
        return rule("merges", f"a squash merge into {target} loses the history of the branch",
                    "Merge with `git merge --no-ff <branch>` and Git's default message")
    if git_commands.syncs_with_its_remote(merge):
        return None
    last = [name for name, _ in merge.options if name in FAST_FORWARD_OPTIONS]
    if not last or last[-1] != "--no-ff":
        return rule("merges", f"a merge into {target} without --no-ff",
                    "Merge with `git merge --no-ff <branch>` so the branch stays in the history")
    if names & {"-m", "--message", "-F", "--file"}:
        return rule("merges", f"a merge into {target} with its own message",
                    "Merge with `git merge --no-ff <branch>` and keep Git's default message")
    return None


def count(folder, *revisions, not_pushed=False):
    """How many commits the revisions select (only those no remote has with `not_pushed`), or None when git
    cannot tell. A revision that starts with `-` would be an option of git: it is not read."""
    if any(revision.startswith("-") for revision in revisions):
        return None
    out = git_commands.git(folder, "rev-list", "--count", *revisions, *(("--not", "--remotes") if not_pushed else ()))
    return int(out) if out.isdigit() else None


def rebase_problem(rebase):
    """The reason a rebase breaks the rules, or None. The only rebase allowed is `--autosquash`
    over commits the remote does not have."""
    names = git_commands.option_names(rebase)
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
    not_pushed = count(rebase.folder, *revisions, not_pushed=True)
    if mine is None or not_pushed is None:
        return rule("rebase", f"the commits to rebase on {upstream} could not be read", todo)
    if mine != not_pushed:
        return rule("rebase", "the rebase rewrites commits the remote already has", todo)
    return None


REBASING_VALUES = {"true", "yes", "on", "1", "merges", "m", "interactive", "i"}


def configured_rebase(pull):
    """The value `pull.rebase` or `branch.<b>.rebase` gives this pull, or None. The `-c` of the command wins
    over the config files, and the key of the branch over `pull.rebase`."""
    keys = [f"branch.{pull.branch}.rebase"] if pull.branch else []
    for key in keys + ["pull.rebase"]:
        given = [value for name, value in pull.config if name.lower() == key.lower()]
        if given:
            return "true" if given[-1] is None else given[-1]
        value = git_commands.git(pull.folder, "config", "--get", key)
        if value:
            return value
    return None


def pull_problem(pull):
    """The reason a pull breaks the rules, or None: a pull that rebases, by option or by config, is a rebase."""
    rebasing = None  # the last of --rebase, -r and --no-rebase on the command line wins
    for name, value in pull.options:
        if name in ("--rebase", "-r"):
            rebasing = value is None or value.lower() in REBASING_VALUES
        elif name == "--no-rebase":
            rebasing = False
    if rebasing is None:
        rebasing = (configured_rebase(pull) or "").lower() in REBASING_VALUES
    if rebasing:
        return rule("rebase", "git pull that rebases rewrites history",
                    "Pull without rebasing: `git pull --no-rebase` or `git merge --ff-only origin/<branch>`")
    # Without a rebase a pull is a merge of what it fetches: of another branch it follows the merge rules.
    return merge_problem(pull)  # the merge rules read a pull through `syncs_with_its_remote`


FORCE_OPTIONS = {"--force", "-f", "--force-with-lease", "--force-if-includes", "--mirror"}


def push_problem(push):
    """The reason a push breaks the rules, or None: no force push, whatever its form."""
    forced = any(name in FORCE_OPTIONS for name, _ in push.options) or any(arg.startswith("+") for arg in push.args)
    if forced:
        return rule("history", "a force push rewrites the history of the remote",
                    "Push without --force, --force-with-lease, --mirror or a `+` refspec; if the remote moved, merge it first")
    names = git_commands.option_names(push)
    refspecs = push.args[1:]  # the first argument is the remote
    deleted = refspecs if names & {"--delete", "-d"} else [arg[1:] for arg in refspecs if arg.startswith(":")]
    releases = [name for name in deleted if VERSION_TAG.fullmatch(name.removeprefix("refs/tags/"))]
    if releases:
        return rule("tags", f"deleting the version tag {', '.join(releases)} on the remote loses a release",
                    "Keep the tag; a version tag is never deleted")
    lost = [name for name in deleted if name.removeprefix("refs/heads/") in PROTECTED]
    if lost:
        return rule("history", f"deleting {', '.join(lost)} on the remote loses the history of the project",
                    "Never delete develop or main; delete only the branch of a closed work item")
    return None


def branch_problem(branch):
    """The reason a branch command breaks the rules, or None: only a Spike's branch is deleted by force, and
    no branch is forced, renamed or copied over an existing one (the commits it had are discarded)."""
    names = git_commands.option_names(branch)
    forced = bool(names & {"-f", "--force"})
    if "-D" in names or (names & {"-d", "--delete"} and forced):
        kept = [name for name in branch.args if not name.startswith("spike/")]
        if kept:
            return rule("history", f"a forced delete of {', '.join(kept)}, which is not a Spike's branch, can lose commits",
                        "Delete it with `git branch -d`, which refuses a branch that is not merged; only `spike/` branches are deleted with -D")
        return None
    moving = names & {"-m", "--move", "-c", "--copy"}
    if "-M" in names or "-C" in names or (forced and moving):
        target = branch.args[-1] if branch.args else None
        source = branch.args[0] if len(branch.args) > 1 else branch.branch
    elif forced and not names & {"-d", "--delete"}:
        target, source = (branch.args[0] if branch.args else None), None
    else:
        return None
    if target and target != source and git_commands.is_branch(branch.folder, target):
        return rule("history", f"forcing the branch {target} over the one that exists discards its commits",
                    "Use another name, or merge the branch into the one you want and delete it with `git branch -d`")
    return None


VERSION_TAG = re.compile(r"v\d+\.\d+\.\d+|[a-z0-9][a-z0-9-]*--v\d+\.\d+\.\d+")
TAG_NOT_CREATING = {"-l", "--list", "-v", "--verify", "-n", "--contains", "--no-contains",
                    "--merged", "--no-merged", "--points-at", "--sort", "--format"}


def tag_problem(tag):
    """The reason a tag breaks the rules, or None: a tag is a version, `vX.Y.Z` or `<plugin>--vX.Y.Z`, a
    version tag is never deleted and an existing tag is never moved."""
    names = git_commands.option_names(tag)
    if names & {"-d", "--delete"}:
        versions = [name for name in tag.args if VERSION_TAG.fullmatch(name)]
        if versions:
            return rule("tags", f"deleting the version tag {', '.join(versions)} loses a release",
                        "Keep the tag; a version tag is never deleted")
        return None
    if not tag.args or names & TAG_NOT_CREATING:
        return None
    if not VERSION_TAG.fullmatch(tag.args[0]):
        return rule("tags", f"the tag {tag.args[0]} is not a version",
                    "Tag only versions, named vX.Y.Z or <plugin>--vX.Y.Z (for example gemba-product--v0.1.0)")
    if names & {"-f", "--force"} and git_commands.git(tag.folder, "rev-parse", "-q", "--verify", f"refs/tags/{tag.args[0]}"):
        return rule("tags", f"`-f` moves the tag {tag.args[0]}, which already exists",
                    "Do not move a tag; release the fix as the next version")
    return None


CHECKS = {"tag": tag_problem, "branch": branch_problem, "merge": merge_problem, "rebase": rebase_problem, "pull": pull_problem, "push": push_problem}


def decide(event):
    cwd = event.get("cwd") or os.getcwd()
    command = event.get("tool_input", {}).get("command", "")
    asking = False
    hidden = False
    for git_command in git_commands.git_commands(command, cwd) if git_commands.needs_walk(command, OPERATIONS) else ():
        hidden = hidden or git_commands.hides_subcommand(git_command, cwd)
        check = CHECKS.get(git_command.subcommand)
        if check is None:
            continue
        project = git_commands.project_of(git_command, cwd)
        if project == "no":
            continue
        if project == "unknown" or (git_command.subcommand in ("merge", "pull") and git_command.branch is None):
            asking = True  # a folder or a branch the parser could not follow: ask, do not decide
            continue
        problem = check(git_command)
        if problem:
            return "deny", problem
    if asking:
        return "ask", UNKNOWN
    if hidden:
        return "ask", "Gemba rule (history): " + git_commands.HIDDEN_SUBCOMMAND
    # The parser reads only a `git` at the start of a command. A wrapper (bash -c, sudo, a shell
    # keyword) hides the operation from it, so a segment that looks like one asks with a generic reason.
    if (git_commands.unparsed_mentions(command, WRAPPED_OPERATIONS) or git_commands.unparsed_hides_subcommand(command)) \
            and git_commands.has_gemba(cwd):
        return "ask", WRAPPED


def main():
    global git_commands
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") != "Bash":
        return
    command = event.get("tool_input", {}).get("command", "")
    if not fallback_words.mentions_git(command):
        return  # no git at all: skip the import and the parsing
    try:
        import git_commands
    except ImportError:  # a crash here would not block: ask for any command that mentions an operation
        if not fallback_words.relevant(command, OPERATION_WORDS):
            return
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "ask",
            "permissionDecisionReason": fallback_words.RULES["history_rules"].unloaded}}))
        return
    git_commands.run_hook(decide, lambda text: fallback_words.relevant(text, OPERATION_WORDS), BROKEN, event)


if __name__ == "__main__":
    main()
