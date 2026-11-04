"""Write the patch that replaces each story of the current release of a story map board with the card of its issue.

Usage: python3 card_story_map.py board.svg keys.json --site https://<site>

Accepts the SVG exactly as getConfluenceContent returns it, including the line-number prefixes,
and finds the rows the same way read_story_map.py does. keys.json maps the text of each story of the
current release to the key of its issue: {"Save a date per customer": "GEMBA-1"}. --site is the URL of the
Jira site, the one the card links to.

Each story that has a key is replaced where it stands: its rectangle becomes an issue card at the same x
and y with the size of a Jira card, and its text is deleted. The patch is one delete_svg and one replace_svg
per story, built against the line numbers of the SVG it was given, so it is applied right after reading and
never to a later reading. A key for a text that is not a story of the current release stops everything and
prints nothing.

Confluence stores every card gray (#f0f1f2): the fill of a card is ignored when it is written and cannot be
changed afterwards, so the patch already says gray. The id of a card is a new one; read the board again to
learn it.

The board in Confluence is the only source; nothing is copied anywhere.
"""
import argparse
import json
import os
import re
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I does not add it

from build_story_map import GRAY, STORY_H, STORY_W
from read_story_map import OPEN_FILLS, attrs, current, parse, read_bands


def elements(svg):
    """{id: {"rect": line, "from": first line of its text, "to": last line}} for each rect of the board."""
    found, text = {}, None
    for line in svg.splitlines():
        m = re.match(r"(\d+)(.*)$", line)
        if not m:
            continue
        number, body = int(m.group(1)), m.group(2)
        rect = re.search(r"<rect\b[^>]*>", body)
        if rect and "id" in attrs(rect.group(0)):
            found.setdefault(attrs(rect.group(0))["id"], {})["rect"] = number
        tag = re.search(r"<text\b[^>]*>", body)
        if tag and "belongs-to" in attrs(tag.group(0)):
            text = (attrs(tag.group(0))["belongs-to"], number)
        if text and "</text>" in body:
            found.setdefault(text[0], {}).update({"from": text[1], "to": number})
            text = None
    return found


def card_svg(key, x, y, site):
    return (f'<rect width="{STORY_W:g}" height="{STORY_H:g}" id="card-{escape(key)}" data-type="issue" fill="{GRAY}" '
            f'x="{round(x, 2)}" y="{round(y, 2)}" data-smartlink-kind="block" '
            f'data-smartlink-url="{escape(site.rstrip("/"))}/browse/{escape(key)}" '
            'data-smartlink-supported-views="block" data-smartlink-supports-preview="false"></rect>')


def card_patch(svg, keys, site):
    board = parse(svg)
    release = current(board)
    if release is None:
        raise ValueError("The board has no current release: there is no story to replace with a card")
    _, bands = read_bands(svg)
    stories = [s for s in bands[release["name"]] if s["fill"].lower() not in OPEN_FILLS and not s["key"]]
    by_text = {}
    for s in stories:
        by_text.setdefault(s["text"], []).append(s)
    unknown = [t for t in keys if t not in by_text]
    if unknown:
        raise ValueError(f'Not a story of the current release ({release["name"]}): ' + ", ".join(unknown))
    twice = [t for t in keys if len(by_text[t]) > 1]
    if twice:
        raise ValueError("The text of more than one story: " + ", ".join(twice))
    lines = elements(svg)
    deletes, replaces = [], []
    for s in sorted(stories, key=lambda s: lines[s["id"]]["rect"]):
        key = keys.get(s["text"])
        if key is None:
            continue
        el = lines[s["id"]]
        if "from" in el:
            deletes.append(f'<delete_svg from="{el["from"]}" to="{el["to"]}"/>')
        replaces.append(f'<replace_svg from="{el["rect"]}" to="{el["rect"]}">\n{card_svg(key, s["x"], s["y"], site)}\n</replace_svg>')
    return "\n".join(deletes + replaces)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Write the patch that replaces each story of the current release with its issue card.")
    parser.add_argument("board", help="the board SVG as getConfluenceContent returns it")
    parser.add_argument("keys", help='JSON {"story text": "KEY"} for the stories of the current release')
    parser.add_argument("--site", required=True, help="the URL of the Jira site, for example https://example.atlassian.net")
    args = parser.parse_args()
    try:
        keys = json.load(open(args.keys, encoding="utf-8"))
        print(card_patch(open(args.board, encoding="utf-8").read(), keys, args.site))
    except ValueError as error:
        parser.error(str(error))
