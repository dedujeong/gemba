"""Put each issue key on its story sticky of the current release of a Story Map whiteboard.

Usage: python3 write_keys.py board.svg keys.json [--check]

board.svg is the SVG exactly as getConfluenceContent returns it (content_format: svg),
including the line-number prefixes. keys.json maps the text of each story sticky of the
current release to the key of its issue: {"Save the vehicle": "TALLER-12"}.

Without --check it prints a patch for updateConfluenceContent: one replace_svg per story
sticky, whose text keeps its lines and gains the key as a last line, the same way the board
stores a second line of a sticky. The patch is built against the line numbers of the SVG it
was given, so it is applied right after reading and never to a later reading. Only the stickies
of the current release's stories are written: activities, tasks, open questions (red) and other
releases are never touched, and a sticky that already ends with its key is skipped. A story
without a key in keys.json is reported on stderr; a key for a text that is not a story of the
current release stops everything and prints nothing.

With --check it reads the board and prints JSON for what to report after writing: for each
story of the current release, the key its sticky carries (found) and whether it is the one in
keys.json (ok). The response of a write is stale, so the report comes only from reading the board again.

The board in Confluence is the only source; nothing is copied anywhere.
"""
import json
import re
import sys
from html import escape, unescape

from read_release import OPEN_FILLS, attrs, current_row, read_bands

KEY = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")
KEY_LINE = '<tspan font-size="15.47px" dy="1">{}</tspan>'


def story_stickies(svg):
    """The stickies of the current release's stories, as read_release.py takes them."""
    labels, bands = read_bands(svg)
    row = current_row(labels, bands)
    if row is None:
        raise ValueError("Every release of the board is gray: there is no release to write keys on")
    return row["name"], [s for s in bands[row["name"]] if s["fill"] not in OPEN_FILLS]


def text_elements(svg):
    """{sticky id: {"from", "to", "lines"}} for the text element of each sticky, with the numbers of its lines."""
    lines = [re.match(r"(\d+)(.*)$", l) for l in svg.splitlines()]
    lines = [(int(m.group(1)), m.group(2)) for m in lines if m]
    found, start = {}, None
    for number, body in lines:
        if start is None:
            m = re.search(r"<text\b[^>]*>", body)
            if m and "belongs-to" in m.group(0):
                start = (number, attrs(m.group(0))["belongs-to"], [body])
        else:
            start[2].append(body)
        if start is not None and "</text>" in body:
            found[start[1]] = {"from": start[0], "to": number, "lines": start[2]}
            start = None
    return found


def carried_key(element):
    """The key a sticky ends with: its last line when that line is only a key."""
    tspans = re.findall(r"<tspan\b[^>]*>([^<]*)</tspan>", "\n".join(element["lines"]))
    last = unescape(tspans[-1]).strip() if tspans else ""
    return last if KEY.match(last) else None


def name_of(sticky, element):
    """The story name: the text of the sticky without the key it carries, which the readers join to it."""
    found = carried_key(element)
    if found and sticky["text"].endswith(" " + found):
        return sticky["text"][: -len(found)].rstrip()
    return sticky["text"]


def check(keys, stories, elements):
    report = []
    for s in stories:
        el = elements[s["id"]]
        found, name = carried_key(el), name_of(s, el)
        report.append({"text": name, "expected": keys.get(name), "found": found, "ok": found is not None and found == keys.get(name)})
    return report


def patch(keys, stories, elements):
    by_text = {}
    for s in stories:
        by_text.setdefault(name_of(s, elements[s["id"]]), []).append(s)
    unknown = [t for t in keys if t not in by_text]
    if unknown:
        raise ValueError("Not a story of the current release: " + ", ".join(unknown))
    twice = [t for t in keys if len(by_text[t]) > 1]
    if twice:
        raise ValueError("The text of more than one sticky: " + ", ".join(twice))
    ops, without = [], []
    for s in sorted(stories, key=lambda s: elements[s["id"]]["from"]):
        name = name_of(s, elements[s["id"]])
        key = keys.get(name)
        if key is None:
            without.append(name)
            continue
        el = elements[s["id"]]
        if carried_key(el) == key:
            continue
        body = el["lines"][:-1] + ["    " + KEY_LINE.format(escape(key))] + [el["lines"][-1]]
        ops.append(f'<replace_svg from="{el["from"]}" to="{el["to"]}">\n' + "\n".join(body) + "\n</replace_svg>")
    return ops, without


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    try:
        svg = open(args[0], encoding="utf-8").read()
        keys = json.load(open(args[1], encoding="utf-8"))
        release, stories = story_stickies(svg)
        elements = text_elements(svg)
        if "--check" in sys.argv:
            print(json.dumps({"release": release, "stories": check(keys, stories, elements)}, ensure_ascii=False, indent=2))
        else:
            ops, without = patch(keys, stories, elements)
            if without:
                print("Without a key: " + ", ".join(without), file=sys.stderr)
            print("\n\n".join(ops))
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
