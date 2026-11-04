"""Read the current release of a Story Map whiteboard: its stories by activity and task, and its open questions.

Usage: python3 read_release.py board.svg [--json]

Accepts the SVG exactly as getConfluenceContent returns it (content_format: svg),
including the line-number prefixes. The board follows the Gemba Product layout:
- each row has a label, a text whose bold 27px line is "User persona", "Activities",
  "Tasks" or a release name ("MVP", "Release 2", ...), at or above its row;
- each story sits under its task, in the same column, drawn as a sticky or as a rectangle of the Jira card.

Each release reports the description on its row label, the value it delivers.
A release is delivered when its stories are gray, and it does not count. The current
release is the first one that is not delivered; the row named Later never is. Red
stickies are open questions, not stories, and are reported apart.

Nothing is copied anywhere: the board in Confluence is the only source, and this
reads it each time. Ported from Gemba Product's read_story_map.py.
"""
import json
import re
import sys
from html import unescape

CARD_W, CARD_H = 240.05, 144.03
RELEASED = "#f0f1f2"
# Reds of the sticky palette: the open-question fill and the light red Confluence snaps near-reds to.
OPEN_FILLS = ("#ffd5d2", "#ffeceb")
BACKBONE = ("User persona", "Activities", "Tasks")


def attrs(tag):
    return dict(re.findall(r'([\w:-]+)="([^"]*)"', tag))


def read_bands(svg):
    """The row labels, top to bottom, and the stickies and story rectangles of each row, keyed by label name."""
    svg = re.sub(r"(?m)^\d+(?=\s*<|$)", "", svg)
    stickies = {}
    for m in re.finditer(r"<rect\b[^>]*>", svg):
        a = attrs(m.group(0))
        if a.get("data-type") in ("sticky", "rectangle"):
            # A story is a sticky or a rectangle of the Jira card size: its height comes from the element itself.
            stickies[a["id"]] = {"id": a["id"], "x": float(a["x"]), "y": float(a["y"]), "h": float(a.get("height", CARD_H)),
                                 "fill": a.get("fill", "").lower(), "text": ""}
    labels = []
    for m in re.finditer(r"(<text\b[^>]*>)(.*?)</text>", svg, re.S):
        a, body = attrs(m.group(1)), m.group(2)
        parts = [unescape(t) for t in re.findall(r"<tspan\b[^>]*>([^<]*)</tspan>", body)]
        text = " ".join(p.strip() for p in parts if p.strip())
        if a.get("belongs-to") in stickies:
            stickies[a["belongs-to"]]["text"] = text
        elif a.get("data-type") == "text":
            title = re.search(r'<tspan[^>]*font-weight="bold"[^>]*font-size="27px"[^>]*>([^<]*)</tspan>', body)
            if title:
                name = unescape(title.group(1)).strip()
                # The lines after the bold name describe the row: for a release, the value it delivers.
                rest = text.split(name, 1)[1].strip() if name in text else ""
                labels.append({"name": name, "description": rest, "y": float(a["y"])})
    labels.sort(key=lambda l: l["y"])
    # The board header (product name and vision) sits above "User persona".
    first = next((i for i, l in enumerate(labels) if l["name"] == "User persona"), 0)
    labels = labels[first:]
    if not labels:
        raise ValueError("No row labels found")

    bands = {l["name"]: [] for l in labels}
    for s in stickies.values():
        center = s["y"] + s["h"] / 2
        above = [l for l in labels if l["y"] <= center]
        if above:
            bands[above[-1]["name"]].append(s)
    return labels, bands


def current_row(labels, bands):
    """The label of the first release not delivered, or None when every release is gray."""
    for l in labels:
        if l["name"] in BACKBONE or l["name"] == "Later":
            continue
        fills = [s["fill"] for s in bands[l["name"]] if s["fill"] not in OPEN_FILLS]
        if not (fills and all(f == RELEASED for f in fills)):
            return l
    return None


def current_release(svg):
    """The first release not delivered, with its stories by activity and task and its open questions apart (the command line refuses a release that has any)."""
    labels, bands = read_bands(svg)
    tasks = sorted(bands.get("Tasks", []), key=lambda s: s["x"])
    activities = sorted(bands.get("Activities", []), key=lambda s: s["x"])

    def column(s):
        best = min(range(len(tasks)), key=lambda i: abs(tasks[i]["x"] - s["x"]), default=None)
        return best if best is not None and abs(tasks[best]["x"] - s["x"]) <= CARD_W / 2 else None

    def activity_for(task):
        owner = [a for a in activities if a["x"] <= task["x"] + CARD_W / 2]
        return owner[-1]["text"] if owner else ""

    l = current_row(labels, bands)
    if l:
        row = bands[l["name"]]
        columns = [[] for _ in tasks]
        for s in sorted(row, key=lambda s: (s["x"], s["y"])):
            c = column(s)
            if c is not None:
                columns[c].append(s)
        stories, open_questions = [], []
        for i, task in enumerate(tasks):
            open_questions += [s["text"] for s in columns[i] if s["fill"] in OPEN_FILLS]
            done = [s["text"] for s in columns[i] if s["fill"] not in OPEN_FILLS]
            if not done:
                continue
            activity = activity_for(task)
            if not stories or stories[-1]["activity"] != activity:
                stories.append({"activity": activity, "tasks": []})
            stories[-1]["tasks"].append({"task": task["text"], "stories": done})
        return {"release": l["name"], "description": l["description"], "stories": stories, "open_questions": open_questions}
    return {"release": "", "description": "", "stories": [], "open_questions": []}


def to_markdown(release):
    lines = [f'## {release["release"]}']
    if release["description"]:
        lines.append(f'\n{release["description"]}')
    for a in release["stories"]:
        lines.append(f'\n### {a["activity"]}')
        for t in a["tasks"]:
            lines.append(f'- **{t["task"]}**')
            lines += [f"  - {text}" for text in t["stories"]]
    return "\n".join(lines)


if __name__ == "__main__":
    release = current_release(open(sys.argv[1], encoding="utf-8").read())
    if release["open_questions"]:
        print(f'{release["release"]} has open questions (red stickies); decide them on the Story Map before opening it:', file=sys.stderr)
        for question in release["open_questions"]:
            print(f"- {question}", file=sys.stderr)
        sys.exit(1)
    del release["open_questions"]
    print(json.dumps(release, ensure_ascii=False, indent=2) if "--json" in sys.argv else to_markdown(release))
