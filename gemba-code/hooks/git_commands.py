"""Reads the git commands inside a shell command, for the hooks of the plugin.

Public API (everything a hook needs; nothing here runs anything but `git`):

- `git_commands(command, cwd=None)`: the `GitCommand` of every segment that is a git command, in order.
  `GitCommand(folder, subcommand, options, args, branch, config)`: `config` are the `-c key=value` pairs of the
  git global options, in order (`()` when none; the value is None for a bare key); `options` are ordered `(name, value)` pairs
  (`value` is None for a flag), `args` the positionals. With `cwd`, the walk follows the context of the
  compound command: `folder` is the folder the command runs in (`-C` on top of the `cd`s before it, on
  top of `cwd`) and `branch` the branch checked out there when the command runs (the real one, read once
  per folder, then the one tracked through `git switch` / `git checkout`). `folder=None` and
  `branch=None` mean "cannot tell" (`cd` alone, `cd -`, `cd $VAR`; `switch -`): the hook should ask, not
  decide. `branch == ""` is a detached HEAD. Without `cwd` nothing is resolved and `branch` is None.
  Returns [] when the command cannot be split (an unbalanced quote): treat that as unreadable.
- `unparsed_mentions(command, pattern)`: True when a segment that is NOT a parseable git command
  (`bash -c "..."`, `sudo git ...`, `if ...`, `echo ...`) mentions the pattern (a compiled regex, a
  subcommand word such as "push" meaning `git ... push`, or a tuple of such words). The arguments of a parsed git command are never
  searched, so `git commit -m "fix the merge"` does not mention `merge`. An unreadable command is searched
  whole. Use it as the fallback for wrapped commands.
- Commands that move the tracked branch: `git switch` and `git checkout` to an existing branch, their create
  forms (`switch -c|-C|--create|--force-create`, `checkout -b|-B`, `--orphan`), their track forms
  (`-t|--track <remote>/<b>` checks out the local `<b>`), `--detach` (branch ""), and `switch -` /
  `checkout -` (unknown). A path checkout (`checkout -- f`, `checkout f` of an existing path) does not.
  Nothing else moves it: `branch -m`, `reset`, `rebase`, `worktree`, `pull`, `merge` leave the tracked
  branch as it is. The branch belongs to the repository (`repository_key`), not to the folder.
- `option_names(command)`: the set of option names of a GitCommand.
- `project_of(command, cwd)`: "yes" when the folder of the GitCommand is in a project with setup, "no" when it
  is not, "unknown" when the folder is None (a `cd` that cannot be followed) and the session's folder has
  setup. The one ladder every hook uses instead of testing `folder is None` itself.
- `run_hook(decide, words, reason, event=None)`: the shared `main()` skeleton. Reads the event from stdin
  (or takes `event`), ignores everything but Bash, calls `decide(event)` and, if it raises, asks with
  `reason` when the command mentions one of `words` (a hook that crashes does not block: fail closed). A
  hook keeps inline only the branch for the module failing to import.
- `word_pattern(*words)`: the compiled regex `git ... <word>` (whole words, not `commit-graph`).
- `parse(words)`, `segments(command)`: the building blocks; `mentions(command, word)` is the plain-text
  search for a hook's ImportError / crash fallback, where the parser itself may be broken.
- `emit(decision, reason)`: prints the PreToolUse decision (`allow`, `ask` or `deny`) a hook answers with.
- Repo helpers: `git`, `current_branch`, `is_branch(folder, name)`, `toplevel`, `repository_key`,
  `gemba_section`, `gemba_field`, `has_gemba`, `in_gemba_project`. Repo reads are cached per run.
"""
import functools
import json
import os
import re
import shlex
import subprocess
import sys
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
    "pull": {"-s", "--strategy", "-X", "--strategy-option", "--depth", "--deepen", "--shallow-since",
             "--shallow-exclude", "-j", "--jobs", "--upstream-pack", "-o", "--server-option"},
}

GitCommand = namedtuple("GitCommand", "folder subcommand options args branch config", defaults=(None, ()))


@functools.lru_cache(maxsize=32)
def _words(command):
    """The words of the command with the separators as words of their own (a tuple), or None when it cannot
    be split. Cached: one hook run tokenizes the same command once."""
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=SEPARATORS)
        lexer.whitespace_split = True
        lexer.whitespace = " \t\r"  # a new line separates commands
        lexer.commenters = ""  # bash starts a comment only at the start of a word, shlex also inside one
        return tuple(lexer)
    except ValueError:
        return None


_SEPARATOR_CHARS = frozenset(SEPARATORS)


