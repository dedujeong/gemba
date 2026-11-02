"""Build a Confluence whiteboard SVG with the architecture diagrams of a product.

Usage: python3 build_architecture.py spec.json out.svg

Spec (see ../assets/architecture-template.json):
{
  "product": {"name": "<Product>", "description": "<What it is, in a few words>"},
  "context": {
    "description": "<Who uses it and which systems it talks to>",
    "actors": ["<Role 1>", "<Role 2>"],
    "externals": [{"name": "<System>", "description": "<What it gives>"}],
    "relations": [{"from": "<Role 1>", "to": "<Product>", "label": "<what it does there>"}]
  }
}

Every relation names two elements of its own diagram and says what flows between
them: an unlabelled arrow tells the reader nothing, so it is rejected.

The element shapes come from a board built by hand and read back, so they are what
Confluence stores, not what the format guide suggests (see ../references/diagrams.md):
an actor is a plain rectangle with its name as free text underneath, because
`data-shape="user"` renders square; a system is a 220x160 `process` shape, gray when
somebody else runs it. Confluence recalculates the routing of every connector, so the
points here only have to be a sane angled path between the two anchors.
"""
import json
import sys
import xml.dom.minidom
from xml.sax.saxutils import escape

FONT = "Atlassian Sans, ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, Ubuntu, Helvetica Neue, sans-serif"
FS = "15.47px"
INK, ARROW = "#172b4d", "#758195"

# Fills of the closed Confluence palette: ours says who runs the piece.
INTERNAL, EXTERNAL = "#cfe1fd", "#f0f1f2"
STROKE_INTERNAL, STROKE_EXTERNAL = "#1558bc", "#7d818a"

ACTOR_SIDE, ACTOR_LABEL_DY = 124, 168
BOX_W, BOX_H = 220, 160

X_ACTOR, X_PRODUCT, X_EXTERNAL = -1117.0, -540.0, 97.0
X_LABEL, HEADING_DY = -1160.1, -173.0
ACTOR_STEP, BOX_STEP = 242.0, 242.0

MARKER_ID = "arrowhead-6-rgb_117__129__149_"
ARROWHEAD = (
    f'<defs id="defs-{MARKER_ID}"><marker markerWidth="6" markerHeight="6" refX="0" refY="3" '
    f'viewBox="0 0 6 6" orient="auto-start-reverse" id="{MARKER_ID}" markerUnits="userSpaceOnUse">'
    f'<polygon points="6,3 0,0 0,6" fill="{ARROW}" id="{MARKER_ID}-head"/></marker></defs>'
)


def heading(hid, title, description, y):
    """A diagram heading: a bold 27px title and a description, laid out like a Story Map row label."""
    spans = f'<tspan font-weight="bold" font-size="27px">{escape(title)}</tspan>'
    if description:
        spans += f'<tspan font-size="{FS}" dy="1">{escape(description)}</tspan>'
    return (
        f'<text x="{X_LABEL}" y="{round(y, 2)}" width="899.81" text-anchor="start" font-size="{FS}" '
        f'fill="{INK}" id="{hid}" data-type="text">{spans}</text>'
    )


