"""Read a story map whiteboard SVG back into releases, activities, tasks, and stories.

Usage: python3 read_story_map.py board.svg [--json] [--previous N]

Accepts the SVG exactly as getConfluenceContent returns it, including the line-number
prefixes. Works on boards edited by hand, as long as:
- the board header, if any, sits above the "User persona" label;
- each row has a label: a text whose bold 27px line is "User persona", "Activities",
  "Tasks", or a release name ("MVP", "Release 2", ...), placed at or above its row;
- each story sits under its task, in the same column (x within half a card).
The first label after "Tasks" is taken as the MVP.

A release's "count" is its stories; red stickies (open questions) are not stories and
are counted apart in "open". --previous N is the number of stories the first release
had when it was last reported; the script then says how much it grew, shrank or stayed.
"""
import json
import re
import sys
from html import unescape

BACKBONE = {"User persona": "personas", "Activities": "activities", "Tasks": "tasks"}
CARD_W, CARD_H = 240.05, 144.03
# Reds of the sticky palette: the open-question fill and the light red Confluence snaps near-reds to.
OPEN_FILLS = ("#ffd5d2", "#ffeceb")


def attrs(tag):
    return dict(re.findall(r'([\w:-]+)="([^"]*)"', tag))


def parse(svg):
    svg = re.sub(r"(?m)^\d+(?=\s*<|$)", "", svg)
    stickies = {}
    for m in re.finditer(r"<rect\b[^>]*>", svg):
        a = attrs(m.group(0))
        if a.get("data-type") == "sticky":
            stickies[a["id"]] = {"x": float(a["x"]), "y": float(a["y"]), "fill": a.get("fill", ""), "text": ""}
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
                labels.append({"name": unescape(title.group(1)).strip(), "y": float(a["y"])})
    labels.sort(key=lambda l: l["y"])
    # The board header (product name and vision) sits above "User persona".
    first = next((i for i, l in enumerate(labels) if l["name"] == "User persona"), 0)
    labels = labels[first:]
    if not labels:
        raise ValueError("No row labels found")

    bands = {l["name"]: [] for l in labels}
    for s in stickies.values():
        center = s["y"] + CARD_H / 2
        above = [l for l in labels if l["y"] <= center]
        if above:
            bands[above[-1]["name"]].append(s)

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
    for l in labels:
        if l["name"] in BACKBONE:
            continue
        columns = [[] for _ in tasks]
        for s in sorted(bands[l["name"]], key=lambda s: (s["x"], s["y"])):
            c = column(s)
            if c is None:
                result["unplaced"].append({"release": l["name"], "text": s["text"]})
            else:
                columns[c].append({"text": s["text"], "open": s["fill"].lower() in OPEN_FILLS})
        result["releases"].append({
            "name": l["name"],
            "count": sum(1 for c in columns for st in c if not st["open"]),
            "open": sum(1 for c in columns for st in c if st["open"]),
            "tasks": [
                {"activity": activity_for(t), "task": t["text"], "stories": columns[i]}
                for i, t in enumerate(tasks)
            ],
        })
    return result


def change(r, previous):
    """Stories the first release gained (positive) or lost (negative) since `previous`."""
    return r["releases"][0]["count"] - previous if r["releases"] else 0


def plural(n, one, many):
    return f"{n} {one if n == 1 else many}"


def summary(r, previous=None):
    lines = [f'{rel["name"]}: {plural(rel["count"], "story", "stories")}, {plural(rel["open"], "open question", "open questions")}'
             for rel in r["releases"]]
    if previous is not None and r["releases"]:
        first, delta = r["releases"][0], change(r, previous)
        verb = f"grew by {delta}" if delta > 0 else f"shrank by {-delta}" if delta < 0 else "stayed the same"
        lines.append(f'{first["name"]} {verb} (was {previous}, now {first["count"]})')
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
                lines.append(f'  - {s["text"]}' + (" (open decision)" if s["open"] else ""))
        lines.append("")
    if r["unplaced"]:
        lines.append("## Unplaced stickies")
        lines += [f'- {u["release"]}: {u["text"]}' for u in r["unplaced"]]
    return "\n".join(lines)


if __name__ == "__main__":
    data = parse(open(sys.argv[1], encoding="utf-8").read())
    if "--json" in sys.argv:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        previous = int(sys.argv[sys.argv.index("--previous") + 1]) if "--previous" in sys.argv else None
        print(summary(data, previous))
        print()
        print(to_markdown(data))
