"""Propose the name of the next fix version of a product.

Usage: python3 next_version.py "<Product>" versions.json [--fix]

versions.json is what getJiraProjectVersions returns: the versions as a list, or an object
with the list under "values". Only published, not archived versions named exactly
"<Product> vX.Y.Z" count; the highest one by number is the base.

By default it proposes the next release, which raises the minor number: X.(Y+1).0.
With --fix it proposes a bug fix on the published version, which raises the third: X.Y.(Z+1).
The major number never changes on its own: it stays the base's until the maintainer says so.
A product with no published version starts at v0.1.0.
"""
import json
import re
import sys


def published(product, versions):
    """The (major, minor, patch) of each published, not archived version of the product."""
    pattern = re.compile(r"^%s v(\d+)\.(\d+)\.(\d+)$" % re.escape(product))
    found = []
    for item in versions:
        match = pattern.match(item.get("name", ""))
        if match and item.get("released") and not item.get("archived"):
            found.append(tuple(int(part) for part in match.groups()))
    return found


def next_name(product, versions, fix=False):
    found = published(product, versions)
    if not found:
        return "%s v0.1.0" % product
    major, minor, patch = max(found)
    if fix:
        return "%s v%d.%d.%d" % (product, major, minor, patch + 1)
    return "%s v%d.%d.0" % (product, major, minor + 1)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    with open(args[1], encoding="utf-8") as f:
        data = json.load(f)
    versions = data["values"] if isinstance(data, dict) else data
    print(next_name(args[0], versions, fix="--fix" in sys.argv))
