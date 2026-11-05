"""Write the base .gitignore of a project that uses Gemba Code.

Usage: python3 write_gitignore.py <.gitignore>

The base is three groups, each with a comment in English: the personal Claude Code files, the
worktrees of the Spikes and the session handoffs. A group is added only for the entries the file
does not have yet, so the lines already there are neither deleted nor reordered. A missing file
is created with the whole base.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "session-close", "scripts"))

from ensure_ignored import ensure_ignored  # noqa: E402

GROUPS = [
    ("Personal Claude Code files, one set per developer", [".claude/settings.local.json", "CLAUDE.local.md"]),
    ("Claude Code worktrees, used for Spikes", [".claude/worktrees/"]),
    ("Session handoffs written by session-close, one per session", [".gemba/sessions/"]),
]


def write_gitignore(content):
    """The content of the .gitignore with every group of the base in it."""
    for comment, patterns in GROUPS:
        commented = False
        for pattern in patterns:
            updated = ensure_ignored(content, pattern, comment)
            if updated == content:
                continue
            if commented:
                # The group already has its comment: the entry goes right under the previous one.
                updated = content + pattern + "\n"
            content = updated
            commented = True
    return content


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    content = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8", newline="") as f:
            content = f.read()
    updated = write_gitignore(content)
    if updated != content or not os.path.exists(path):
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(updated)
