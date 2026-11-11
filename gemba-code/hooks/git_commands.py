"""Reads the git commands inside a shell command, for the hooks of the plugin.

Public API (everything a hook needs; nothing here runs anything but `git`):

- `git_commands(command, cwd=None)`: the `GitCommand` of every segment that is a git command, in order.
  `GitCommand(folder, subcommand, options, args, branch)`: `options` are ordered `(name, value)` pairs
  (`value` is None for a flag), `args` the positionals. With `cwd`, the walk follows the context of the
  compound command: `folder` is the folder the command runs in (`-C` on top of the `cd`s before it, on
  top of `cwd`) and `branch` the branch checked out there when the command runs (the real one, read once
  per folder, then the one tracked through `git switch` / `git checkout`). `folder=None` and
  `branch=None` mean "cannot tell" (`cd` alone, `cd -`, `cd $VAR`; `switch -`): the hook should ask, not
  decide. `branch == ""` is a detached HEAD. Without `cwd` nothing is resolved and `branch` is None.
  Returns [] when the command cannot be split (an unbalanced quote): treat that as unreadable.
- `unparsed_mentions(command, pattern)`: True when a segment that is NOT a parseable git command
  (`bash -c "..."`, `sudo git ...`, `if ...`, `echo ...`) mentions the pattern (a compiled regex, or a
  subcommand word such as "push" meaning `git ... push`). The arguments of a parsed git command are never
  searched, so `git commit -m "fix the merge"` does not mention `merge`. An unreadable command is searched
  whole. Use it as the fallback for wrapped commands.
- `parse(words)`, `segments(command)`: the building blocks; `mentions(command, word)` is the plain-text
  search for a hook's ImportError / crash fallback, where the parser itself may be broken.
- `emit(decision, reason)`: prints the PreToolUse decision (`allow`, `ask` or `deny`) a hook answers with.
- Repo helpers: `git`, `current_branch`, `gemba_section`, `gemba_field`, `has_gemba`, `in_gemba_project`.
"""
import functools
import json
import os
import re
import shlex
import subprocess
from collections import namedtuple

SEPARATORS = "();<>|&\n"
GLOBAL_OPTIONS_WITH_A_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}

# The options that take a value, per subcommand: the parser cannot tell `-m msg` from `-a msg` without it.
OPTIONS_WITH_A_VALUE = {
    "commit": {"-m", "--message", "-F", "--file", "-C", "-c", "--reuse-message", "--reedit-message",
               "--author", "--date", "--fixup", "--squash", "-t", "--template", "--trailer", "--cleanup",
               "--pathspec-from-file"},
    "merge": {"-m", "--message", "-F", "--file", "-s", "--strategy", "-X", "--strategy-option"},
    "push": {"-o", "--push-option", "--repo", "--receive-pack", "--exec"},
    "branch": {"-u", "--set-upstream-to"},
    "switch": {"-c", "-C", "--create", "--force-create", "--orphan"},
    "checkout": {"-b", "-B", "--orphan"},
    "worktree": {"-b", "-B", "--reason"},
    "tag": {"-m", "--message", "-F", "--file", "-u", "--local-user", "--cleanup", "--sort", "--format",
            "--contains", "--no-contains", "--points-at", "--merged", "--no-merged"},
    "rebase": {"--onto", "-x", "--exec", "-s", "--strategy", "-X", "--strategy-option"},
    "pull": {"-s", "--strategy", "-X", "--strategy-option"},
}

GitCommand = namedtuple("GitCommand", "folder subcommand options args branch", defaults=(None,))


def _words(command):
    """The words of the command with the separators as words of their own, or None when it cannot be split."""
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=SEPARATORS)
        lexer.whitespace_split = True
        lexer.whitespace = " \t\r"  # a new line separates commands
        lexer.commenters = ""  # bash starts a comment only at the start of a word, shlex also inside one
        return list(lexer)
    except ValueError:
        return None


def _is_separator(word):
    return set(word) <= set(SEPARATORS)


def segments(command):
    """The commands joined by &&, ||, ;, |, & or a new line as lists of words. Nothing when it cannot be split."""
    current = []
    for word in _words(command) or []:
        if _is_separator(word):
            if current:
                yield current
            current = []
        else:
            current.append(word)
    if current:
        yield current