class Diagram:
    """One diagram on the board: its elements, their boxes and the arrows between them."""

    def __init__(self, prefix):
        self.prefix = prefix
        self.out = []
        self.box_of = {}
        self.arrows = 0

    def _put(self, name, eid, x, y, w, h):
        self.box_of[name] = (eid, x, y, w, h)

    def actor(self, name, x, y):
        eid = f"{self.prefix}-a{len(self.box_of)}"
        self.out.append(
            f'<rect width="{ACTOR_SIDE}" height="{ACTOR_SIDE}" fill="{INTERNAL}" x="{x}" y="{y}" '
            f'stroke="{STROKE_EXTERNAL}" stroke-width="0.5" id="{eid}" data-type="rectangle"/>'
        )
        self.out.append(
            f'<text x="{round(x + ACTOR_SIDE / 2, 2)}" y="{round(y + ACTOR_LABEL_DY, 2)}" text-anchor="middle" '
            f'font-size="{FS}" fill="{INK}" id="{eid}-name" data-type="text">'
            f'<tspan font-size="{FS}">{escape(name)}</tspan></text>'
        )
        self._put(name, eid, x, y, ACTOR_SIDE, ACTOR_SIDE)

    def box(self, name, description, x, y, external=False, shape="process"):
        eid = f"{self.prefix}-b{len(self.box_of)}"
        fill, stroke = (EXTERNAL, STROKE_EXTERNAL) if external else (INTERNAL, STROKE_INTERNAL)
        self.out.append(
            f'<rect width="{BOX_W}" height="{BOX_H}" fill="{fill}" x="{x}" y="{y}" stroke="{stroke}" '
            f'stroke-width="0.5" id="{eid}" data-type="shape" data-shape="{shape}"/>'
        )
        # Several tspans in one shape read as a single line, so the description follows the name with a space.
        spans = f'<tspan font-size="{FS}">{escape(name)}</tspan>'
        if description:
            spans += f'<tspan font-size="{FS}"> {escape(description)}</tspan>'
        self.out.append(
            f'<text x="{round(x + BOX_W / 2, 2)}" y="{round(y + BOX_H / 2, 2)}" width="176" text-anchor="middle" '
            f'font-size="{FS}" font-scale="1" fill="{INK}" id="{eid}-text" belongs-to="{eid}">{spans}</text>'
        )
        self._put(name, eid, x, y, BOX_W, BOX_H)

    def arrow(self, source, target, label):
        (sid, sx, sy, sw, sh), (tid, tx, ty, tw, th) = self.box_of[source], self.box_of[target]
        horizontal = abs((tx + tw / 2) - (sx + sw / 2)) >= abs((ty + th / 2) - (sy + sh / 2))
        if horizontal:
            start, end = ("right", "left") if tx >= sx else ("left", "right")
        else:
            start, end = ("bottom", "top") if ty >= sy else ("top", "bottom")
        x1, y1 = anchor_point(sx, sy, sw, sh, start)
        x2, y2 = anchor_point(tx, ty, tw, th, end)
        if horizontal:
            mid = round((x1 + x2) / 2, 2)
            points = f"{x1},{y1} {mid},{y1} {mid},{y2} {x2},{y2}"
            lx, ly = mid, round((y1 + y2) / 2, 2)
        else:
            mid = round((y1 + y2) / 2, 2)
            points = f"{x1},{y1} {x1},{mid} {x2},{mid} {x2},{y2}"
            lx, ly = round((x1 + x2) / 2, 2), mid
        self.arrows += 1
        cid = f"{self.prefix}-r{self.arrows}"
        self.out.append(
            f'<polyline points="{points}" fill="none" stroke-width="2" stroke="{ARROW}" id="{cid}" '
            f'data-type="connector" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" begins-at="{sid}" ends-at="{tid}" '
            f'start-anchor="{start}" start-proportion="0.5" end-anchor="{end}" end-proportion="0.5" '
            f'line-type="angled" marker-end="url(#{MARKER_ID})"/>'
        )
        self.out.append(
            f'<text x="{lx}" y="{ly}" text-anchor="middle" font-size="{FS}" font-scale="1" fill="{INK}" '
            f'id="{cid}-label" data-type="pathLabel" belongs-to="{cid}" data-proportion="0.5">'
            f'<tspan font-size="{FS}">{escape(label)}</tspan></text>'
        )

    def bottom(self):
        return max((y + h for _, _, y, _, h in self.box_of.values()), default=0.0)


def anchor_point(x, y, w, h, side):
    return {
        "left": (round(x, 2), round(y + h / 2, 2)),
        "right": (round(x + w, 2), round(y + h / 2, 2)),
        "top": (round(x + w / 2, 2), round(y, 2)),
        "bottom": (round(x + w / 2, 2), round(y + h, 2)),
    }[side]


def draw_relations(diagram, relations, where):
    """Draw every arrow of one diagram, after checking it can be drawn and says something."""
    for relation in relations:
        source, target = relation.get("from"), relation.get("to")
        for name in (source, target):
            if name not in diagram.box_of:
                raise ValueError(f'{where}: "{name}" is not an element of this diagram')
        label = (relation.get("label") or "").strip()
        if not label:
            raise ValueError(f'{where}: the arrow from "{source}" to "{target}" says nothing: give it a label')
        diagram.arrow(source, target, label)


def context_diagram(spec, top):
    """Who uses the product and which systems it talks to: actors at the left, the product in the middle."""
    product = spec["product"]
    if not product.get("name"):
        raise ValueError("product: the name is required, because every diagram is about it")
    context = spec.get("context", {})
    actors = context.get("actors", [])
    externals = context.get("externals", [])

    d = Diagram("ctx")
    out = [heading("heading-context", "Context", context.get("description", ""), top + HEADING_DY)]
    for i, actor in enumerate(actors):
        d.actor(actor, X_ACTOR, round(top + i * ACTOR_STEP, 2))

    column_height = max(len(actors) - 1, 0) * ACTOR_STEP + ACTOR_SIDE
    d.box(product["name"], product.get("description", ""), X_PRODUCT,
          round(top + (column_height - BOX_H) / 2, 2))
    for i, external in enumerate(externals):
        d.box(external["name"], external.get("description", ""), X_EXTERNAL,
              round(top + i * BOX_STEP, 2), external=True)

    draw_relations(d, context.get("relations", []), "context")
    return out + d.out, d.bottom()


def build(spec):
    elements, _ = context_diagram(spec, 0.0)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="50000" height="50000" '
        f'viewBox="-25160.1 -25173 50000 50000" font-family="{FONT}">'
        + ARROWHEAD + "".join(elements) + "</svg>"
    )
    xml.dom.minidom.parseString(svg)
    return svg


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    svg = build(spec)
    open(sys.argv[2], "w", encoding="utf-8").write(svg)
    context = spec.get("context", {})
    print(f"{len(svg)} bytes")
    print(f'Context: {len(context.get("actors", []))} actors, '
          f'{len(context.get("externals", []))} external systems, '
          f'{len(context.get("relations", []))} arrows')
