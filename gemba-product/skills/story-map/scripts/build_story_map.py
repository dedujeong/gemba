"""Build a Confluence whiteboard SVG for a user story map from a JSON spec.

Usage: python3 build_story_map.py spec.json out.svg

Spec (see ../assets/story-map-template.json):
{
  "title": "<Product name>",
  "vision": "<One or two sentences: what the product will be and for whom.>",
  "labels": {"persona": "...", "activities": "...", "tasks": "..."},
  "personas": ["<Primary user>", "<Actor 2>"],
  "activities": [{"column": 0, "text": "<Activity 1>"}],
  "tasks": ["<Task 1>", "..."],
  "releases": [
    {"name": "MVP", "description": "...",
     "stories": [[{"text": "story", "traces": "Problem"}, {"text": "open question", "open": true}], []]},
    {"name": "Release 2", "description": "...", "stories": [["later story"], ...]}
  ]
}
"releases[i].stories" has one list per task column, top to bottom.
Colors follow the Jira work items and always mean the same thing: persona yellow,
activities purple, tasks blue. Releases are colored by position among the ones not
delivered: the first (usually the MVP) is the current release, green; the second is
the next one, orange; the rest are later, light orange. "released": true marks a
delivered release and turns its row gray. "open": true makes a red sticky for an
unresolved question.

Every story of the current release (the first one not delivered) must say where it comes from in the brief:
"traces" names the problem, the primary job or the Quality bar condition it
serves. A story without it is rejected, so no MVP story is left without an
origin. Open questions and later-release stories do not need it.

The output is for createConfluenceContent. On create, Confluence reads a free
text's y as its vertical center and stores its top, so text y values here are
the desired top plus half the estimated height. It also pushes a separate title
text about 113 units above the text below it, so the product name and the
vision share one text element, laid out like the row labels. Mentions are
dropped on create, so the board names no people.
"""
import math
import json
import sys
import xml.dom.minidom
from xml.sax.saxutils import escape

FONT = "Atlassian Sans, ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, Ubuntu, Helvetica Neue, sans-serif"
CARD_W, CARD_H = 240.05, 144.03
X_LABEL, X0, PITCH = -120.56, 318.51, 303.33
Y_PERSONA, BACKBONE_STEP = -185.02, 250.68
ROW_STEP, RELEASE_GAP = 184.03, 245.6

# Fills are values of the closed sticky palette of Confluence: any other hex is
# snapped to the nearest one and the stored color differs from the requested one.
PERSONA, ACTIVITY, TASK = "#f5e989", "#eed7fc", "#cfe1fd"
CURRENT, NEXT, LATER, RELEASED, OPEN = "#baf3db", "#fce4a6", "#fff5db", "#f0f1f2", "#ffd5d2"
FS = "15.47px"

# Desired tops relative to the persona row, measured on a reference board.
LABEL_TOP = {"persona": -67, "activities": -56, "tasks": -45, "release": -62}
HEADER_TOP, HEADER_SCALE, HEADER_CHARS = -299, 1.29, 170
LABEL_BASE_H, LABEL_LINE_H, LABEL_CHARS = 80, 22, 42


def label_height(description, chars=LABEL_CHARS):
    lines = math.ceil(len(description) / chars) if description else 0
    return LABEL_BASE_H + LABEL_LINE_H * lines


def release_fills(releases):
    """The story fill of each release: gray if delivered, else current, next and later by position."""
    fills, position = [], 0
    for release in releases:
        if release.get("released"):
            fills.append(RELEASED)
        else:
            fills.append((CURRENT, NEXT)[position] if position < 2 else LATER)
            position += 1
    return fills


def current_release(spec):
    """The first release not delivered, or None when every release shipped."""
    return next((r for r in spec["releases"] if not r.get("released")), None)


def col_x(i):
    return round(X0 + i * PITCH, 2)


class Board:
    def __init__(self):
        self.out = []
        self.n = 0

    def sticky(self, x, y, fill, text):
        self.n += 1
        sid = f"s{self.n}"
        self.out.append(f'<rect width="{CARD_W}" height="{CARD_H}" id="{sid}" data-type="sticky" fill="{fill}" x="{x}" y="{y}"/>')
        self.out.append(
            f'<text x="{round(x + CARD_W / 2, 2)}" y="{round(y + CARD_H / 2, 2)}" width="216" text-anchor="middle" '
            f'font-size="{FS}" fill="#172b4d" id="{sid}-text" belongs-to="{sid}"><tspan font-size="{FS}">{escape(text)}</tspan></text>'
        )

    def row_label(self, lid, top, title, description, width=344.12, scale=1, chars=LABEL_CHARS):
        y = top + scale * label_height(description, chars) / 2
        spans = f'<tspan font-size="{FS}"> </tspan><tspan font-weight="bold" font-size="27px" dy="1">{escape(title)}</tspan>'
        if description:
            spans += f'<tspan font-size="{FS}" dy="1">{escape(description)}</tspan>'
        self.out.append(
            f'<text x="{X_LABEL}" y="{round(y, 2)}" width="{width}" text-anchor="start" font-size="{FS}" '
            f'font-scale="{scale}" fill="#172b4d" id="{lid}" data-type="text">{spans}</text>'
        )


