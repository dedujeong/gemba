"""Make sure a .gitignore ignores a pattern.

Usage: python3 ensure_ignored.py <.gitignore> "<pattern>" "<comment>"

If a line of the file already is the pattern, with or without a final slash, nothing changes.
Otherwise the file gets a section like the ones it already has: a blank line after the last
one, a comment that says what is ignored, and the pattern. A missing file is created with only
the section. The rest of the file stays as it was, except that it now ends with a newline.
"""
import os
import sys


def ensure_ignored(content, pattern, comment):
    """The content of the .gitignore with the pattern in it."""
    if any(line.strip().rstrip("/") == pattern.rstrip("/") for line in content.splitlines()):
        return content
    text = content
    if text and not text.endswith("\n"):
        text += "\n"
    if text and not text.endswith("\n\n"):
        text += "\n"
    return text + "# " + comment + "\n" + pattern + "\n"


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    path, pattern, comment = sys.argv[1:]
    content = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8", newline="") as f:
            content = f.read()
    updated = ensure_ignored(content, pattern, comment)
    if updated != content or not os.path.exists(path):
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(updated)
