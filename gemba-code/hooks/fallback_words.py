"""The words every Bash hook reads before it loads `git_commands`, and again when it fails to load or crashes.

Standard library only, and nothing else of the plugin: a hook imports this first, so it still loads when the parser
does not. It reads the raw text of a command, the way a model that forgot a rule would write it, not an adversary's:

- `unquoted(command)`: the command without quotes and backslashes (`pu""sh` is `push`, `pu\\sh` is `push`).
- `normalize(command)`: `unquoted` with a variable in the program position (`$GIT push`, `sudo ${GIT} push`) read as `git`.
- `mentions_git(command)`: the cheap gate: a `git` anywhere once quotes and escapes are gone.
- `hides_subcommand(command)`: a git command whose subcommand is a variable or a substitution (`git $P`, `git -C d $(x)`)
  or comes from an alias defined on the command line (`git -c alias.p=push p`).
- `relevant(command, pattern)`: what the ImportError and crash fallbacks ask for: the hook's own pattern on the
  normalized text, or a hidden subcommand.
"""
import re

_OPTIONS = r"(?:-\S+\s+(?:[^-\s$`]\S*\s+)?)*"  # global options of git, each with the value it may take
_SUBCOMMAND_VARIABLE = re.compile(rf"\bgit\s+{_OPTIONS}[$`]")
_COMMAND_LINE_ALIAS = re.compile(rf"\bgit\s+{_OPTIONS[:-1]}*?-c\s*alias\.")
_PROGRAM_VARIABLE = re.compile(
    r"((?:^|[;&|(!\n]\s*|\b(?:sudo|time|command|env|nice|nohup|exec|then|do|else|if|while|until)\s+)"
    r"(?:-\S+\s+|\w+=\S*\s+)*)\$(?:\{\w+\}|\w+)(?=\s)")


def unquoted(command):
    return re.sub(r"[\\'\"]", "", command)


def normalize(command):
    return _PROGRAM_VARIABLE.sub(r"\1git", unquoted(command))


def mentions_git(command):
    return re.search(r"\bgit\b", unquoted(command)) is not None


def hides_subcommand(command):
    text = unquoted(command)
    return bool(_SUBCOMMAND_VARIABLE.search(text) or _COMMAND_LINE_ALIAS.search(text))


def relevant(command, pattern):
    return bool(pattern.search(normalize(command)) or hides_subcommand(command))