def _is_separator(word):
    return set(word) <= _SEPARATOR_CHARS


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
    config = []
    while i < len(words) and words[i].startswith("-"):
        option = words[i]
        if option in GLOBAL_OPTIONS_WITH_A_VALUE:
            if option == "-c" and i + 1 < len(words):
                key, equals, value = words[i + 1].partition("=")
                config.append((key, value if equals else None))  # a bare key has no value: git reads it as true
            if option == "-C" and i + 1 < len(words):
                # Git applies every -C on top of the one before, like successive cd.
                folder = os.path.join(folder, words[i + 1]) if folder else words[i + 1]
            i += 2
        else:
            i += 1
    if i >= len(words):
        return None
    options, args = parse_options_and_args(words[i], words[i + 1:])
    return GitCommand(folder, words[i], options, args, config=tuple(config))


def option_names(command):
    """The set of option names of a GitCommand."""
    return {name for name, _ in command.options}


def _cd_target(words):
    """The folder a `cd` segment goes to as written (`~` expanded), or None when it cannot be told."""
    args = [word for word in words[1:] if word not in ("-L", "-P", "-e", "-@", "--")]
    if len(args) != 1 or args[0] == "-" or re.search(r"[$`*?\[]", args[0]):
        return None
    return os.path.expanduser(args[0])


UNCHANGED = object()


def _switches_to(command, words, folder):
    """The branch a git command leaves checked out, "" for a detached HEAD, None when it cannot be told,
    or UNCHANGED when it does not switch the branch."""
    if command.subcommand not in ("switch", "checkout"):
        return UNCHANGED
    names = dict(command.options)
    for name in OPTIONS_WITH_A_VALUE[command.subcommand]:  # the options that create a branch take its name
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
    if command.subcommand == "checkout" and folder and os.path.exists(os.path.join(folder, target)) \
            and not is_branch(folder, target):
        return UNCHANGED  # a path, not a branch
    return target


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
                elif folder_of(target) is not None:  # unknown stays unknown unless the target is absolute
                    state["folder"], state["lost"] = os.path.normpath(folder_of(target)), False
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


@functools.lru_cache(maxsize=None)
def word_pattern(*words):
    """The compiled regex for `git ... <word>` with any of the words, as whole words (`commit` is not `commit-graph`)."""
    alternatives = "|".join(re.escape(word) for word in words)
    return re.compile(rf"\bgit\b.*(?<![\w-])(?:{alternatives})(?![\w-])", re.DOTALL)


def unparsed_mentions(command, pattern):
    """True when a segment that is not a parseable git command mentions the pattern (a compiled regex, a
    subcommand word meaning `git ... <word>`, or a tuple of such words). The arguments of a parsed git command
    are never searched. An unreadable command (an unbalanced quote) is searched whole."""
    if isinstance(pattern, str):
        pattern = word_pattern(pattern)
    elif isinstance(pattern, (tuple, list)):
        pattern = word_pattern(*pattern)
    if _words(command) is None:
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


def run_hook(decide, words, reason, event=None):
    """The shared `main()` of the hooks: reads the event from stdin (or takes `event`), ignores what is not a
    Bash command, calls `decide(event)` and fails closed. A crash of `decide` exits non-zero, which does not
    block, so when the command mentions one of `words` it asks with `reason` instead."""
    if event is None:
        try:
            event = json.load(sys.stdin)
        except ValueError:
            return
    if event.get("tool_name") != "Bash":
        return
    try:
        decide(event)
    except Exception:
        if word_pattern(*words).search(event.get("tool_input", {}).get("command", "")):
            emit("ask", reason)


def git(folder, *args):
    result = subprocess.run(["git", "-C", folder, *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


@functools.lru_cache(maxsize=None)
def toplevel(folder):
    """The top folder of the repository of `folder` (the folder itself outside one). Read once per folder."""
    return git(folder, "rev-parse", "--show-toplevel") or folder


@functools.lru_cache(maxsize=None)
def repository_key(folder):
    """A key that is the same from every folder of one repository (its git dir; the folder itself outside one)."""
    return git(folder, "rev-parse", "--absolute-git-dir") or os.path.normpath(folder)


def is_branch(folder, name):
    """True when `name` is a local branch of the repository of `folder`."""
    return bool(git(folder, "rev-parse", "-q", "--verify", f"refs/heads/{name}"))


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


def project_of(command, cwd):
    """"yes", "no" or "unknown": whether the GitCommand runs in a project with setup (see the module docstring)."""
    if command.folder is None:
        return "unknown" if has_gemba(cwd) else "no"
    return "yes" if in_gemba_project(command.folder, cwd) else "no"


def gemba_field(folder, name):
    """The value of the `- <name>: <value>` line inside the `## Gemba` section of CLAUDE.md, or None."""
    section = gemba_section(folder)
    if section is None:
        return None
    line = re.search(rf"^- {re.escape(name)}:[ \t]*(.*?)[ \t]*$", section, re.MULTILINE)
    return line.group(1) if line else None


def current_branch(folder):
    return git(folder, "branch", "--show-current")