def split_story(story):
    """Return (text, is_open, traces) for a story given as text or as a dict."""
    if isinstance(story, dict):
        return story["text"], bool(story.get("open")), (story.get("traces") or "").strip()
    return story, False, ""


def check_traces(spec):
    """Every story of the current release must trace to the brief."""
    release = current_release(spec)
    for column in release["stories"] if release else []:
        for story in column:
            text, is_open, traces = split_story(story)
            if not is_open and not traces:
                raise ValueError(f'{release["name"]}: story "{text}" has no "traces" to a problem, job or Quality bar condition')


def trace_table(spec):
    """(story, traces) for each story of the current release, in board order."""
    rows, release = [], current_release(spec)
    for column in release["stories"] if release else []:
        for story in column:
            text, is_open, traces = split_story(story)
            if not is_open:
                rows.append((text, traces))
    return rows


def check_release_names(spec):
    """The reader finds each row by its label: a repeated or reserved name would merge or hide a row."""
    seen = {"User persona", "Activities", "Tasks"}
    for release in spec["releases"]:
        if release["name"] in seen:
            raise ValueError(f'{release["name"]}: a release name must be unique and not "User persona", "Activities" or "Tasks"')
        seen.add(release["name"])


def build(spec):
    check_release_names(spec)
    check_traces(spec)
    b = Board()
    labels = spec.get("labels", {})
    tasks = spec["tasks"]

    b.row_label("board-header", Y_PERSONA + HEADER_TOP, spec["title"], spec.get("vision", ""),
                width=1445.17, scale=HEADER_SCALE, chars=HEADER_CHARS)

    y_act, y_task = round(Y_PERSONA + BACKBONE_STEP, 2), round(Y_PERSONA + 2 * BACKBONE_STEP, 2)
    b.row_label("label-persona", Y_PERSONA + LABEL_TOP["persona"], "User persona", labels.get("persona", ""))
    b.row_label("label-activities", y_act + LABEL_TOP["activities"], "Activities", labels.get("activities", ""))
    b.row_label("label-tasks", y_task + LABEL_TOP["tasks"], "Tasks", labels.get("tasks", ""))

    for i, p in enumerate(spec["personas"]):
        b.sticky(col_x(i), Y_PERSONA, PERSONA, p)
    for a in spec["activities"]:
        b.sticky(col_x(a["column"]), y_act, ACTIVITY, a["text"])
    for i, t in enumerate(tasks):
        b.sticky(col_x(i), y_task, TASK, t)

    y = y_task + RELEASE_GAP
    fills = release_fills(spec["releases"])
    for r_index, release in enumerate(spec["releases"]):
        stories = release["stories"]
        if len(stories) > len(tasks):
            raise ValueError(f'{release["name"]}: {len(stories)} columns but only {len(tasks)} tasks')
        b.row_label(f"label-release-{r_index}", y + LABEL_TOP["release"], release["name"], release.get("description", ""))
        depth = max((len(c) for c in stories), default=0) or 1
        for col, column in enumerate(stories):
            for row, story in enumerate(column):
                text, is_open, _ = split_story(story)
                fill = OPEN if is_open else fills[r_index]
                b.sticky(col_x(col), round(y + row * ROW_STEP, 2), fill, text)
        y = round(y + (depth - 1) * ROW_STEP + RELEASE_GAP, 2)

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="50000" height="50000" '
        f'viewBox="-25120.56 -25484.45 50000 50000" font-family="{FONT}">' + "".join(b.out) + "</svg>"
    )
    xml.dom.minidom.parseString(svg)
    return svg


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    svg = build(spec)
    open(sys.argv[2], "w", encoding="utf-8").write(svg)
    counts = [sum(len(c) for c in r["stories"]) for r in spec["releases"]]
    print(f"{len(svg)} bytes; stories per release: " + ", ".join(f'{r["name"]}={n}' for r, n in zip(spec["releases"], counts)))
    current = current_release(spec)
    print(f'Traces of the {current["name"] if current else "current release"} stories:')
    for text, traces in trace_table(spec):
        print(f"- {text} -> {traces}")
