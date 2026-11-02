"""Print the path of the most recent session handoff.

Usage: python3 latest_handoff.py

Run it in the project. The handoffs are the .md files of .gemba/sessions in the main working
tree, which is the one that holds the git directory, so it also works from the worktree of a
Spike. Their names are the date and time of the session, so the last one by name is the most
recent. It prints nothing when there is no handoff.
"""
import glob
import os
import subprocess


def main_working_tree(folder):
    """The folder that holds the git directory, or the folder itself outside a repository."""
    result = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            cwd=folder, capture_output=True, text=True)
    if result.returncode != 0:
        return folder
    return os.path.dirname(result.stdout.strip())


def latest_handoff(folder):
    handoffs = sorted(glob.glob(os.path.join(main_working_tree(folder), ".gemba", "sessions", "*.md")))
    return handoffs[-1] if handoffs else None


if __name__ == "__main__":
    handoff = latest_handoff(os.getcwd())
    if handoff:
        print(handoff)
