"""Read a story map whiteboard SVG back into releases, activities, tasks, and stories.

Usage: python3 read_story_map.py board.svg [--statuses statuses.json] [--json] [--mvp [--json]] [--gaps] [--previous N]

Accepts the SVG exactly as getConfluenceContent returns it, including the line-number
prefixes. A story is a sticky, a rectangle or the card of its Jira issue (data-type="issue"):
the card has no text, so the story is listed by its key, read from the link of the issue.
The status a card shows is drawn by Jira and is not in the SVG: --statuses takes a JSON file
{"KEY": "Status"} that the skill fills from Jira, and each card reports its status, or null.
Works on boards edited by hand, as long as:
- the board header, if any, sits above the "User persona" label;
- each row has a label: a text whose bold 27px line is "User persona", "Activities",
  "Tasks", or a release name ("MVP", "Release 2", ...), placed at or above its row;
- each story sits under its task, in the same column (x within half a card).

Colors: green is the release about to be declared, gray the releases after it, red an
open question. Each release reports its "state":
- "delivered": it has issue cards and every one is Done or Cancelled (needs --statuses);
  a color never says that a release shipped, and a sticky or a rectangle has no issue.
- "current": the first release, never Later, with a green story that is not delivered.
- "later": the row named Later, which is not a release.
- "next": any other release, gray or not.
A board in the old colors has no green release, so it has no current release.

A release's "count" is its stories; red stickies (open questions) are not stories and
are counted apart in "open". A story is "declared" when it is the card of its issue (it has
a key) and "pending" while it is still a sticky or a rectangle: version-start swaps one for the other. --previous N is the number of stories the current release
had when it was last reported; the script then says how much it grew, shrank or stayed.

--gaps walks the current release left to right and prints the tasks with no story: the
steps a user would take that the release does not cover, and then its open questions,
the gaps nobody could decide yet. A release with one of those does not close.

--mvp prints only the current release, the value it delivers (the description on its row
label) and its stories grouped by activity and task, for whoever builds it; with --json it
prints the same as data, with the open questions apart. version-start reads it that way.
Nothing is copied anywhere: the board in Confluence is the only source, and this reads
it each time.
"""
import json
import os
import re
import sys
from html import unescape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I does not add it

from build_story_map import CARD_H, CARD_W, CURRENT

BACKBONE = {"User persona": "personas", "Activities": "activities", "Tasks": "tasks"}
# Reds of the sticky palette: the open-question fill and the light red Confluence snaps near-reds to.
OPEN_FILLS = ("#ffd5d2", "#ffeceb")
ISSUE_KEY = re.compile(r"/browse/([A-Z][A-Z0-9]*-\d+)")


def attrs(tag):
    return dict(re.findall(r'([\w:-]+)="([^"]*)"', tag))


def read_bands(svg):
    """The row labels, top to bottom, and the stickies and story rectangles of each row, keyed by label name."""
    svg = re.sub(r"(?m)^\d+(?=\s*<|$)", "", svg)
    stickies = {}
    for m in re.finditer(r"<rect\b[^>]*>", svg):
        a = attrs(m.group(0))
        if a.get("data-type") in ("sticky", "rectangle", "issue"):
            # A story is a sticky, a rectangle of the Jira card size or the card of its issue: its height comes from the
            # element itself. A card has no text, only the link of the issue, so its key stands for its text.
            key = ISSUE_KEY.search(a.get("data-smartlink-url", "")) if a["data-type"] == "issue" else None
            stickies[a["id"]] = {"id": a["id"], "x": float(a["x"]), "y": float(a["y"]), "h": float(a.get("height", CARD_H)),
                                 "fill": a.get("fill", ""), "text": key.group(1) if key else "", "key": key.group(1) if key else None}
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


