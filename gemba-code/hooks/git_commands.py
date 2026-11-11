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
  of only `@{u}`, `@{upstream}` or `<configured remote>/<the branch it runs on>`; a pull of that branch from a
  configured remote or a url, or of a remote only when it is the upstream remote of the branch. The remotes
  are read lazily and once.
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

GitCommand = namedtuple("GitCommand", "folder subcommand options args branch config git_dir unresolved",
                        defaults=(None, (), None, False))


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
    while i < len(words):
        if re.fullmatch(r"\w+=.*", words[i]):
            name, _, value = words[i].partition("=")
            env[name] = value
        elif words[i] != "env" or i + 1 >= len(words) or not re.fullmatch(r"\w+=.*", words[i + 1]):
            break  # `env NAME=value git ...` is read; `env` with options or alone is a wrapper the parser does not read
        i += 1
    if i >= len(words) or os.path.basename(words[i]) != "git":
        return None
    i += 1
    folder = None
    config = []
    git_dir = env.get("GIT_DIR")  # `--git-dir` wins over the environment; `--work-tree` and GIT_WORK_TREE never change the repository
    while i < len(words) and words[i].startswith("-"):
        option = words[i]
        name, equals, value = option.partition("=")
        if equals and name == "--git-dir":
            git_dir = value
            i += 1
        elif option in GLOBAL_OPTIONS_WITH_A_VALUE:
            if option == "--git-dir" and i + 1 < len(words):
                git_dir = words[i + 1]
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
    return GitCommand(folder, words[i], options, args, config=tuple(config), git_dir=git_dir)


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
    """Each segment of the command as (words, base, lost, env): the folder it starts in (`cwd` after the `cd`s
    before it), whether that folder is lost (a `cd` the parser cannot follow) and the variables `export`ed before
    it (a dict). Nothing when it cannot be split."""
    items = _words(command)
    if items is None:
        return
    state = {"folder": cwd, "lost": False, "env": {}}
    saved = []
    pending = []

    def segment(words, asynchronous):
        yield words, state["folder"], state["lost"], dict(state["env"])
        if asynchronous or not words:
            return
        if words[0] == "export":
            for word in words[1:]:
                name, equals, value = word.partition("=")
                if equals:
                    state["env"][name] = value
        elif words[0] == "unset":
            for word in words[1:]:
                state["env"].pop(word, None)
        elif words[0] == "cd" and parse(words) is None:
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
                saved.append({**state, "env": dict(state["env"])})
            elif char == ")" and saved:
                state.clear()
                state.update(saved.pop())
    if pending:
        yield from segment(pending, False)


def segment_folders(command, cwd):
    """(words, folder, env) of every segment of the command, whatever it runs (`gh`, `cd`, `git`): the folder it
    runs in as `git_commands` follows it (None when it cannot be told) and the variables exported before it. For
    a hook that checks a command that is not git."""
    return [(words, None if lost else base, env) for words, base, lost, env in _walk(command, cwd)]


EXPANSION = re.compile(r"[$`~*?\[]")


@functools.lru_cache(maxsize=None)
def _main_worktree(start, git_dir):
    """The folder of the main worktree of the repository `git_dir` names (seen from `start`): the parent of its
    common git dir, which is the same for a linked worktree's git dir. None when git cannot read it, the
    common dir itself for a bare repository (it has no CLAUDE.md)."""
    command = ["git", f"--git-dir={git_dir}"] + (["-C", start] if start else [])
    result = subprocess.run(command + ["rev-parse", "--path-format=absolute", "--git-common-dir"],
                            capture_output=True, text=True)
    common = result.stdout.strip()
    if result.returncode != 0 or not common:
        return None
    return os.path.dirname(common) if os.path.basename(common) == ".git" else common


def _repository_folder(command, base, lost, env, cwd):
    """(folder, unresolved) of the repository a GitCommand runs in: the folder it starts in (`cd`, `-C`), or the
    main worktree of the repository `--git-dir` / `GIT_DIR` names (the work tree never changes the repository).
    `unresolved` when a value has a shell expansion or does not exist, or git cannot read the git dir: the
    caller must ask. A folder that cannot be told because of a `cd` is (None, False): the session decides."""
    if cwd is None:
        return _join(base, lost, command.folder), False
    git_dir = command.git_dir or env.get("GIT_DIR")
    if EXPANSION.search(command.folder or "") or EXPANSION.search(git_dir or ""):
        return None, True
    start = _join(base, lost, command.folder)
    if start is None and not (git_dir and os.path.isabs(git_dir)):
        return None, git_dir is not None
    if start is not None and not os.path.isdir(start):
        return None, True
    if git_dir:
        root = _main_worktree(start, git_dir)
        return root, root is None
    return start, False


def git_commands(command, cwd=None):
    """The GitCommand of every segment of the command that is a git command, with the context of the walk
    (see the module docstring): `folder` and `branch` as they are when each command runs. Without `cwd`,
    `folder` is the `-C` folder as written (None when there is none) and `branch` is None."""
    found = []
    branches = {}
    for words, base, lost, env in _walk(command, cwd):
        git_command = parse(words)
        if git_command is None:
            continue
        folder, unresolved = _repository_folder(git_command, base, lost, env, cwd)
        branch = None
        if cwd is not None and folder is not None:
            key = repository_key(folder)
            if key not in branches:
                branches[key] = current_branch(folder)
            branch = branches[key]
            switched = _switches_to(git_command, words, folder)
            if switched is not UNCHANGED:
                branches[key] = switched
        found.append(git_command._replace(folder=folder, branch=branch, unresolved=unresolved))
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
    matters when the folder cannot be told (None): "unknown" when it has setup, "no" when it has none. A folder or
    git dir that cannot be resolved (a shell expansion, a path that does not exist yet, git cannot read it) is
    always "unknown": the hook asks."""
    if command.unresolved:
        return "unknown"
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


@functools.lru_cache(maxsize=None)
def remotes(folder):
    """The names of the configured remotes of the repository of `folder`. Read once per folder, and only when needed."""
    return tuple(git(folder, "remote").split())


def _is_a_url(remote):
    return "/" in remote or ":" in remote or remote.startswith(".")


def syncs_with_its_remote(command):
    """True when the `merge` or the `pull` only updates the branch it runs on from its own remote: it brings in
    `@{u}`, `@{upstream}` or `<configured remote>/<that branch>` (a bare merge or pull is `@{u}`); a pull of
    the same branch from a configured remote or a url; a pull of a remote only, when it is the branch's upstream
    remote. Anything else merges another branch."""
    branch = command.branch
    if command.subcommand == "pull":
        remote = command.args[0] if command.args else None
        names = [arg.lstrip("+").partition(":")[0].removeprefix("refs/heads/") for arg in command.args[1:]]
        if remote is None:
            return True
        if not names:
            return bool(branch) and git(command.folder, "config", "--get", f"branch.{branch}.remote") == remote
        return all(name == branch for name in names) and (_is_a_url(remote) or remote in remotes(command.folder))
    return all(target.lower() in ("@{u}", "@{upstream}")
               or (bool(branch) and "/" in target and any(target == f"{remote}/{branch}" for remote in remotes(command.folder)))
               for target in (command.args or ["@{u}"]))  # a bare merge brings in @{u}
