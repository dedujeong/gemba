"""Write the patch that moves stories of a story map board to another release (or to Later).

Usage: python3 move_story_map.py board.svg --story ID [--story ID ...] --to NAME [--task TASK]

Accepts the SVG exactly as getConfluenceContent returns it, like read_story_map.py, and
finds the rows the same way. ID is the id of a sticky, as read_story_map.py --json lists
it; NAME is the label of the target row.

Each story keeps its column (its task) and takes the next free row of that column in the
target, unless --task TASK names another task of the board: then it takes the column of that
task, and the target may be the release it is already in (a story moves to another column of
its release). A card of an issue moves the same way as a sticky: only its x and y change, so
it keeps its issue. The story takes the next free row of the column: right below the stories already there, or at the top of the row when the cell is
empty (a row without stickies takes the top of its label). Positions are read from the
board as it is now, so a board arranged by hand is respected.

If the stack gets deeper and would reach the next row, the rows below move down by what is
missing, so the spacing the builder gives is kept: their stickies and their labels move
together. Nothing above the target moves, and the rows the stories leave are not closed up.

`row_top`, `stack_y` and `shift_patch` are the placement of a sticky in a row; add_story_map.py
puts a new sticky in a row with the same three.

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


def row_top(bands, label, moving=()):
    """Where a row starts: its first row of stickies, or its label when it has none. Stickies on the move do not count."""
    return min((s["y"] for s in bands[label["name"]] if s["id"] not in moving), default=label["y"])


def stack_y(row, x, top):
    """The y a sticky takes in the column x of a row: under the stickies it would overlap, or the top of the row."""
    stack = [s["y"] for s in row if abs(s["x"] - x) < CARD_W]
    return round(max(stack) + ROW_STEP, 2) if stack else top


def shift_patch(svg, labels, bands, target_label, deepest, moving=()):
    """The ops that push the rows below the target down when it grew, labels and their stickies together.

    `deepest` is the y of the lowest sticky of the target row once the new ones are placed.
    Returns (label ops, sticky ops), empty when nothing has to move.
    """
    below = labels[labels.index(target_label) + 1:]
    shift = max(0, round(deepest + RELEASE_GAP - row_top(bands, below[0], moving), 2)) if below else 0
    if not shift:
        return [], []
    label_ops = [replace_patch(svg, l["name"], top=round(row_top(bands, l, moving) + shift, 2)) for l in below]
    sticky_ops = [f'<update_elements_svg ids="{s["id"]}">\n<attr x="{s["x"]}" y="{round(s["y"] + shift, 2)}"/>\n</update_elements_svg>'
                  for l in below
                  for s in sorted(bands[l["name"]], key=lambda s: (s["y"], s["x"]))
                  if s["id"] not in moving]
    return label_ops, sticky_ops


def move_patch(svg, ids, target, task=None):
    labels, bands = read_bands(svg)
    names = [l["name"] for l in labels if l["name"] not in BACKBONE]
    if target not in names:
        raise ValueError(f'No release labeled "{target}" on the board; the labels are: {", ".join(names)}')
    columns = {s["text"]: s["x"] for s in bands.get("Tasks", [])}
    if task is not None and task not in columns:
        raise ValueError(f'No task "{task}" on the board; the tasks are: {", ".join(columns)}')
    by_id = {s["id"]: (name, s) for name, stickies in bands.items() for s in stickies}
    if len(set(ids)) != len(ids):
        raise ValueError("A sticky is listed twice; list each story once")
    for sid in ids:
        if sid not in by_id:
            raise ValueError(f'No sticky with id "{sid}" on the board')
        name, story = by_id[sid]
        if name in BACKBONE:
            raise ValueError(f'"{story["text"]}" is in {name}, not in a release; only stories move')
        if name == target and task is None:
            raise ValueError(f'"{story["text"]}" is already in {target}')

    target_label = next(l for l in labels if l["name"] == target)
    row = [s for s in bands[target] if s["id"] not in ids]
    placed = {}
    for sid in ids:
        story = by_id[sid][1]
        x = columns[task] if task is not None else story["x"]
        y = stack_y(row, x, row_top(bands, target_label, ids))
        placed[sid] = (x, y)
        row.append({"id": sid, "x": x, "y": y})

    label_ops, sticky_ops = shift_patch(svg, labels, bands, target_label, max(s["y"] for s in row), ids)
    parts = list(label_ops)
    parts += [f'<update_elements_svg ids="{sid}">\n<attr x="{x}" y="{y}"/>\n</update_elements_svg>'
              for sid, (x, y) in placed.items()]
    parts += sticky_ops
    return "\n".join(parts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Write the patch that moves stories to another release.")
    parser.add_argument("board", help="the board SVG as getConfluenceContent returns it")
    parser.add_argument("--story", action="append", required=True, metavar="ID", help="the id of a sticky to move; repeat for each one")
    parser.add_argument("--to", required=True, metavar="NAME", help="the label of the target row")
    parser.add_argument("--task", metavar="TASK", help="the task whose column the stories take; the target can then be their own release")
    args = parser.parse_args()
    try:
        print(move_patch(open(args.board, encoding="utf-8").read(), args.story, args.to, args.task))
    except ValueError as error:
        parser.error(str(error))
