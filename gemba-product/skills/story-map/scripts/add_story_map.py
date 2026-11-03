"""Write the patch that adds a story to a story map board.

Usage: python3 add_story_map.py board.svg --to NAME --task TASK --text TEXT [--traces WHERE]

Accepts the SVG exactly as getConfluenceContent returns it, like read_story_map.py, and
finds the rows and the columns the same way. NAME is the label of the row the story goes
to; TASK is the text of the task whose column it belongs to, as the board writes it.

The story takes the next free row of that column in its release: right below the stories
already there, or the top of the row when the cell is empty. Positions are read from the
board as it is now, so a board arranged by hand is respected, and if the row gets deeper
the rows below move down with their labels, as move_story_map.py does.

Its color is the one of the row it lands in, read from the board: green in the current
release, orange in the next one, light orange later and in the Later row. A delivered
release takes no story. A story of the current release needs --traces, the part of the
brief it serves, the same cut build_story_map.py makes.

The output is a replace_svg per label that moves, the insert_svg with the new sticky and
its text, and an update_elements_svg per sticky that moves. Confluence gives the inserted
sticky a new id: read the board again afterwards to report what it says.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I does not add it

from build_story_map import release_fills, sticky_svg
from move_story_map import row_top, shift_patch, stack_y
from read_story_map import BACKBONE, current, parse, read_bands


def end_line(svg):
    """The line of </svg>: inserting there leaves the new sticky last and the SVG valid."""
    for line in reversed(svg.strip().splitlines()):
        if "</svg>" in line:
            number = re.match(r"\s*(\d+)", line)
            if number:
                return int(number.group(1))
            break
    raise ValueError("The board has no numbered </svg> line; send the SVG as getConfluenceContent returns it")


def free_id(svg):
    """An id no element of the board uses; Confluence replaces it with one of its own."""
    sid, n = "new-story", 1
    while f'id="{sid}"' in svg:
        n += 1
        sid = f"new-story-{n}"
    return sid


def add_patch(svg, target, task, text, traces=""):
    labels, bands = read_bands(svg)
    names = [l["name"] for l in labels if l["name"] not in BACKBONE]
    if target not in names:
        raise ValueError(f'No release labeled "{target}" on the board; the labels are: {", ".join(names)}')
    tasks = sorted(bands.get("Tasks", []), key=lambda s: s["x"])
    column = next((s for s in tasks if s["text"] == task), None)
    if column is None:
        raise ValueError(f'No task "{task}" on the board; the tasks are: {", ".join(s["text"] for s in tasks)}')

    board = parse(svg)
    index = next(i for i, r in enumerate(board["releases"]) if r["name"] == target)
    if board["releases"][index]["delivered"]:
        raise ValueError(f'"{target}" is delivered: a release that shipped takes no story')
    being = current(board)
    if being and being["name"] == target and not traces.strip():
        raise ValueError(f'"{target}" is the current release: story "{text}" needs --traces '
                         "to a problem, the primary job or a Quality bar condition")
    fill = release_fills([{"name": r["name"], "released": r["delivered"]} for r in board["releases"]])[index]

    target_label = next(l for l in labels if l["name"] == target)
    sid = free_id(svg)
    row = list(bands[target])
    y = stack_y(row, column["x"], row_top(bands, target_label))
    row.append({"id": sid, "x": column["x"], "y": y})

    label_ops, sticky_ops = shift_patch(svg, labels, bands, target_label, max(s["y"] for s in row))
    sticky = "\n".join(sticky_svg(sid, column["x"], y, fill, text))
    return "\n".join(label_ops + [f'<insert_svg line="{end_line(svg)}">\n{sticky}\n</insert_svg>'] + sticky_ops)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Write the patch that adds a story to a release.")
    parser.add_argument("board", help="the board SVG as getConfluenceContent returns it")
    parser.add_argument("--to", required=True, metavar="NAME", help="the label of the row the story goes to")
    parser.add_argument("--task", required=True, metavar="TASK", help="the text of the task whose column it belongs to")
    parser.add_argument("--text", required=True, metavar="TEXT", help="the story, in one short sentence")
    parser.add_argument("--traces", default="", metavar="WHERE", help="the part of the brief it serves; required in the current release")
    args = parser.parse_args()
    try:
        print(add_patch(open(args.board, encoding="utf-8").read(), args.to, args.task, args.text, args.traces))
    except ValueError as error:
        parser.error(str(error))
