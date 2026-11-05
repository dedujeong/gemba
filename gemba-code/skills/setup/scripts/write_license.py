"""Write the license files of a project.

Usage: python3 write_license.py <repository root> <Apache-2.0|MIT|none> --holder <name>
           --year <yyyy> --product <name> [--holder-url <url>] [--source-dir <dir>]

The LICENSE is the official text, fetched when the script runs: the plugin keeps no copy of
any license. For MIT the holder and the year go inside the LICENSE. For none nothing is written.
A LICENSE that already exists is left as it is. If the official text cannot be read, nothing
is written and the error says which text is missing and where it comes from.

--source-dir reads <license>.txt from a folder instead of the network; it is meant for tests.
"""
import argparse
import os
import sys
import urllib.request

SOURCES = {
    "Apache-2.0": "https://www.apache.org/licenses/LICENSE-2.0.txt",
    "MIT": "https://raw.githubusercontent.com/spdx/license-list-data/main/text/MIT.txt",
}
LICENSE_FILES = ("LICENSE", "LICENSE.md", "LICENSE.txt")


class TextUnavailable(Exception):
    pass


def official_text(license_name, source_dir=None):
    """The official text of the license, read now."""
    url = SOURCES[license_name]
    try:
        if source_dir:
            with open(os.path.join(source_dir, license_name + ".txt"), encoding="utf-8", newline="") as f:
                return f.read()
        with urllib.request.urlopen(url, timeout=20) as response:
            return response.read().decode("utf-8")
    except (OSError, ValueError) as error:
        raise TextUnavailable(
            f"could not read the official text of {license_name} from {url} ({error}); nothing was written."
        )


def license_text(license_name, holder, year, source_dir=None):
    text = official_text(license_name, source_dir)
    if license_name == "MIT":
        text = text.replace("<year>", year).replace("<copyright holders>", holder)
    return text


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root")
    parser.add_argument("license", choices=["Apache-2.0", "MIT", "none"])
    parser.add_argument("--holder", required=True)
    parser.add_argument("--year", required=True)
    parser.add_argument("--product", required=True)
    parser.add_argument("--holder-url")
    parser.add_argument("--source-dir")
    args = parser.parse_args(argv)

    if args.license == "none":
        print("No license chosen: LICENSE and NOTICE were not written.")
        return 0

    existing = [name for name in LICENSE_FILES if os.path.exists(os.path.join(args.root, name))]
    if existing:
        print(f"{existing[0]} already exists: left as it is.")
        return 0

    try:
        text = license_text(args.license, args.holder, args.year, args.source_dir)
    except TextUnavailable as error:
        print(error, file=sys.stderr)
        return 2
    with open(os.path.join(args.root, "LICENSE"), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"LICENSE written: {args.license}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
