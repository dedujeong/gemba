"""Reads the git commands inside a shell command, for the hooks of the plugin.

`git_commands(command)` splits a compound command into its git commands. Each one is a
`GitCommand(folder, subcommand, options, args)`: the folder from `-C`, the subcommand, the
options as ordered `(name, value)` pairs (`value` is None for a flag) and the positionals.
The module also has the repo helpers the hooks share. It never runs anything but `git`.
"""
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
    "worktree": {"-b", "-B"},
    "tag": {"-m", "--message", "-F", "--file", "-u", "--local-user"},
    "rebase": {"--onto", "-x", "--exec", "-s", "--strategy", "-X", "--strategy-option"},
    "pull": {"-s", "--strategy", "-X", "--strategy-option"},
}

GitCommand = namedtuple("GitCommand", "folder subcommand options args")


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


def git_commands(command, cwd=None):
    """The GitCommand of every segment of the command that is a git command. With `cwd`, each folder is
    resolved against it: the `-C` folder joined to `cwd`, or `cwd` itself when there is no `-C`."""
    found = [command for command in map(parse, segments(command)) if command is not None]
    if cwd is None:
        return found
    return [command._replace(folder=os.path.join(cwd, command.folder) if command.folder else cwd)
            for command in found]


def mentions(command, subcommand):
    """True when the text has a git command with that subcommand anywhere, even where `parse` cannot read it
    (a wrapper such as bash -c or sudo, a shell keyword, a quoted script)."""
    return re.search(rf"\bgit\b.*\b{re.escape(subcommand)}\b", command, re.DOTALL) is not None


def git(folder, *args):
    result = subprocess.run(["git", "-C", folder, *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def read_claude_md(folder):
    top = git(folder, "rev-parse", "--show-toplevel") or folder
    try:
        with open(os.path.join(top, "CLAUDE.md"), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


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
