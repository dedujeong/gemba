#!/usr/bin/env python3
"""PreToolUse hook: a project with setup only pushes and merges what its `Integration` mode allows.

Reads the hook event from stdin. In a project whose CLAUDE.md has a `## Gemba` section it denies the
`git push`, the local `git merge` (or `git pull` of another branch) into develop or main and the
`gh pr merge` that break the `Integration` mode, and asks (generic reason) for a push or merge it cannot
read. The mode is the one of the repository the command runs in, and the branch a bare push or a merge
acts on is the one the command has checked out when it runs. It prints nothing for what the mode allows,
so `confirm_push.py` still asks about every push. It never allows and never changes anything: it only runs
`git` to read the repository.
"""
import fnmatch
import json
import re
import os
import sys

import fallback_words  # before git_commands: it still loads when the parser does not

git_commands = None  # imported by main() once the command is known to mention a push, a merge or a pull

MODES = ("merge", "pull request")
MAIN_BRANCHES = ("develop", "main")
GIT_WORDS = ("push", "merge", "pull")
GH_PR_MERGE = re.compile(r"\bgh\b.*\bpr\b.*\bmerge\b", re.DOTALL)
# The cheap test that skips every other command before the parser is imported.
RELEVANT = re.compile(r"\bgit\b.*(?<![\w-])(?:%s)(?![\w-])|%s" % ("|".join(GIT_WORDS), GH_PR_MERGE.pattern), re.DOTALL)
UNREADABLE = ("Gemba rule (integration): this command contains a git push or a merge the hook could not read (a wrapper,"
              " a shell keyword, a folder or a branch it cannot tell or a quoted script), so it cannot check the"
              " integration mode. Confirm it.")
NOT_A_NEW_TAG = {"-d", "--delete", "-l", "--list", "-v", "--verify"}  # `git tag` options that create no tag
UNKNOWN = object()  # a branch the hook cannot tell


def configured_pushes(push):
    """What a push without refspecs writes because of the configuration: "matching" for `push.default=matching`,
    the refspecs of `remote.<name>.push` (of the remote it names, or of any remote when it names none), or None.
    One `git config --get-regexp` call."""
    remote = push.args[0] if push.args and not dict(push.options).get("--repo") else None
    refspecs = []
    for line in git_commands.git(push.folder, "config", "--get-regexp", r"^(push\.default|remote\..*\.push)$").splitlines():
        key, _, value = line.partition(" ")
        if key == "push.default" and value.strip().lower() == "matching":
            return "matching"
        if key.startswith("remote.") and (remote is None or key == f"remote.{remote}.push"):
            refspecs.append(value.strip())
    return refspecs or None


def is_a_tag(folder, name):
    return bool(git_commands.git(folder, "rev-parse", "--verify", "--quiet", f"refs/tags/{name}"))


def pushed_branches(push, created=()):
    """The branches a `git push` writes, UNKNOWN when it depends on a branch the hook cannot tell. Tag pushes and
    deletions write none. `--all`, `--branches` and `--mirror` are reported as `all branches`. `--repo <remote>` takes the
    remote, so then every positional is a refspec. `created` are the tags an earlier `git tag` of the same command makes."""
    flags = git_commands.option_names(push)
    if flags & {"--delete", "-d"}:
        return []
    if flags & {"--all", "--branches", "--mirror"}:
        return ["all branches"]
    names = dict(push.options)
    refspecs = push.args if names.get("--repo") else push.args[1:]
    tracked = push.branch
    if not refspecs:
        if "--tags" in flags:
            return []
        configured = configured_pushes(push)
        if configured is not None:
            if configured == "matching":
                return ["all branches"]
            refspecs = configured
    if not refspecs:
        return UNKNOWN if tracked is None else ([tracked] if tracked else [])
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
        if name in ("HEAD", "@"):  # `@` is an alias of HEAD
            if tracked is None:
                return UNKNOWN
            name = tracked
        elif not colon and (name in created or is_a_tag(push.folder, name)):
            continue
        name = name.removeprefix("refs/heads/")
        if name:
            branches.append(name)
    return branches


def push_problem(push, mode, created=()):
    """Why the push breaks the mode, None when the mode allows it, or UNKNOWN."""
    branches = pushed_branches(push, created)
    if branches is UNKNOWN:
        return UNKNOWN
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
        main = ["develop and main" if branch == "all branches" else branch
                for branch in branches if branch == "all branches" or any(fnmatch.fnmatchcase(m, branch) for m in MAIN_BRANCHES)]
        if main:
            return (f"Gemba rule (integration: pull request): develop and main are not pushed ({', '.join(main)})."
                    " Push the work branch and open a pull request; the maintainer merges it.")
    return None


def merge_problem(command, mode):
    """Why a local `git merge`, or a `git pull` of another branch, breaks the mode, None, or UNKNOWN."""
    if mode != "pull request" or git_commands.option_names(command) & {"--abort", "--continue", "--quit"}:
        return None
    if command.branch is None:
        return UNKNOWN
    if command.branch not in MAIN_BRANCHES:
        return None
    if git_commands.syncs_with_its_remote(command) and \
            (command.subcommand == "pull" or "--ff-only" in git_commands.option_names(command)):
        return None  # `git pull [origin develop]` and `git merge --ff-only origin/develop` on develop only sync it
    return (f"Gemba rule (integration: pull request): nothing is merged locally into {command.branch}."
            " Open a pull request from the work branch; the maintainer merges it.")


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


