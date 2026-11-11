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
- `project_of(command, cwd)`: "yes" when the repository the GitCommand runs in is a project with setup, "no" when it
  is not (the session's folder does not matter), "unknown" when the folder is None (a `cd` that cannot be
  followed) and the session's folder has setup. The one ladder every hook uses instead of testing `folder is
  None` itself. The folder counts `cd`, `-C`, `--git-dir`, `--work-tree` and the `GIT_DIR=` / `GIT_WORK_TREE=`
  prefixes (`--work-tree` first, else `--git-dir`, whose parent is the folder when it is a `.git`).
- `segment_folders(command, cwd)`: `(words, folder)` of every segment, git or not, with the same folder walk, for
  a hook that checks something else (`gh pr merge`).
- `syncs_with_its_remote(command)`: the one rule for "brings in only its own remote": a `merge`, or a `pull`
  (its refspecs read as `<remote>/<branch>`, none as `@{u}`), of only `@{u}`, `@{upstream}` or
  `<configured remote>/<the branch it runs on>`.
- `run_hook(decide, relevant, reason, event=None)`: the shared `main()` skeleton. Reads the event from stdin
  (or takes `event`), ignores everything but Bash, calls `decide(event)` and, if it raises, asks with
  `reason` when the command matches `relevant`, the hook's own pattern (a hook that crashes does not block: fail closed). A
  hook keeps inline only the branch for the module failing to import.
- `word_pattern(*words)`: the compiled regex `git ... <word>` (whole words, not `commit-graph`).
- Redirections are not part of a command: the operator and its target word (`2>&1`, `2>/dev/null`, `> f`,
  `>> f`, `< f`, `&> f`, `<<< text`, `<<WORD`) are dropped before the words are read, and so is the body of a
  heredoc (`<<WORD`, `<<'WORD'`, `<<"WORD"`, `<<-WORD`) up to its terminator line: its lines are text, not
  commands (the command line with the `<<` itself still is read). A heredoc without terminator swallows the
  rest. A number is a file descriptor only when it touches the operator (`2>&1`, not `2 > f`). A bare
  operator character inside quotes (`'>'`) is still read as an operator.
- `parse(words)`, `segments(command)`: the building blocks; `mentions(command, word)` is the plain-text
  search for a hook's ImportError / crash fallback, where the parser itself may be broken.
- `emit(decision, reason)`: prints the PreToolUse decision (`allow`, `ask` or `deny`) a hook answers with.
- Repo helpers: `git`, `current_branch`, `is_branch(folder, name)`, `toplevel`, `repository_key`,
  `gemba_section`, `gemba_field`, `has_gemba`. Repo reads are cached per run.
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

GitCommand = namedtuple("GitCommand", "folder subcommand options args branch config git_dir work_tree",
                        defaults=(None, (), None, None))


def _without_heredocs_and_descriptors(command):
    """The command without the bodies of its heredocs (up to the terminator line, which goes too) and without
    the file descriptor number in front of a redirection (`2>&1` becomes `>&1`: the number is part of the
    operator, not a word). Quote aware: an operator inside quotes is text. A heredoc whose terminator never
    comes swallows the rest of the command, like in bash."""
    out = []
    pending = []  # (delimiter, strip_tabs) of the heredocs opened on the current line
    i, n = 0, len(command)
    quote = None
    while i < n:
        char = command[i]
        if quote == "'":
            quote = None if char == "'" else quote
        elif quote == '"':
            if char == "\\" and i + 1 < n:
                out.append(char)
                i += 1
                char = command[i]
            elif char == '"':
                quote = None
        elif char == "\\" and i + 1 < n:
            out.append(char)
            i += 1
            char = command[i]
        elif char in "'\"":
            quote = char
        elif char == "\n" and pending:
            out.append(char)
            i += 1
            for delimiter, strip_tabs in pending:
                while i < n:
                    end = command.find("\n", i)
                    end = n if end == -1 else end
                    line = command[i:end]
                    i = min(end + 1, n)
                    if (line.lstrip("\t") if strip_tabs else line) == delimiter:
                        break
            pending = []
            continue
        elif char.isdigit() and (not out or out[-1] in " \t\n;&|()") and re.match(r"\d+[<>]", command[i:]):
            while command[i].isdigit():
                i += 1
            continue
        elif command.startswith("<<<", i):
            out.append("<<<")
            i += 3
            continue
        elif command.startswith("<<", i):
            match = re.compile(r"<<(-?)[ \t]*((?:[^\s;&|()<>'\"\\]|'[^']*'|\"[^\"]*\"|\\.)+)").match(command, i)
            if match:
                delimiter = re.sub(r"\\(.)|['\"]", r"\1", match.group(2))
                pending.append((delimiter, match.group(1) == "-"))
                out.append(command[i:match.end()])
                i = match.end()
                continue
        out.append(char)
        i += 1
    return "".join(out)


_REDIRECTION_CHARS = frozenset("<>&")


def _is_redirection(word):
    return set(word) <= _REDIRECTION_CHARS and ("<" in word or ">" in word)


def _without_redirections(words):
    """The words without the redirection operators and their target (`2>&1`, `> file`, `<<EOF`, `<<< text`)."""
    found = []
    i = 0
    while i < len(words):
        if _is_redirection(words[i]):
            i += 1
            if i < len(words) and not _is_separator(words[i]):
                i += 1
        else:
            found.append(words[i])
            i += 1
    return found


@functools.lru_cache(maxsize=32)
def _words(command):
    """The words of the command with the separators as words of their own (a tuple), or None when it cannot
    be split. Redirections (operator and target) and heredoc bodies are not words. Cached: one hook run
    tokenizes the same command once."""
    try:
        lexer = shlex.shlex(_without_heredocs_and_descriptors(command), posix=True, punctuation_chars=SEPARATORS)
        lexer.whitespace_split = True
        lexer.whitespace = " \t\r"  # a new line separates commands
        lexer.commenters = ""  # bash starts a comment only at the start of a word, shlex also inside one
        return tuple(_without_redirections(list(lexer)))
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
    env = {}
    while i < len(words) and re.fullmatch(r"\w+=.*", words[i]):
        name, _, value = words[i].partition("=")
        env[name] = value
        i += 1
    if i >= len(words) or os.path.basename(words[i]) != "git":
        return None
    i += 1
    folder = None
    config = []
    git_dir, work_tree = env.get("GIT_DIR"), env.get("GIT_WORK_TREE")  # the options win over the environment
    while i < len(words) and words[i].startswith("-"):
        option = words[i]
        name, equals, value = option.partition("=")
        if equals and name in ("--git-dir", "--work-tree"):
            git_dir, work_tree = (value, work_tree) if name == "--git-dir" else (git_dir, value)
            i += 1
        elif option in GLOBAL_OPTIONS_WITH_A_VALUE:
            if option in ("--git-dir", "--work-tree") and i + 1 < len(words):
                git_dir, work_tree = (words[i + 1], work_tree) if option == "--git-dir" else (git_dir, words[i + 1])
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
    return GitCommand(folder, words[i], options, args, config=tuple(config), git_dir=git_dir, work_tree=work_tree)


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


def _join(base, lost, relative):
    """`relative` on top of `base`: absolute stays, None when the base is lost, `base` itself without relative."""
    if relative and os.path.isabs(relative):
        return relative
    if lost:
        return None
    if relative:
        return os.path.join(base, relative) if base else relative
    return base


def _walk(command, cwd):
    """Each segment of the command as (words, base, lost): the folder it starts in (`cwd` after the `cd`s
    before it) and whether that folder is lost (a `cd` the parser cannot follow). Nothing when it cannot be split."""
    items = _words(command)
    if items is None:
        return
    state = {"folder": cwd, "lost": False}
    saved = []
    pending = []

    def segment(words, asynchronous):
        yield words, state["folder"], state["lost"]
        if words and words[0] == "cd" and parse(words) is None and not asynchronous:
            target = _cd_target(words)
            if target is None:
                state["folder"], state["lost"] = None, True
            elif _join(state["folder"], state["lost"], target) is not None:  # unknown stays unknown unless the target is absolute
                state["folder"], state["lost"] = os.path.normpath(_join(state["folder"], state["lost"], target)), False

    for word in items:
        if not _is_separator(word):
            pending.append(word)
            continue
        asynchronous = "|" in word or re.search(r"(?<!&)&(?!&)", word) is not None
        if pending:
            yield from segment(pending, asynchronous)
        pending = []
        for char in word:
            if char == "(":
                saved.append(dict(state))
            elif char == ")" and saved:
                state.clear()
                state.update(saved.pop())
    if pending:
        yield from segment(pending, False)


def segment_folders(command, cwd):
    """(words, folder) of every segment of the command, whatever it runs (`gh`, `cd`, `git`): the folder it runs
    in as `git_commands` follows it, None when it cannot be told. For a hook that checks a command that is not git."""
    return [(words, None if lost else base) for words, base, lost in _walk(command, cwd)]


def _repository_folder(command, base, lost):
    """The folder of the repository a GitCommand runs in: `--work-tree`, else the folder of `--git-dir` (its
    parent when it is a `.git`), else `-C`, each on top of the folder the command starts in."""
    start = _join(base, lost, command.folder)
    if command.work_tree:
        return _join(start, start is None, command.work_tree)
    if command.git_dir:
        git_dir = _join(start, start is None, command.git_dir)
        return git_dir and (os.path.dirname(os.path.normpath(git_dir)) if os.path.basename(os.path.normpath(git_dir)) == ".git"
                            else git_dir)
    return start


def git_commands(command, cwd=None):
    """The GitCommand of every segment of the command that is a git command, with the context of the walk
    (see the module docstring): `folder` and `branch` as they are when each command runs. Without `cwd`,
    `folder` is the `-C` folder as written (None when there is none) and `branch` is None."""
    found = []
    branches = {}
    for words, base, lost in _walk(command, cwd):
        git_command = parse(words)
        if git_command is None:
            continue
        folder = _repository_folder(git_command, base, lost)
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


def run_hook(decide, relevant, reason, event=None):
    """The shared `main()` of the hooks: reads the event from stdin (or takes `event`), ignores what is not a
    Bash command, calls `decide(event)` and fails closed. A crash of `decide` exits non-zero, which does not
    block, so when the command is one the hook checks it asks with `reason` instead. `relevant` is the hook's own
    pattern (a compiled regex, searched in the command), a tuple of git words, or a callable taking the command."""
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
        command = event.get("tool_input", {}).get("command", "")
        if isinstance(relevant, (tuple, list)):
            relevant = word_pattern(*relevant)
        if relevant(command) if callable(relevant) else relevant.search(command):
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


def project_of(command, cwd):
    """"yes", "no" or "unknown": whether the repository the GitCommand runs in (its folder: `cd`, `-C`,
    `--git-dir`, `--work-tree`, `GIT_DIR`, `GIT_WORK_TREE`) is a project with setup. The session's folder only
    matters when the folder cannot be told (None): "unknown" when it has setup, "no" when it has none."""
    if command.folder is None:
        return "unknown" if has_gemba(cwd) else "no"
    return "yes" if has_gemba(command.folder) else "no"


def gemba_field(folder, name):
    """The value of the `- <name>: <value>` line inside the `## Gemba` section of CLAUDE.md, or None."""
    section = gemba_section(folder)
    if section is None:
        return None
    line = re.search(rf"^- {re.escape(name)}:[ \t]*(.*?)[ \t]*$", section, re.MULTILINE)
    return line.group(1) if line else None


def current_branch(folder):
    return git(folder, "branch", "--show-current")


def pulled(pull):
    """What a `git pull` merges, as the arguments of a `git merge`: `<remote>/<branch>` for each refspec (the
    remote the pull names), `@{u}` when it names none."""
    remote = pull.args[0] if pull.args else None
    names = [arg.lstrip("+").partition(":")[0].removeprefix("refs/heads/") for arg in pull.args[1:]]
    return [f"{remote}/{name}" for name in names] if names else ["@{u}"]


def syncs_with_its_remote(command):
    """True when the `merge` (or the `pull`) brings in only `@{u}`, `@{upstream}` or `<remote>/<the branch it
    runs on>` of a configured remote: it updates the branch from its own remote and merges nothing else."""
    targets = pulled(command) if command.subcommand == "pull" else (command.args or ["@{u}"])  # a bare merge brings in @{u}
    remotes = git(command.folder, "remote").split()
    return all(target.lower() in ("@{u}", "@{upstream}") or any(target == f"{remote}/{command.branch}" for remote in remotes)
               for target in targets)
