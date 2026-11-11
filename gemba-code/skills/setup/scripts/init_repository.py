"""Prepare the repository of a project that uses Gemba Code: `main` and `develop`.

Usage: python3 init_repository.py <project folder>

- A folder that is not a repository, or a repository with no commit yet, gets `git init -b main`, an
  empty `initial commit` on `main` and `develop` created from `main`. It stays on `main`, and the
  files already in the folder are left uncommitted.
- A repository with `main` and no `develop` gets `develop` created from `main`.
- A repository with `main` and `develop` is not changed.
- A clone whose `main` or `develop` exists only as `origin/main` or `origin/develop` gets the local
  branch created from the remote one.
- A repository with commits but no `main` is not changed either: no branch is ever renamed. The
  script exits with 1 and says that `main` is missing, so setup asks the person.
- Without a git identity the initial commit cannot be made: the script exits with 1 and says so, so
  setup asks for the name and email, sets them in the repository and runs it again.

It prints what it did, one line, and only ever runs `git` with fixed arguments.
"""
import subprocess
import sys


def git(folder, *args):
    return subprocess.run(["git", "-C", folder, *args], capture_output=True, text=True)


def has(folder, ref):
    return git(folder, "rev-parse", "--verify", "--quiet", ref).returncode == 0


def prepare(folder):
    """(exit code, message) after making sure the folder's repository has `main` and `develop`."""
    if git(folder, "rev-parse", "--git-dir").returncode != 0:
        result = git(folder, "init", "--quiet", "--initial-branch=main")
        if result.returncode != 0:
            return 1, f"git init failed: {result.stderr.strip()}"
        created = "created the repository, "
    else:
        created = ""
    if not has(folder, "HEAD"):
        if git(folder, "symbolic-ref", "HEAD", "refs/heads/main").returncode != 0:
            return 1, "could not point the new repository to main"
        if git(folder, "var", "GIT_AUTHOR_IDENT").returncode != 0 or git(folder, "var", "GIT_COMMITTER_IDENT").returncode != 0:
            return 1, ("git has no identity for the initial commit: ask the person for the name and email, set them "
                       "with git config user.name and git config user.email, and run this again")
        result = git(folder, "commit", "--quiet", "--allow-empty", "-m", "initial commit")
        if result.returncode != 0:
            return 1, f"git commit failed: {result.stderr.strip()}"
        result = git(folder, "branch", "develop", "main")
        if result.returncode != 0:
            return 1, f"made the initial commit on main, but develop could not be created: {result.stderr.strip()}"
        return 0, f"{created}made the empty initial commit on main and created develop from main"
    for branch in ("main", "develop"):
        if not has(folder, f"refs/heads/{branch}") and has(folder, f"refs/remotes/origin/{branch}"):
            result = git(folder, "branch", "--track", branch, f"origin/{branch}")
            if result.returncode != 0:
                return 1, f"{branch} could not be created from origin/{branch}: {result.stderr.strip()}"
    if not has(folder, "refs/heads/main"):
        return 1, "the repository has commits but no main branch; ask the person what to do, no branch is renamed"
    if not has(folder, "refs/heads/develop"):
        result = git(folder, "branch", "develop", "main")
        if result.returncode != 0:
            return 1, f"git branch failed: {result.stderr.strip()}"
        return 0, "created develop from main"
    return 0, "main and develop already exist; nothing changed"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    code, message = prepare(sys.argv[1])
    print(message)
    sys.exit(code)
