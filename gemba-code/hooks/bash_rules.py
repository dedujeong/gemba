#!/usr/bin/env python3
"""PreToolUse hook: every Bash rule of the plugin, run from one process.

Reads the hook event from stdin and asks each rule script (`confirm_push`, `commit_rules`, `branch_rules`,
`history_rules`, `integration_rules`) for its `decide(event)`: `(decision, reason)` or None. They run in this one
process, so the command is tokenized once and every repository read (`git_commands` caches them per process) is shared.
When several rules decide, `deny` wins over `ask` and the reasons are joined in one answer; when none decides it
prints nothing. It never allows. Each rule script still runs on its own.

It fails closed. A rule that crashes (or cannot be imported) asks, with its generic reason, for a command it would
check (its pattern in `fallback_words.RULES`), and the other rules still run. When `git_commands` does not import, it
asks for any command any rule would check.
"""
import importlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # the rules are imported from this folder
import fallback_words  # before git_commands: it still loads when the parser does not

RULES = ("confirm_push", "commit_rules", "branch_rules", "history_rules", "integration_rules")


def combine(answers):
    """The one answer of the decisions of several rules: `deny` when any denies, else `ask`; every reason, once, in order."""
    if not answers:
        return None
    reasons = list(dict.fromkeys(reason for _, reason in answers))
    return ("deny" if any(decision == "deny" for decision, _ in answers) else "ask"), "\n".join(reasons)


def decide(event):
    """The combined `(decision, reason)` of every rule for the event, or None."""
    command = event.get("tool_input", {}).get("command", "")
    rules = [fallback_words.RULES[name] for name in RULES if fallback_words.RULES[name].gate(command)]
    if not rules:
        return None  # no git, no gh pr merge: skip the import and the parsing
    answers = []
    try:
        import git_commands
    except Exception:  # a crash here would not block: ask for any command a rule would check
        return combine([("ask", rule.unloaded) for rule in rules if fallback_words.relevant(command, rule.pattern)])
    for rule in rules:
        try:
            module = importlib.import_module(rule.name)
            module.git_commands = git_commands
            found = module.decide(event)
        except Exception:  # a crash exits non-zero, which does not block: ask for what this rule checks
            found = ("ask", rule.broken) if fallback_words.relevant(command, rule.pattern) else None
        if found:
            answers.append(found)
    return combine(answers)


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") != "Bash":
        return
    try:
        found = decide(event)
    except Exception:  # the dispatcher itself: ask for any command any rule would check
        command = event.get("tool_input", {}).get("command", "")
        found = combine([("ask", rule.unloaded) for rule in fallback_words.RULES.values()
                         if rule.gate(command) and fallback_words.relevant(command, rule.pattern)])
    if found:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": found[0], "permissionDecisionReason": found[1]}}))


if __name__ == "__main__":
    main()