def parse_options_and_args(subcommand, words):
    """(options, args) of the words after the subcommand."""
    takes_a_value = OPTIONS_WITH_A_VALUE.get(subcommand, set())
    options, args = [], []
    i = 0
    only_args = False
    while i < len(words) and not words[i].startswith("#"):
        word = words[i]
        i += 1
        if only_args or not word.startswith("-") or word == "-":
            args.append(word)
        elif word == "--":
            only_args = True
        elif word.startswith("--"):
            name, equals, value = word.partition("=")
            if equals:
                options.append((name, value))
            elif name in takes_a_value:
                options.append((name, words[i] if i < len(words) else None))
                i += 1
            else:
                options.append((name, None))
        else:
            # Bundled short options: -am msg, -mmsg. A value option takes the rest of the word or the next word.
            for position, letter in enumerate(word[1:], start=1):
                name = "-" + letter
                if name in takes_a_value:
                    rest = word[position + 1:]
                    if rest:
                        options.append((name, rest))
                    else:
                        options.append((name, words[i] if i < len(words) else None))
                        i += 1
                    break
                options.append((name, None))
    return options, args


def parse(words):
    """A GitCommand when the words are a git command, otherwise None."""
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
                # Git applies every -C on top of the one before, like successive cd.
                folder = os.path.join(folder, words[i + 1]) if folder else words[i + 1]
            i += 2
        else:
            i += 1
    if i >= len(words):
        return None
    options, args = parse_options_and_args(words[i], words[i + 1:])
    return GitCommand(folder, words[i], options, args)


def _cd_target(words):
    """The folder a `cd` segment goes to as written (`~` expanded), or None when it cannot be told."""
    args = [word for word in words[1:] if word not in ("-L", "-P", "-e", "-@", "--")]
    if len(args) != 1 or args[0] == "-" or re.search(r"[$`*?\[]", args[0]):
        return None
    return os.path.expanduser(args[0])


def _switches_to(command, words, folder):
    """The branch a git command leaves checked out, "" for a detached HEAD, None when it cannot be told,
    or UNCHANGED when it does not switch the branch."""
    names = dict(command.options)
    if command.subcommand not in ("switch", "checkout"):
        return UNCHANGED
    creating = ("-c", "-C", "--create", "--force-create") if command.subcommand == "switch" else ("-b", "-B")
    for name in creating + ("--orphan",):
        if names.get(name):
            return names[name]
    if "-d" in names or "--detach" in names:
        return ""
    if command.subcommand == "checkout" and "--" in words:
        return UNCHANGED
    if len(command.args) != 1:
        return UNCHANGED
    target = command.args[0]
    if target == "-":
        return None
    if ("-t" in names or "--track" in names) and "/" in target:
        return target.partition("/")[2]  # `origin/feat` creates and checks out the local `feat`
    if command.subcommand == "checkout" and folder and (
            os.path.exists(os.path.join(folder, target))
            and not git(folder, "rev-parse", "-q", "--verify", f"refs/heads/{target}")):
        return UNCHANGED  # a path, not a branch
    return target


UNCHANGED = object()


def git_commands(command, cwd=None):
    """The GitCommand of every segment of the command that is a git command, with the context of the walk
    (see the module docstring): `folder` and `branch` as they are when each command runs. Without `cwd`,
    `folder` is the `-C` folder as written (None when there is none) and `branch` is None."""
    items = _words(command)
    if items is None:
        return []
    found = []
    state = {"folder": cwd, "lost": False}
    saved = []
    branches = {}
    pending = []

    def folder_of(relative):
        if relative and os.path.isabs(relative):
            return relative
        if state["lost"]:
            return None
        if relative:
            return os.path.join(state["folder"], relative) if state["folder"] else relative
        return state["folder"]

    def apply(words, asynchronous):
        git_command = parse(words)
        if git_command is None:
            if words and words[0] == "cd" and not asynchronous:
                target = _cd_target(words)
                if target is None:
                    state["folder"], state["lost"] = None, True
                elif os.path.isabs(target):
                    state["folder"], state["lost"] = os.path.normpath(target), False
                elif not state["lost"]:
                    state["folder"] = os.path.normpath(os.path.join(state["folder"], target)) if state["folder"] else target
            return
        folder = folder_of(git_command.folder)
        branch = None
        if cwd is not None and folder is not None:
            key = repository_key(folder)
            if key not in branches:
                branches[key] = current_branch(folder)
            branch = branches[key]
            switched = _switches_to(git_command, words, folder)
            if switched is not UNCHANGED:
                branches[key] = switched
        found.append(git_command._replace(folder=folder, branch=branch))

    for word in items:
        if not _is_separator(word):
            pending.append(word)
            continue
        asynchronous = "|" in word or re.search(r"(?<!&)&(?!&)", word) is not None
        if pending:
            apply(pending, asynchronous)
        pending = []
        for char in word:
            if char == "(":
                saved.append(dict(state))
            elif char == ")" and saved:
                state = saved.pop()
    if pending:
        apply(pending, False)
    return found


