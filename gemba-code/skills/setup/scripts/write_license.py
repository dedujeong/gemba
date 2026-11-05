"""Write the license files of a project.

Usage: python3 write_license.py <repository root> <Apache-2.0|MIT|none> --holder <name>
           --year <yyyy> --product <name> [--holder-url <url>] [--source-dir <dir>]

The LICENSE is the official text, fetched when the script runs: the plugin keeps no copy of
any license. For MIT the holder and the year go inside the LICENSE. For Apache-2.0 the NOTICE
is written from assets/notice.md, unless there is one. For none nothing is written. A LICENSE
that already exists is left as it is, and then no NOTICE is written. If the official text cannot be read, nothing
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
NOTICE_TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "notice.md")


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


def notice_text(product, year, holder, holder_url):
    """The NOTICE, filled from the template of setup."""
    with open(NOTICE_TEMPLATE, encoding="utf-8", newline="") as f:
        text = f.read()
    if holder_url:
        text = text.replace("<holder URL>", holder_url)
    else:
        text = text.replace(" (<holder URL>)", "")
    return text.replace("<Product name>", product).replace("<year>", year).replace("<holder>", holder)


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
    if args.license == "Apache-2.0":
        notice = os.path.join(args.root, "NOTICE")
        if os.path.exists(notice):
            print("NOTICE already exists: left as it is.")
        else:
            with open(notice, "w", encoding="utf-8", newline="") as f:
                f.write(notice_text(args.product, args.year, args.holder, args.holder_url))
            print("NOTICE written.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
