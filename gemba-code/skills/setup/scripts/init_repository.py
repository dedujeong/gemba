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


NO_IDENTITY = ("git has no identity for the initial commit: ask the person for the name and email, set them with "
               "git config user.name and git config user.email, and run this again")
NO_MAIN = "the repository has commits but no main branch; ask the person what to do, no branch is renamed"


class Failed(Exception):
    pass


def step(folder, failure, *args):
    """Run one git command; a failure stops the preparation with this message and git's error."""
    result = git(folder, *args)
    if result.returncode != 0:
        raise Failed(f"{failure}: {result.stderr.strip()}" if result.stderr.strip() else failure)


def prepare(folder):
    """(exit code, message) after making sure the folder's repository has `main` and `develop`."""
    done = []
    try:
        if git(folder, "rev-parse", "--git-dir").returncode != 0:
            step(folder, "git init failed", "init", "--quiet", "--initial-branch=main")
            done.append("created the repository")
        if not has(folder, "HEAD"):
            step(folder, "could not point the new repository to main", "symbolic-ref", "HEAD", "refs/heads/main")
            if not all(git(folder, "var", ident).returncode == 0 for ident in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT")):
                return 1, NO_IDENTITY
            step(folder, "git commit failed", "commit", "--quiet", "--allow-empty", "-m", "initial commit")
            done.append("made the empty initial commit on main")
        for branch in ("main", "develop"):
            if not has(folder, f"refs/heads/{branch}") and has(folder, f"refs/remotes/origin/{branch}"):
                step(folder, f"{branch} could not be created from origin/{branch}",
                     "branch", "--track", branch, f"origin/{branch}")
                done.append(f"created {branch} from origin/{branch}")
        if not has(folder, "refs/heads/main"):
            return 1, NO_MAIN
        if not has(folder, "refs/heads/develop"):
            step(folder, "develop could not be created from main", "branch", "develop", "main")
            done.append("created develop from main")
    except Failed as failure:
        return 1, "; ".join([*done, str(failure)])
    return 0, "; ".join(done) if done else "main and develop already exist; nothing changed"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    code, message = prepare(sys.argv[1])
    print(message)
    sys.exit(code)