def _word_pattern(subcommand):
    return re.compile(rf"\bgit\b.*(?<![\w-]){re.escape(subcommand)}(?![\w-])", re.DOTALL)


def unparsed_mentions(command, pattern):
    """True when a segment that is not a parseable git command mentions the pattern (a compiled regex, or a
    subcommand word meaning `git ... <word>`). The arguments of a parsed git command are never searched. An
    unreadable command (an unbalanced quote) is searched whole."""
    if isinstance(pattern, str):
        pattern = _word_pattern(pattern)
    items = _words(command)
    if items is None:
        return pattern.search(command) is not None
    return any(pattern.search(" ".join(words)) for words in segments(command) if parse(words) is None)


def mentions(command, subcommand):
    """True when the text has a git command with that subcommand anywhere, even where `parse` cannot read it
    (a wrapper such as bash -c or sudo, a shell keyword, a quoted script). Plain text, for the fallbacks of a
    hook whose parser may not load or may crash; otherwise use `unparsed_mentions`."""
    return re.search(rf"\bgit\b.*\b{re.escape(subcommand)}\b", command, re.DOTALL) is not None


def emit(decision, reason):
    """Prints the PreToolUse decision a hook answers with: `allow`, `ask` or `deny`, and why."""
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason,
    }}))


def git(folder, *args):
    result = subprocess.run(["git", "-C", folder, *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


_TOPLEVELS = {}
_KEYS = {}


def toplevel(folder):
    """The top folder of the repository of `folder` (the folder itself outside one). Read once per folder."""
    if folder not in _TOPLEVELS:
        found = git(folder, "rev-parse", "--show-toplevel")
        if not found:
            return folder
        _TOPLEVELS[folder] = found
    return _TOPLEVELS[folder]


def repository_key(folder):
    """A key that is the same from every folder of one repository (its git dir; the folder itself outside one)."""
    if folder not in _KEYS:
        found = git(folder, "rev-parse", "--absolute-git-dir")
        if not found:
            return os.path.normpath(folder)
        _KEYS[folder] = found
    return _KEYS[folder]


@functools.lru_cache(maxsize=None)
def _read(path, mtime, size):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def read_claude_md(folder):
    """The CLAUDE.md of the repository of `folder`, or None. Read once per file version within a hook run."""
    path = os.path.join(toplevel(folder), "CLAUDE.md")
    try:
        info = os.stat(path)
    except OSError:
        return None
    return _read(path, info.st_mtime_ns, info.st_size)


def gemba_section(folder):
    """The text of the `## Gemba` section of the repository's CLAUDE.md, or None."""
    text = read_claude_md(folder)
    if text is None:
        return None
    section = re.search(r"^## Gemba\s*$(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    return section.group(1) if section else None


def has_gemba(folder):
    return gemba_section(folder) is not None


def in_gemba_project(folder, cwd):
    """True when the folder the command runs in, or the session's folder, is a project with setup."""
    return has_gemba(folder) or (folder != cwd and has_gemba(cwd))


def gemba_field(folder, name):
    """The value of the `- <name>: <value>` line inside the `## Gemba` section of CLAUDE.md, or None."""
    section = gemba_section(folder)
    if section is None:
        return None
    line = re.search(rf"^- {re.escape(name)}:[ \t]*(.*?)[ \t]*$", section, re.MULTILINE)
    return line.group(1) if line else None


def current_branch(folder):
    return git(folder, "branch", "--show-current")