def names_a_repository(words, env):
    """True when a `gh` command (or a wrapper of one) names its repository with `-R`, `--repo` or `GH_REPO`."""
    return "GH_REPO" in env or any(re.fullmatch(r"GH_REPO=.*|-R.*|--repo(=.*)?", word) or "GH_REPO=" in word
                                   for word in words if not word.startswith("---"))


def wraps_pr_merge(words):
    """True when a segment that is not `gh` itself hides a `gh ... pr merge` (a wrapper such as `sudo` or
    `bash -c '...'`): a word that is `gh` followed by a pr merge, or a quoted script that has one."""
    for i, word in enumerate(words):
        if os.path.basename(word) == "gh" and is_pr_merge(words[i:]):
            return True
        if " " in word and any(is_pr_merge(inner) or (gh_words(inner) is None and wraps_pr_merge(inner))
                               for inner in git_commands.segments(word)):
            return True
    return False


def decide(event):
    cwd = event.get("cwd") or os.getcwd()
    command = event.get("tool_input", {}).get("command", "")
    modes = {}  # repository -> its mode, read once
    # The cheap test before any repository is read: no git command that matters, no gh pr merge, nothing hidden.
    walk = git_commands.needs_walk(command, GIT_WORDS + ("tag",))
    if not (walk or GH_PR_MERGE.search(fallback_words.unquoted(command))
            or git_commands.unparsed_mentions(command, ("push", "merge", "pull"))
            or git_commands.unparsed_hides_subcommand(command)):
        return

    def mode_of(folder):
        key = git_commands.toplevel(folder)
        if key not in modes:
            modes[key] = (git_commands.gemba_field(folder, "Integration") or "").strip().lower() or None
        return modes[key]

    asking = False
    tags = {}  # repository -> the tags an earlier `git tag` of this command creates
    hidden = False
    for found in git_commands.git_commands(command, cwd) if walk else ():
        hidden = hidden or git_commands.hides_subcommand(found, cwd)
        if found.subcommand == "tag" and found.folder and not git_commands.option_names(found) & NOT_A_NEW_TAG:
            tags.setdefault(git_commands.repository_key(found.folder), set()).update(found.args[:1])
        if found.subcommand not in GIT_WORDS:
            continue
        project = git_commands.project_of(found, cwd)
        if project == "no":
            continue  # a repository without a Gemba section
        if project == "unknown":
            asking = asking or found.subcommand == "push" or mode_of(cwd) != "merge"
            continue
        if found.subcommand == "push":
            problem = push_problem(found, mode_of(found.folder), tags.get(git_commands.repository_key(found.folder), ()))
        else:
            problem = merge_problem(found, mode_of(found.folder))
        if problem is UNKNOWN:
            asking = True
        elif problem:
            return git_commands.emit("deny", problem)
    in_project = git_commands.has_gemba(cwd)
    for words, folder, env in git_commands.segment_folders(command, cwd):
        is_plain = is_pr_merge(words)
        if not (is_plain or (gh_words(words) is None and wraps_pr_merge(words))):
            continue
        if names_a_repository(words, env):  # `-R`, `--repo`, `GH_REPO`: the folder does not tell which repository it is
            asking = True
        elif folder is None:  # a cd the parser could not follow: only the session's project can be asked about
            asking = asking or (in_project and mode_of(cwd) != "merge")
        elif git_commands.has_gemba(folder):
            if is_plain and mode_of(folder) == "pull request":
                return git_commands.emit(
                    "deny", "Gemba rule (integration: pull request): gh pr merge is not run by Claude."
                            " The maintainer merges the pull request.")
            asking = asking or (not is_plain and mode_of(folder) != "merge")  # a hidden one, like a hidden merge
    if asking or hidden:
        return git_commands.emit("ask", UNREADABLE if asking else "Gemba rule (integration): " + git_commands.HIDDEN_SUBCOMMAND)
    # The parser reads only a `git` at the start of a command. A wrapper (bash -c, sudo, a shell keyword)
    # hides it, so a command that mentions one asks with a generic reason. A local merge, a pull or a pull
    # request merge is only a rule in pull request mode, so only there is a hidden one asked about.
    if not in_project:
        return
    hidden_push = git_commands.unparsed_mentions(command, "push")
    hidden_merge = git_commands.unparsed_mentions(command, ("merge", "pull"))
    if hidden_push or git_commands.unparsed_hides_subcommand(command) or (hidden_merge and mode_of(cwd) != "merge"):
        git_commands.emit("ask", UNREADABLE)


def main():
    global git_commands
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") != "Bash":
        return
    command = event.get("tool_input", {}).get("command", "")
    if not (fallback_words.mentions_git(command) or GH_PR_MERGE.search(fallback_words.unquoted(command))):
        return  # no git or gh pr merge at all: skip the import and the parsing
    try:
        import git_commands
    except ImportError:  # a crash here would not block: ask for any command that mentions one
        if not fallback_words.relevant(command, RELEVANT):
            return
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": UNREADABLE}}))
        return
    git_commands.run_hook(decide, lambda text: fallback_words.relevant(text, RELEVANT), UNREADABLE, event)


if __name__ == "__main__":
    main()
