"""Write the patch that moves stories of a story map board to another release (or to Later).

Usage: python3 move_story_map.py board.svg --story ID [--story ID ...] --to NAME

Accepts the SVG exactly as getConfluenceContent returns it, like read_story_map.py, and
finds the rows the same way. ID is the id of a sticky, as read_story_map.py --json lists
it; NAME is the label of the target row.

Each story keeps its column (its task) and takes the next free row of that column in the
target: right below the stories already there, or at the top of the row when the cell is
empty (a row without stickies takes the top of its label). Positions are read from the
board as it is now, so a board arranged by hand is respected.

If the stack gets deeper and would reach the next row, the rows below move down by what is
missing, so the spacing the builder gives is kept: their stickies and their labels move
together. Nothing above the target moves, and the rows the stories leave are not closed up.

The output is one update_elements_svg per sticky (x and y; its text follows it, tested on
a real board), plus a replace_svg for each label that moves. It does not change colors:
read the board again afterwards and run recolor_story_map.py, so each story takes the color
of its new row.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I does not add it

from build_story_map import CARD_W, RELEASE_GAP, ROW_STEP
from label_story_map import replace_patch
from read_story_map import BACKBONE, read_bands


def move_patch(svg, ids, target):
    labels, bands = read_bands(svg)
    names = [l["name"] for l in labels if l["name"] not in BACKBONE]
    if target not in names:
        raise ValueError(f'No release labeled "{target}" on the board; the labels are: {", ".join(names)}')
    by_id = {s["id"]: (name, s) for name, stickies in bands.items() for s in stickies}
    if len(set(ids)) != len(ids):
        raise ValueError("A sticky is listed twice; list each story once")
    for sid in ids:
        if sid not in by_id:
            raise ValueError(f'No sticky with id "{sid}" on the board')
        name, story = by_id[sid]
        if name in BACKBONE:
            raise ValueError(f'"{story["text"]}" is in {name}, not in a release; only stories move')
        if name == target:
            raise ValueError(f'"{story["text"]}" is already in {target}')

    def row_top(label):
        """Where a row starts: its first row of stickies, or its label when it has none. Stories on the move do not count."""
        return min((s["y"] for s in bands[label["name"]] if s["id"] not in ids), default=label["y"])

    target_label = next(l for l in labels if l["name"] == target)
    row = list(bands[target])
    placed = {}
    for sid in ids:
        story = by_id[sid][1]
        stack = [s["y"] for s in row if abs(s["x"] - story["x"]) < CARD_W]  # any sticky it would overlap
        y = round(max(stack) + ROW_STEP, 2) if stack else row_top(target_label)
        placed[sid] = (story["x"], y)
        row.append({"id": sid, "x": story["x"], "y": y})

    below = labels[labels.index(target_label) + 1:]
    shift = max(0, round(max(s["y"] for s in row) + RELEASE_GAP - row_top(below[0]), 2)) if below else 0
    below = below if shift else []

    parts = []
    for l in below:
        parts.append(replace_patch(svg, l["name"], top=round(row_top(l) + shift, 2)))
    for sid, (x, y) in placed.items():
        parts.append(f'<update_elements_svg ids="{sid}">\n<attr x="{x}" y="{y}"/>\n</update_elements_svg>')
    for l in below:
        for s in sorted(bands[l["name"]], key=lambda s: (s["y"], s["x"])):
            if s["id"] not in placed:
                parts.append(f'<update_elements_svg ids="{s["id"]}">\n<attr x="{s["x"]}" y="{round(s["y"] + shift, 2)}"/>\n</update_elements_svg>')
    return "\n".join(parts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Write the patch that moves stories to another release.")
    parser.add_argument("board", help="the board SVG as getConfluenceContent returns it")
    parser.add_argument("--story", action="append", required=True, metavar="ID", help="the id of a sticky to move; repeat for each one")
    parser.add_argument("--to", required=True, metavar="NAME", help="the label of the target row")
    args = parser.parse_args()
    try:
        print(move_patch(open(args.board, encoding="utf-8").read(), args.story, args.to))
    except ValueError as error:
        parser.error(str(error))