def parse(svg, statuses=None):
    """`statuses` maps the key of an issue to its status in Jira: the card is drawn by Jira and the SVG does not carry it."""
    statuses = statuses or {}
    labels, bands = read_bands(svg)
    tasks = sorted(bands.get("Tasks", []), key=lambda s: s["x"])
    activities = sorted(bands.get("Activities", []), key=lambda s: s["x"])

    def column(s):
        best = min(range(len(tasks)), key=lambda i: abs(tasks[i]["x"] - s["x"]), default=None)
        if best is None or abs(tasks[best]["x"] - s["x"]) > CARD_W / 2:
            return None
        return best

    def activity_for(task):
        owner = [a for a in activities if a["x"] <= task["x"] + CARD_W / 2]
        return owner[-1]["text"] if owner else ""

    result = {
        "personas": [s["text"] for s in sorted(bands.get("User persona", []), key=lambda s: s["x"])],
        "releases": [],
        "unplaced": [],
    }
    green = []
    for l in labels:
        if l["name"] in BACKBONE:
            continue
        columns = [[] for _ in tasks]
        for s in sorted(bands[l["name"]], key=lambda s: (s["x"], s["y"])):
            c = column(s)
            if c is None:
                result["unplaced"].append({"release": l["name"], "id": s["id"], "text": s["text"]})
            else:
                status = statuses.get(s["key"]) if s["key"] else None
                columns[c].append({"id": s["id"], "text": s["text"], "open": s["fill"].lower() in OPEN_FILLS, "key": s["key"],
                                   "status": status, "cancelled": (status or "").lower() == "cancelled"})
        cards = [st for c in columns for st in c if st["key"] and not st["open"]]
        green.append(any(s["fill"].lower() == CURRENT for s in bands[l["name"]]))
        result["releases"].append({
            "name": l["name"],
            "description": l["description"],
            "delivered": bool(cards) and all(st["cancelled"] or (st["status"] or "").lower() == "done" for st in cards),
            "count": sum(1 for c in columns for st in c if not st["open"]),
            "declared": len(cards),
            "pending": sum(1 for c in columns for st in c if not st["open"] and not st["key"]),
            "open": sum(1 for c in columns for st in c if st["open"]),
            "cancelled": sum(1 for c in columns for st in c if st["cancelled"]),
            "tasks": [
                {"activity": activity_for(t), "task": t["text"], "stories": columns[i]}
                for i, t in enumerate(tasks)
            ],
        })
    chosen = False
    for release, is_green in zip(result["releases"], green):
        if release["name"] == "Later":
            release["state"] = "later"
        elif release["delivered"]:
            release["state"] = "delivered"
        elif is_green and not chosen:
            release["state"], chosen = "current", True
        else:
            release["state"] = "next"
    return result


def current(r):
    """The release about to be declared: the first green one that is not delivered. Later is a parking row, never the current release."""
    return next((release for release in r["releases"] if release["state"] == "current"), None)


def change(r, previous):
    """Stories the current release gained (positive) or lost (negative) since `previous`."""
    release = current(r)
    return release["count"] - previous if release else 0


def gaps(r):
    """The tasks of the current release with no story, left to right: the steps it leaves uncovered.

    An open question is not a story, so a task whose only sticky is red is a gap too.
    """
    release = current(r)
    return [{"activity": t["activity"], "task": t["task"]}
            for t in (release["tasks"] if release else [])
            if not any(not st["open"] for st in t["stories"])]


def open_questions(r):
    """The open questions of the current release, left to right: the gaps nobody could decide yet."""
    release = current(r)
    return [{"activity": t["activity"], "task": t["task"], "text": st["text"]}
            for t in (release["tasks"] if release else [])
            for st in t["stories"] if st["open"]]


def gaps_markdown(r):
    release = current(r)
    if not release:
        return "Every release is delivered: there is none to close."
    rows, questions = gaps(r), open_questions(r)
    if rows:
        lines = [f'{release["name"]}: {plural(len(rows), "task", "tasks")} with no story']
        lines += [f'- {g["activity"]}: {g["task"]}' for g in rows]
    else:
        lines = [f'{release["name"]}: every task has a story.']
    if questions:
        lines.append(f'{release["name"]}: {plural(len(questions), "open question", "open questions")} with no decision')
        lines += [f'- {q["activity"]}: {q["task"]}: {q["text"]}' for q in questions]
    return "\n".join(lines)


