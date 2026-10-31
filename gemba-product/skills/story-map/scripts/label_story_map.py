"""Write the patch that changes or adds a row label of an existing story map board.

Usage: python3 label_story_map.py board.svg --label NAME [--description TEXT] [--top Y]
       python3 label_story_map.py board.svg --add NAME --description TEXT --top Y

Accepts the SVG exactly as getConfluenceContent returns it, including the line-number
prefixes, and finds the rows like read_story_map.py does.

--label prints a replace_svg for the label NAME: the whole <text>, as the API needs it.
Its top is level with the top of the first row of stickies of that row, read from the board
as it is now, so a board arranged by hand is respected; --top overrides it, and a row
without stickies needs it. Without --description the label keeps its text and only realigns.
--add prints an insert_svg for the label of a new release (or the Later row) with its top
at Y, after the last element of the board.

Confluence reads a free text's y as its vertical center, so the patch carries
top + height / 2 (see label_svg). The patch touches only the label: send it with the
board you just read as context.content, so nothing else moves.
"""
import argparse
import os
import re
import sys
from html import unescape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I does not add it

from build_story_map import label_svg
from read_story_map import attrs, read_bands


def scan_labels(svg):
    """The free texts of the board with a bold 27px title, in board order, with the lines they occupy."""
    lines = [(int(m.group(1)), m.group(2)) for m in re.finditer(r"(?m)^(\d+)\s*(.*)$", svg)]
    found, i = [], 0
    while i < len(lines):
        if lines[i][1].lstrip().startswith("<text"):
            j = i
            while "</text>" not in lines[j][1]:
                j += 1
            body = " ".join(t.strip() for _, t in lines[i:j + 1])
            tag = attrs(re.match(r"<text\b[^>]*>", body).group(0))
            tspans = re.findall(r'<tspan([^>]*)>([^<]*)</tspan>', body)
            title = next((k for k, (a, _) in enumerate(tspans) if 'font-weight="bold"' in a and "27px" in a), None)
            if tag.get("data-type") == "text" and title is not None:
                found.append({
                    "name": unescape(tspans[title][1]).strip(), "attrs": tag,
                    "description": unescape(tspans[title + 1][1]) if title + 1 < len(tspans) else "",
                    "from": lines[i][0], "to": lines[j][0],
                })
            i = j
        i += 1
    return found, lines


def row_labels(svg):
    """The labels of the rows (not the board header), by name."""
    labels, bands = read_bands(svg)
    found, lines = scan_labels(svg)
    rows = {}
    for l in labels:
        same = [f for f in found if f["name"] == l["name"]]
        if len(same) != 1:
            raise ValueError(f'More than one row is labeled "{l["name"]}"; rename one of them first' if same
                             else f'The label "{l["name"]}" could not be read from the board; read it again')
        rows[l["name"]] = same[0]
    return rows, bands, lines


def replace_patch(svg, name, description=None, top=None):
    rows, bands, _ = row_labels(svg)
    if name not in rows:
        raise ValueError(f'No row labeled "{name}" on the board; the labels are: {", ".join(rows)}')
    label = rows[name]
    if top is None:
        if not bands[name]:
            raise ValueError(f'"{name}" has no stickies to align with; give its top')
        top = min(s["y"] for s in bands[name])
    a = label["attrs"]
    text = label_svg(a["id"], top, name, label["description"] if description is None else description,
                     width=a.get("width", "344.12"), scale=float(a.get("font-scale", 1)), x=a["x"])
    return f'<replace_svg from="{label["from"]}" to="{label["to"]}">\n{text}\n</replace_svg>'


def insert_patch(svg, name, description, top):
    rows, _, lines = row_labels(svg)
    if name in rows:
        raise ValueError(f'"{name}" is already on the board; use --label to change it')
    closing = max((n for n, t in lines if t.strip() == "</svg>"), default=None)
    if closing is None:
        raise ValueError("The board has no closing </svg> line; read it again")
    first = next(iter(rows.values()))["attrs"]
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    text = label_svg(f"label-added-{slug}", top, name, description, width=first.get("width", "344.12"), x=first["x"])
    return f'<insert_svg line="{closing}">\n{text}\n</insert_svg>'


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Write the patch that changes or adds a row label.")
    parser.add_argument("board", help="the board SVG as getConfluenceContent returns it")
    what = parser.add_mutually_exclusive_group(required=True)
    what.add_argument("--label", metavar="NAME", help="change the label of this row")
    what.add_argument("--add", metavar="NAME", help="add the label of a new release")
    parser.add_argument("--description", help="the text under the title")
    parser.add_argument("--top", type=float, help="the top of the label, when it is not the first row of the row")
    args = parser.parse_args()
    if args.add and args.top is None:
        parser.error("--add needs --top, the top of the row of the new release")
    svg = open(args.board, encoding="utf-8").read()
    try:
        if args.add:
            print(insert_patch(svg, args.add, args.description or "", args.top))
        else:
            print(replace_patch(svg, args.label, args.description, args.top))
    except ValueError as error:
        parser.error(str(error))
