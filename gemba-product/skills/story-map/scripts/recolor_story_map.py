"""Say which stickies of an existing story map board change color, and to which.

Usage: python3 recolor_story_map.py board.svg [--released NAME]...

Accepts the SVG exactly as getConfluenceContent returns it, like read_story_map.py,
and finds the rows the same way. Each sticky takes the color of its row: persona,
activities and tasks by their label; each release by its position among the ones not
delivered (current, next, later), or gray when named with --released. Open questions
stay red. Old gray cannot tell a delivered release from a later one, so a delivered
release is never guessed: the person names it.

Only the stickies that change are listed, grouped by color, ready for
`update_elements_svg ids="..." <attr fill="..."/>`. Text and positions are not part
of the output, so applying it cannot move or rewrite anything.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I does not add it

from build_story_map import ACTIVITY, OPEN, PERSONA, RELEASED, TASK, release_fills
from read_story_map import BACKBONE, OPEN_FILLS, read_bands

BACKBONE_FILLS = {"User persona": PERSONA, "Activities": ACTIVITY, "Tasks": TASK}


def plan(svg, released=()):
    """{fill: [sticky ids]} for the stickies whose fill is not the one of their row."""
    labels, bands = read_bands(svg)
    names = [l["name"] for l in labels if l["name"] not in BACKBONE]
    unknown = [n for n in released if n not in names]
    if unknown:
        raise ValueError(f'No release labeled {", ".join(map(repr, unknown))} on the board; the labels are: {", ".join(names)}')
    row_fill = dict(BACKBONE_FILLS)
    row_fill.update(zip(names, release_fills([{"released": n in released} for n in names])))
    changes = {}
    for name, stickies in bands.items():
        for s in sorted(stickies, key=lambda s: (s["y"], s["x"])):
            target = OPEN if s["fill"].lower() in OPEN_FILLS else row_fill[name]
            if s["fill"].lower() != target:
                changes.setdefault(target, []).append(s["id"])
    return changes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Say which stickies of a story map board change color.")
    parser.add_argument("board", help="the board SVG as getConfluenceContent returns it")
    parser.add_argument("--released", action="append", default=[], metavar="NAME",
                        help="a delivered release, by its label; repeat for each one")
    args = parser.parse_args()
    try:
        changes = plan(open(args.board, encoding="utf-8").read(), args.released)
    except ValueError as error:
        parser.error(str(error))
    print("\n".join(f'{fill}: ids="{",".join(ids)}"' for fill, ids in changes.items()) or "Nothing to change.")
