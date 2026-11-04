"""Build a Confluence whiteboard SVG with the architecture diagrams of a product.

Usage: python3 build_architecture.py spec.json out.svg

Spec (see ../assets/architecture-template.json):
{
  "product": {"name": "<Product>"},
  "context": {
    "description": "<Who uses it and which systems it talks to>",
    "actors": ["<Role 1>", "<Role 2>"],
    "externals": [{"name": "<System>"}],
    "relations": [{"from": "<Role 1>", "to": "<Product>", "label": "<what it does there>"}]
  }
}

"data_model" is optional: {"description", "entities": [{"name", "fields": [...]}],
"relations": [{"from", "to", "label", "cardinality"}]}. It draws one box per entity with its main
fields and an arrow per relation, below the other diagrams; with no entities it is not drawn.
A relation whose cardinality is "1:N" carries 1 next to its origin, N next to its destination and
the verb in the middle; one whose cardinality is not decided leaves "cardinality" out and carries
only the verb.

"states" is optional, one item per entity that changes state: {"entity", "description",
"initial": {"state", "event"}, "states": [...], "transitions": [{"from", "to", "event"}]}. The
entity must be in the data model. It draws a box per state and an arrow per event, starting
from a marker with the event that creates the entity; an arrow with no event is rejected.

Each diagram takes "questions": [{"about": "<element>", "text": "<question>"}], one red sticky
beside the element it is about, for a doubt nobody has answered yet.

Every relation names two elements of its own diagram and says what flows between
them: an unlabelled arrow tells the reader nothing, so it is rejected, and so is a
label that does not start with a capital.

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

ACTOR_SIDE = 124
BOX_W, BOX_H = 220, 160

X_ACTOR, X_PRODUCT, X_EXTERNAL = -1117.0, -540.0, 97.0
X_LABEL, HEADING_DY = -1160.1, -173.0
ACTOR_STEP, BOX_STEP = 242.0, 242.0

# A boundary is a section around the pieces that run in the same place, stacked inside it.
PAD_X, PAD_TOP, PAD_BOTTOM, GAP_IN = 28.8, 70.0, 40.0, 90.0
SECTION_W = BOX_W + 2 * PAD_X
X_BOUNDARY, SECTION_GAP, LABEL_CHAR = -668.8, 80.0, 9.0
BLOCK_GAP, EXTERNAL_GAP, EXTERNAL_STEP = 300.0, 120.0, BOX_W + 80.0
SECTION_FILL = "#e9f2fe"

# Entities of the data model sit in a grid, a few per row.
ENTITY_COLUMNS, ENTITY_GAP_X, ENTITY_GAP_Y = 3, 300.0, 150.0

# The states of an entity: the same grid, with a small start marker at the left of the first row.
START_SIDE, START_FILL, START_GAP = 40, "#b7b9be", 300.0

# An open question is a red sticky of the Story Map palette, beside the element it comes from.
STICKY_W, STICKY_H, STICKY_FILL, STICKY_GAP, STICKY_CLEAR = 240.05, 144.03, "#ffd5d2", 180.0, 20.0

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
        self.sections = 0
        self.floor = 0.0
        self.obstacles = []
        self.stickies = []
        self.sideways = set()

    def _put(self, name, eid, x, y, w, h):
        self.box_of[name] = (eid, x, y, w, h)

    def actor(self, name, x, y):
        eid = f"{self.prefix}-a{len(self.box_of)}"
        self.out.append(
            f'<rect width="{ACTOR_SIDE}" height="{ACTOR_SIDE}" fill="{INTERNAL}" x="{x}" y="{y}" '
            f'stroke="{STROKE_EXTERNAL}" stroke-width="0.5" id="{eid}" data-type="rectangle"/>'
        )
        # The name is the text of the box itself, so it stays inside it wherever the box is moved.
        self.out.append(
            f'<text x="{round(x + ACTOR_SIDE / 2, 2)}" y="{round(y + ACTOR_SIDE / 2, 2)}" width="99.2" text-anchor="middle" '
            f'font-size="{FS}" font-scale="1" fill="{INK}" id="{eid}-text" belongs-to="{eid}">'
            f'<tspan font-size="{FS}">{escape(name)}</tspan></text>'
        )
        self._put(name, eid, x, y, ACTOR_SIDE, ACTOR_SIDE)

    def start(self, x, y):
        """The start marker of a state diagram: a small square the first arrow leaves from."""
        eid = f"{self.prefix}-start"
        self.out.append(
            f'<rect width="{START_SIDE}" height="{START_SIDE}" fill="{START_FILL}" x="{x}" y="{y}" '
            f'stroke="{STROKE_EXTERNAL}" stroke-width="0.5" id="{eid}" data-type="rectangle"/>'
        )
        self._put("Start", eid, x, y, START_SIDE, START_SIDE)

    def section(self, title, x, y, height):
        """A deployment boundary: the pieces that run in the same place, with the platform in its title."""
        sid = f"{self.prefix}-s{self.sections}"
        self.sections += 1
        self.obstacles.append((x, y, SECTION_W, height))
        self.out.append(
            f'<rect width="{round(SECTION_W, 2)}" height="{round(height, 2)}" fill="{SECTION_FILL}" '
            f'x="{round(x, 2)}" y="{round(y, 2)}" id="{sid}" data-type="section" data-title="{escape(title)}"/>'
        )
        return sid

    def box(self, name, description, x, y, external=False, shape="process", parent=None):
        eid = f"{self.prefix}-b{len(self.box_of)}"
        fill, stroke = (EXTERNAL, STROKE_EXTERNAL) if external else (INTERNAL, STROKE_INTERNAL)
        belongs = f' belongs-to="{parent}"' if parent else ""
        self.out.append(
            f'<rect width="{BOX_W}" height="{BOX_H}" fill="{fill}" x="{x}" y="{y}" stroke="{stroke}" '
            f'stroke-width="0.5" id="{eid}" data-type="shape" data-shape="{shape}"{belongs}/>'
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

    def arrow(self, source, target, label, cardinality=None):
        (sid, sx, sy, sw, sh), (tid, tx, ty, tw, th) = self.box_of[source], self.box_of[target]
        horizontal = abs((tx + tw / 2) - (sx + sw / 2)) >= abs((ty + th / 2) - (sy + sh / 2)) \
            or source in self.sideways or target in self.sideways
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
        parts = [(label, 0.5, lx, ly)]
        if cardinality:
            # One to many: 1 near the origin and N near the destination, with the verb in the middle.
            parts = [("1", 0.08, round(x1 + (lx - x1) * 0.16, 2), round(y1 + (ly - y1) * 0.16, 2))] + parts \
                + [("N", 0.92, round(x2 + (lx - x2) * 0.16, 2), round(y2 + (ly - y2) * 0.16, 2))]
        for n, (text, proportion, x, y) in enumerate(parts):
            self.out.append(
                f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{FS}" font-scale="1" fill="{INK}" '
                f'id="{cid}-label{n if cardinality else ""}" data-type="pathLabel" belongs-to="{cid}" '
                f'data-proportion="{proportion}"><tspan font-size="{FS}">{escape(text)}</tspan></text>'
            )

    def question(self, about, text, where):
        """An open question: a red sticky beside the element it is about, where nothing else is drawn."""
        if about not in self.box_of:
            raise ValueError(f'{where}: the question "{text}" is about "{about}", which is not an element of this diagram')
        _, x, y, w, h = self.box_of[about]
        centre_y = y + h / 2 - STICKY_H / 2
        taken = [(bx, by, bw, bh) for _, bx, by, bw, bh in self.box_of.values()] + self.obstacles + self.stickies
        right_most = max(bx + bw for bx, _, bw, _ in taken)
        candidates = [
            (x + w + STICKY_GAP, centre_y),
            (x - STICKY_GAP - STICKY_W, centre_y),
            (x + w / 2 - STICKY_W / 2, y + h + STICKY_GAP / 3),
            (x + w / 2 - STICKY_W / 2, y - STICKY_GAP / 3 - STICKY_H),
            (right_most + STICKY_GAP, centre_y),
        ]
        others = [(bx, by, bw, bh) for name, (_, bx, by, bw, bh) in self.box_of.items() if name != about]
        for sx, sy in candidates:
            clear = all(sx + STICKY_W + STICKY_CLEAR <= bx or bx + bw + STICKY_CLEAR <= sx
                        or sy + STICKY_H + STICKY_CLEAR <= by or by + bh + STICKY_CLEAR <= sy for bx, by, bw, bh in taken)
            # It must read as the doubt of its own element: no other element may sit nearer to it.
            nearest = all(rect_gap((sx, sy, STICKY_W, STICKY_H), (x, y, w, h))
                          < rect_gap((sx, sy, STICKY_W, STICKY_H), other) for other in others)
            if clear and nearest:
                break
        sid = f"{self.prefix}-q{len(self.stickies)}"
        self.stickies.append((sx, sy, STICKY_W, STICKY_H))
        self.out.append(
            f'<rect width="{STICKY_W}" height="{STICKY_H}" id="{sid}" data-type="sticky" fill="{STICKY_FILL}" '
            f'x="{round(sx, 2)}" y="{round(sy, 2)}" font-scale="1"/>'
        )
        self.out.append(
            f'<text x="{round(sx + STICKY_W / 2, 2)}" y="{round(sy + STICKY_H / 2, 2)}" width="216" text-anchor="middle" '
            f'font-size="{FS}" font-scale="1" fill="{INK}" id="{sid}-text" belongs-to="{sid}">'
            f'<tspan font-size="{FS}">{escape(text)}</tspan></text>'
        )

    def bottom(self):
        return max([y + h for _, _, y, _, h in self.box_of.values()] + [y + h for _, y, _, h in self.stickies]
                   + [self.floor], default=0.0)


def rect_gap(a, b):
    """The distance between two (x, y, w, h) rects, 0 when they touch or overlap."""
    dx = max(b[0] - (a[0] + a[2]), a[0] - (b[0] + b[2]), 0)
    dy = max(b[1] - (a[1] + a[3]), a[1] - (b[1] + b[3]), 0)
    return (dx ** 2 + dy ** 2) ** 0.5


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
        if label[0].islower():
            raise ValueError(f'{where}: the label of the arrow from "{source}" to "{target}" must start with a capital: "{label}"')
        cardinality = relation.get("cardinality")
        if cardinality not in (None, "1:N"):
            raise ValueError(f'{where}: the cardinality "{cardinality}" is not drawn: use "1:N", or leave it out when it is not decided')
        diagram.arrow(source, target, label, cardinality)


def draw_questions(diagram, questions, where):
    """Draw every open question of one diagram as a red sticky beside the element it is about."""
    for question in questions:
        diagram.question(question.get("about"), (question.get("text") or "").strip(), where)


def context_diagram(spec, top):
    """Who uses the product and which systems it talks to: actors at the left, the product in the middle."""
    product = spec["product"]
    if not product.get("name"):
        raise ValueError("product: the name is required, because every diagram is about it")
    context = spec.get("context", {})
    actors = context.get("actors", [])
    externals = context.get("externals", [])

    own = {piece["name"] for piece in deployable_pieces(spec)}
    for external in externals:
        if external["name"] in own:
            raise ValueError(f'context: "{external["name"]}" is a piece the team operates, not an external system: '
                             'it only appears in Containers, so take it out of the context externals')

    d = Diagram("ctx")
    out = [heading("heading-context", "Context", context.get("description", ""), top + HEADING_DY)]
    for i, actor in enumerate(actors):
        d.actor(actor, X_ACTOR, round(top + i * ACTOR_STEP, 2))

    column_height = max(len(actors) - 1, 0) * ACTOR_STEP + ACTOR_SIDE
    product_y = round(top + (column_height - BOX_H) / 2, 2)
    d.box(product["name"], "", X_PRODUCT, product_y)
    # The main flow is one straight row: the first external sits on the row of the product.
    for i, external in enumerate(externals):
        d.box(external["name"], "", X_EXTERNAL,
              round(product_y + i * BOX_STEP, 2), external=True)

    draw_relations(d, context.get("relations", []), "context")
    draw_questions(d, context.get("questions", []), "context")
    return out + d.out, d.bottom()


def deployable_pieces(spec):
    """The pieces of the product that are deployed on their own, across every boundary."""
    boundaries = spec.get("containers", {}).get("boundaries", [])
    return [piece for boundary in boundaries for piece in boundary.get("containers", [])]


def boundary_starts(containers):
    """The x of each boundary: between two neighbours there is room for the longest label that crosses them."""
    side = {}
    for i, boundary in enumerate(containers["boundaries"]):
        for piece in boundary.get("containers", []):
            side[piece["name"]] = i
    xs = [X_BOUNDARY]
    for i in range(1, len(containers["boundaries"])):
        longest = max([len((r.get("label") or "").strip()) for r in containers.get("relations", [])
                       if r.get("from") in side and r.get("to") in side
                       and min(side[r["from"]], side[r["to"]]) < i <= max(side[r["from"]], side[r["to"]])], default=0)
        xs.append(xs[-1] + SECTION_W + max(SECTION_GAP, LABEL_CHAR * longest + SECTION_GAP))
    return xs


def containers_diagram(spec, top):
    """What runs where and what each part is in charge of. Only for a product with more than one piece."""
    containers = spec["containers"]
    d = Diagram("con")
    out = [heading("heading-containers", "Containers", containers.get("description", ""), top + HEADING_DY)]

    # The main flow is one straight row: the first actor and the first piece of every boundary share it.
    row_centre = top + PAD_TOP + BOX_H / 2
    for i, actor in enumerate(containers.get("actors", [])):
        d.actor(actor, X_ACTOR, round(row_centre - ACTOR_SIDE / 2 + i * ACTOR_STEP, 2))

    starts = boundary_starts(containers)
    tallest = 0.0
    for i, boundary in enumerate(containers["boundaries"]):
        pieces = boundary.get("containers", [])
        height = PAD_TOP + len(pieces) * BOX_H + max(len(pieces) - 1, 0) * GAP_IN + PAD_BOTTOM
        tallest = max(tallest, height)
        x = round(starts[i], 2)
        sid = d.section(boundary["name"], x, top, height)
        for j, piece in enumerate(pieces):
            d.box(piece["name"], "", round(x + PAD_X, 2),
                  round(top + PAD_TOP + j * (BOX_H + GAP_IN), 2),
                  shape=piece.get("shape", "process"), parent=sid)

    # An external sits below the boundaries, one lane to the right of the boundary of the piece it talks to,
    # so its arrow leaves sideways into the gap and comes down without going through another piece.
    y_external = round(top + tallest + EXTERNAL_GAP, 2)
    side = {piece["name"]: i for i, b in enumerate(containers["boundaries"]) for piece in b.get("containers", [])}
    stacked = {}
    for external in containers.get("externals", []):
        peers = [r["to"] if r.get("from") == external["name"] else r["from"] for r in containers.get("relations", [])
                 if external["name"] in (r.get("from"), r.get("to"))]
        column = next((side[p] for p in peers if p in side), len(containers["boundaries"]) - 1)
        row = stacked.get(column, 0)
        stacked[column] = row + 1
        piece_right = starts[column] + PAD_X + BOX_W
        lane = starts[column] + SECTION_W + SECTION_GAP / 2
        d.box(external["name"], "", round(2 * lane - piece_right, 2),
              round(y_external + row * (BOX_H + GAP_IN / 2), 2), external=True)
        d.sideways.add(external["name"])

    d.floor = top + tallest
    draw_relations(d, containers.get("relations", []), "containers")
    draw_questions(d, containers.get("questions", []), "containers")
    return out + d.out, d.bottom()


def data_model_diagram(spec, top):
    """What the product keeps: one box per entity with its main fields, and an arrow per relation."""
    model = spec["data_model"]
    d = Diagram("dat")
    out = [heading("heading-data-model", "Data model", model.get("description", ""), top + HEADING_DY)]
    for i, entity in enumerate(model["entities"]):
        fields = entity.get("fields", [])
        if not fields:
            raise ValueError(f'data model: the entity "{entity["name"]}" has no fields: list its main fields')
        col, row = i % ENTITY_COLUMNS, i // ENTITY_COLUMNS
        d.box(entity["name"], ", ".join(fields),
              round(X_ACTOR + col * (BOX_W + ENTITY_GAP_X), 2),
              round(top + row * (BOX_H + ENTITY_GAP_Y), 2))
    draw_relations(d, model.get("relations", []), "data model")
    draw_questions(d, model.get("questions", []), "data model")
    return out + d.out, d.bottom()


def state_diagram(spec, diagram, index, top):
    """How one entity changes: a box per state and an arrow per event, with the event that creates it."""
    entity = diagram["entity"]
    if entity not in [e["name"] for e in spec.get("data_model", {}).get("entities", [])]:
        raise ValueError(f'states: "{entity}" is not an entity of the data model')
    states = diagram.get("states", [])
    initial = diagram.get("initial", {})
    if initial.get("state") not in states:
        raise ValueError(f'states of {entity}: the initial state "{initial.get("state")}" is not one of its states')
    where = f"states of {entity}"
    d = Diagram(f"st{index}")
    out = [heading(f"heading-states-{index}", f"States of {entity}", diagram.get("description", ""), top + HEADING_DY)]
    d.start(round(X_ACTOR, 2), round(top + (BOX_H - START_SIDE) / 2, 2))
    for i, state in enumerate(states):
        col, row = i % ENTITY_COLUMNS, i // ENTITY_COLUMNS
        d.box(state, "", round(X_ACTOR + START_SIDE + START_GAP + col * (BOX_W + ENTITY_GAP_X), 2),
              round(top + row * (BOX_H + ENTITY_GAP_Y), 2))
    relations = [{"from": "Start", "to": initial["state"], "label": initial.get("event")}]
    for transition in diagram.get("transitions", []):
        for name in (transition.get("from"), transition.get("to")):
            if name not in states:
                raise ValueError(f'{where}: "{name}" is not one of its states')
        relations.append({"from": transition["from"], "to": transition["to"], "label": transition.get("event")})
    draw_relations(d, relations, where)
    draw_questions(d, diagram.get("questions", []), where)
    return out + d.out, d.bottom()


def build(spec):
    elements, floor = context_diagram(spec, 0.0)
    if len(deployable_pieces(spec)) > 1:
        more, floor = containers_diagram(spec, round(floor + BLOCK_GAP, 2))
        elements += more
    if spec.get("data_model", {}).get("entities"):
        more, floor = data_model_diagram(spec, round(floor + BLOCK_GAP, 2))
        elements += more
    for index, diagram in enumerate(spec.get("states", [])):
        more, floor = state_diagram(spec, diagram, index, round(floor + BLOCK_GAP, 2))
        elements += more
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
    pieces = deployable_pieces(spec)
    if len(pieces) > 1:
        containers = spec["containers"]
        print(f'Containers: {len(pieces)} pieces in {len(containers["boundaries"])} boundaries, '
              f'{len(containers.get("relations", []))} arrows')
    else:
        print("Containers: not drawn, the product has one deployable piece")
    model = spec.get("data_model", {})
    if model.get("entities"):
        print(f'Data model: {len(model["entities"])} entities, {len(model.get("relations", []))} arrows')
    else:
        print("Data model: not drawn, the spec lists no entities")
    for diagram in spec.get("states", []):
        print(f'States of {diagram["entity"]}: {len(diagram.get("states", []))} states, '
              f'{len(diagram.get("transitions", [])) + 1} arrows')
