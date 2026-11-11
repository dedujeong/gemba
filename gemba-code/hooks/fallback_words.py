"""The words every Bash hook reads before it loads `git_commands`, and again when it fails to load or crashes.

Standard library only, and nothing else of the plugin: a hook imports this first, so it still loads when the parser
does not. It reads the raw text of a command, the way a model that forgot a rule would write it, not an adversary's:

- `unquoted(command)`: the command without quotes and backslashes (`pu""sh` is `push`, `pu\\sh` is `push`).
- `normalize(command)`: `unquoted` with a variable in the program position (`$GIT push`, `sudo ${GIT} push`) read as `git`.
- `mentions_git(command)`: the cheap gate: a `git` anywhere once quotes, escapes and a program variable are gone.
- `hides_subcommand(command)`: a git command whose subcommand is a variable or a substitution (`git $P`, `git -C d $(x)`)
  or comes from an alias defined on the command line (`git -c alias.p=push p`).
- `relevant(command, pattern)`: what the ImportError and crash fallbacks ask for: the hook's own pattern on the
  normalized text, or a hidden subcommand.
- `PROTECTED_BRANCHES`: develop and main, the one place every rule reads them from.
- `RULES`: every Bash rule (`Rule(name, pattern, gate, unloaded, broken)`): the pattern of what it checks, the cheap
  gate before it loads `git_commands`, and the reasons it asks with when its parser does not load (`unloaded`) or
  it crashes (`broken`). A rule script and the dispatcher `bash_rules.py` both read them from here.
"""
import re

PROTECTED_BRANCHES = ("develop", "main")

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
    return re.search(r"\bgit\b", normalize(command)) is not None


def hides_subcommand(command):
    text = unquoted(command)
    return bool(_SUBCOMMAND_VARIABLE.search(text) or _COMMAND_LINE_ALIAS.search(text))


def relevant(command, pattern):
    return bool(pattern.search(normalize(command)) or hides_subcommand(command))


class Rule:
    """One Bash rule: its pattern, its gate and the reasons it asks with (plain class: standard library only)."""

    def __init__(self, name, pattern, gate, unloaded, broken):
        self.name, self.pattern, self.gate, self.unloaded, self.broken = name, pattern, gate, unloaded, broken

CREATES_COMMITS = ("commit", "revert", "cherry-pick", "am")
_BRANCH_MODE = (r"-[dDlarvu]\S*|--(?:delete|list|all|remotes|verbose|show-current|contains|no-contains|merged"
                r"|no-merged|set-upstream-to|unset-upstream|edit-description|points-at|sort|format)(?![\w-])")
OPERATIONS = ("merge", "rebase", "pull", "push", "branch", "tag")
GIT_WORDS = ("push", "merge", "pull")  # integration_rules.py has the same pattern of its own (a test keeps them equal)
GH_PR_MERGE = re.compile(r"\bgh\b.*\bpr\b.*\bmerge\b", re.DOTALL)

MENTIONS_A_PUSH = re.compile(r"\bgit\b.*\bpush\b", re.DOTALL)
# Any git command that creates a commit, as whole words: the cheap test that skips every other command.
CREATING_WORDS = re.compile(r"\bgit\b.*(?<![\w-])(?:%s|merge\b.*--continue)(?![\w-])"
                            % "|".join(map(re.escape, CREATES_COMMITS)), re.DOTALL)
# A clear creation form of a branch, for a command the parser cannot read and for the fallbacks.
# `git branch` takes any leading options, except those of a mode that lists, deletes or edits.
BRANCH_CREATING = re.compile(
    r"\bgit\b.*(?<![\w-])(?:"
    r"(?:switch|checkout)\s(?:.*\s)?-(?:[a-zA-Z]*[cCbB]|-create|-force-create|-orphan)(?![\w-])"
    r"|worktree\s+add\s(?:.*\s)?-[bB](?![\w-])"
    rf"|branch\s+(?:(?!{_BRANCH_MODE})-\S*\s+)*[^-\s]"
    r"|branch\s(?:.*\s)?(?:-[a-zA-Z]*[mMcC]|--move|--copy)(?![\w-])"
    r")", re.DOTALL)
OPERATION_WORDS = re.compile(r"\bgit\b.*(?<![\w-])(?:%s)(?![\w-])" % "|".join(OPERATIONS), re.DOTALL)
INTEGRATION_RELEVANT = re.compile(r"\bgit\b.*(?<![\w-])(?:%s)(?![\w-])|%s" % ("|".join(GIT_WORDS), GH_PR_MERGE.pattern),
                                  re.DOTALL)


def _git_or_pr_merge(command):
    return mentions_git(command) or GH_PR_MERGE.search(unquoted(command)) is not None


UNREADABLE_INTEGRATION = ("Gemba rule (integration): this command contains a git push or a merge the hook could not read (a wrapper,"
                          " a shell keyword, a folder or a branch it cannot tell or a quoted script), so it cannot check the"
                          " integration mode. Confirm it.")

RULES = {rule.name: rule for rule in (
    Rule("confirm_push", MENTIONS_A_PUSH, mentions_git,
         "git push: the confirmation hook could not load its parser. Confirm before anything reaches the remote.",
         "git push: the confirmation hook could not read the branch and the remote. Confirm before anything reaches the remote."),
    Rule("commit_rules", CREATING_WORDS, mentions_git,
         "Gemba rule (commits): the hook could not load its parser. Confirm the commit message follows the commit rules.",
         "Gemba rule (commits): the hook could not check this commit. Confirm the commit message follows the commit rules."),
    Rule("branch_rules", BRANCH_CREATING, mentions_git,
         "Gemba rule (branches): the branch hook could not load its parser. Confirm that the branch "
         "is named <type>/<KEY>-<slug> and starts from develop.",
         "Gemba rule (branches): the branch hook could not read this command. Confirm that the branch is named "
         "<type>/<KEY>-<slug> and starts from develop."),
    Rule("history_rules", OPERATION_WORDS, mentions_git,
         "Gemba rule (history): the hook could not load its parser. Confirm that this command does not rewrite or lose history.",
         "Gemba rule (history): the hook could not read the repository. "
         "Confirm that this command does not rewrite or lose history."),
    Rule("integration_rules", INTEGRATION_RELEVANT, _git_or_pr_merge, UNREADABLE_INTEGRATION, UNREADABLE_INTEGRATION),
)}