def for_development(r):
    """The current release as development reads it: stories by activity and task, open questions apart."""
    release = current(r)
    stories, open_questions = [], []
    for task in (release["tasks"] if release else []):
        done = [st["text"] for st in task["stories"] if not st["open"] and not st["cancelled"]]
        open_questions += [st["text"] for st in task["stories"] if st["open"]]
        if not done:
            continue
        if not stories or stories[-1]["activity"] != task["activity"]:
            stories.append({"activity": task["activity"], "tasks": []})
        stories[-1]["tasks"].append({"task": task["task"], "stories": done})
    return {"release": release["name"] if release else "", "description": release["description"] if release else "",
            "declared": release["declared"] if release else 0, "pending": release["pending"] if release else 0,
            "stories": stories, "open_questions": open_questions}


def mvp_markdown(mvp):
    lines = [f'## {mvp["release"]}']
    if mvp["description"]:
        lines.append(f'\n{mvp["description"]}')
    for a in mvp["stories"]:
        lines.append(f'\n### {a["activity"]}')
        for t in a["tasks"]:
            lines.append(f'- **{t["task"]}**')
            lines += [f"  - {text}" for text in t["stories"]]
    if mvp["open_questions"]:
        lines.append("\n### Open questions")
        lines += [f"- {q}" for q in mvp["open_questions"]]
    return "\n".join(lines)


def plural(n, one, many):
    return f"{n} {one if n == 1 else many}"


def summary(r, previous=None):
    lines = [f'{rel["name"]}: {plural(rel["count"], "story", "stories")}, {plural(rel["open"], "open question", "open questions")}'
             + (f', {rel["cancelled"]} cancelled' if rel["cancelled"] else "")
             + (" (delivered)" if rel["state"] == "delivered" else "") for rel in r["releases"]]
    release = current(r)
    if previous is not None and release:
        delta = change(r, previous)
        verb = f"grew by {delta}" if delta > 0 else f"shrank by {-delta}" if delta < 0 else "stayed the same"
        lines.append(f'{release["name"]} {verb} (was {previous}, now {release["count"]})')
    return "\n".join(lines)


def to_markdown(r):
    lines = []
    for release in r["releases"]:
        lines.append(f'## {release["name"]} ({plural(release["count"], "story", "stories")}, {plural(release["open"], "open question", "open questions")})')
        current = None
        for t in release["tasks"]:
            if not t["stories"]:
                continue
            if t["activity"] != current:
                current = t["activity"]
                lines.append(f"\n### {current}")
            lines.append(f'- **{t["task"]}**')
            for s in t["stories"]:
                lines.append(f'  - {s["text"]}' + (" (open decision)" if s["open"] else f' ({s["status"]})' if s["status"] else ""))
        lines.append("")
    if r["unplaced"]:
        lines.append("## Unplaced stickies")
        lines += [f'- {u["release"]}: {u["text"]}' for u in r["unplaced"]]
    return "\n".join(lines)


if __name__ == "__main__":
    statuses = json.load(open(sys.argv[sys.argv.index("--statuses") + 1], encoding="utf-8")) if "--statuses" in sys.argv else None
    data = parse(open(sys.argv[1], encoding="utf-8").read(), statuses)
    if "--gaps" in sys.argv:
        print(gaps_markdown(data))
    elif "--mvp" in sys.argv:
        mvp = for_development(data)
        print(json.dumps(mvp, ensure_ascii=False, indent=2) if "--json" in sys.argv else mvp_markdown(mvp))
    elif "--json" in sys.argv:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        previous = int(sys.argv[sys.argv.index("--previous") + 1]) if "--previous" in sys.argv else None
        print(summary(data, previous))
        print()
        print(to_markdown(data))
