import copy
import os
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "architecture", "scripts")
sys.path.insert(0, SCRIPTS)

import build_architecture  # noqa: E402

NS = "http://www.w3.org/2000/svg"
INTERNAL, EXTERNAL = "#cfe1fd", "#f0f1f2"


def tags(root, tag):
    return list(root.iter("{%s}%s" % (NS, tag)))

SPEC = {
    "product": {"name": "Periplo", "description": "web app para tour operadoras"},
    "context": {
        "description": "Quién usa Periplo y con qué sistemas habla",
        "actors": ["Administrador", "Operaciones", "Ventas"],
        "externals": [{"name": "Mapa base", "description": "proveedor por definir"}],
        "relations": [
            {"from": "Administrador", "to": "Periplo", "label": "crea tours y tarifas"},
            {"from": "Operaciones", "to": "Periplo", "label": "asigna salidas"},
            {"from": "Ventas", "to": "Periplo", "label": "registra ventas"},
            {"from": "Periplo", "to": "Mapa base", "label": "carga el mapa"},
        ],
    },
}


def build(spec):
    return ET.fromstring(build_architecture.build(spec))


def shapes(root, fill=None, shape=None):
    out = []
    for rect in tags(root, "rect"):
        if fill and rect.get("fill") != fill:
            continue
        if shape and rect.get("data-shape") != shape:
            continue
        out.append(rect)
    return out


def texts_of(root):
    return ["".join(t.itertext()).strip() for t in tags(root, "text")]


class ContextDiagram(unittest.TestCase):
    def test_the_svg_parses_and_covers_the_board(self):
        root = build(SPEC)
        self.assertTrue(root.tag.endswith("svg"))
        self.assertIsNotNone(root.get("viewBox"))

    def test_it_has_a_context_heading_with_its_description(self):
        root = build(SPEC)
        heading = [t for t in tags(root, "text") if "Context" in "".join(t.itertext())]
        self.assertEqual(len(heading), 1)
        spans = list(heading[0])
        self.assertEqual(spans[0].text, "Context")
        self.assertEqual(spans[0].get("font-weight"), "bold")
        self.assertIn(SPEC["context"]["description"], "".join(heading[0].itertext()))

    def test_one_actor_box_per_user_with_its_name(self):
        root = build(SPEC)
        actors = [r for r in tags(root, "rect") if r.get("data-type") == "rectangle"]
        self.assertEqual(len(actors), 3)
        for actor in actors:
            self.assertEqual((actor.get("width"), actor.get("height")), ("124", "124"))
            self.assertEqual(actor.get("fill"), INTERNAL)
        names = texts_of(root)
        for name in SPEC["context"]["actors"]:
            self.assertIn(name, names)

    def test_the_actors_are_a_column_at_the_left_of_the_product(self):
        root = build(SPEC)
        actors = [r for r in tags(root, "rect") if r.get("data-type") == "rectangle"]
        xs = {float(a.get("x")) for a in actors}
        ys = sorted(float(a.get("y")) for a in actors)
        self.assertEqual(len(xs), 1)
        self.assertEqual(len(set(ys)), 3)
        product = shapes(root, shape="process")[0]
        self.assertLess(xs.pop() + 124, float(product.get("x")))

    def test_the_product_is_an_internal_box_with_only_its_name(self):
        root = build(SPEC)
        product = [r for r in shapes(root, shape="process") if r.get("fill") == INTERNAL]
        self.assertEqual(len(product), 1)
        self.assertEqual((product[0].get("width"), product[0].get("height")), ("220", "160"))
        label = [t for t in tags(root, "text") if t.get("belongs-to") == product[0].get("id")]
        self.assertEqual(len(label), 1)
        self.assertEqual("".join(label[0].itertext()).strip(), "Periplo")

    def test_an_external_system_is_gray(self):
        root = build(SPEC)
        external = shapes(root, fill=EXTERNAL, shape="process")
        self.assertEqual(len(external), 1)
        label = [t for t in tags(root, "text") if t.get("belongs-to") == external[0].get("id")]
        self.assertIn("Mapa base", "".join(label[0].itertext()))

    def test_one_arrow_with_its_label_per_relation(self):
        root = build(SPEC)
        connectors = [p for p in tags(root, "polyline") if p.get("data-type") == "connector"]
        self.assertEqual(len(connectors), len(SPEC["context"]["relations"]))
        labels = [t for t in tags(root, "text") if t.get("data-type") == "pathLabel"]
        self.assertEqual(len(labels), len(SPEC["context"]["relations"]))
        said = ["".join(t.itertext()).strip() for t in labels]
        for relation in SPEC["context"]["relations"]:
            self.assertIn(relation["label"], said)

    def test_every_arrow_joins_two_elements_of_the_board(self):
        root = build(SPEC)
        ids = {e.get("id") for e in tags(root, "rect")}
        for connector in [p for p in tags(root, "polyline") if p.get("data-type") == "connector"]:
            self.assertIn(connector.get("begins-at"), ids)
            self.assertIn(connector.get("ends-at"), ids)
            self.assertEqual(connector.get("line-type"), "angled")
            self.assertTrue(connector.get("marker-end", "").startswith("url(#"))
            for side in ("start", "end"):
                self.assertEqual(connector.get(f"{side}-proportion"), "0.5")
                self.assertIn(connector.get(f"{side}-anchor"), {"left", "right", "top", "bottom"})

    def test_the_arrowhead_is_defined_once_with_its_ids(self):
        root = build(SPEC)
        defs = list(tags(root, "defs"))
        self.assertEqual(len(defs), 1)
        self.assertIsNotNone(defs[0].get("id"))
        markers = list(tags(defs[0], "marker"))
        self.assertEqual(len(markers), 1)
        polygons = list(tags(markers[0], "polygon"))
        self.assertEqual(len(polygons), 1)
        self.assertIsNotNone(polygons[0].get("id"))
        used = {p.get("marker-end") for p in tags(root, "polyline")}
        self.assertEqual(used, {f'url(#{markers[0].get("id")})'})

    def test_a_relation_to_an_element_that_is_not_there_is_rejected(self):
        spec = copy.deepcopy(SPEC)
        spec["context"]["relations"].append({"from": "Periplo", "to": "Cobros", "label": "cobra"})
        with self.assertRaises(ValueError) as caught:
            build_architecture.build(spec)
        self.assertIn("Cobros", str(caught.exception))

    def test_a_relation_with_no_label_is_rejected(self):
        spec = copy.deepcopy(SPEC)
        spec["context"]["relations"][0] = {"from": "Administrador", "to": "Periplo"}
        with self.assertRaises(ValueError) as caught:
            build_architecture.build(spec)
        self.assertIn("Administrador", str(caught.exception))


CONTAINERS = {
    "description": "Qué corre dónde y de qué se encarga cada parte",
    "boundaries": [
        {"name": "Cloudflare Pages (gratuito)",
         "containers": [{"name": "Web app", "description": "SPA en React y TypeScript"}]},
        {"name": "Supabase (plan gratuito)",
         "containers": [
             {"name": "Postgres", "description": "agency_id y RLS", "shape": "database"},
             {"name": "Auth", "description": "acceso, un rol por usuario"},
         ]},
    ],
    "externals": [{"name": "Sentry", "description": "alertas de errores"}],
    "relations": [
        {"from": "Web app", "to": "Postgres", "label": "lee y escribe por HTTPS"},
        {"from": "Web app", "to": "Auth", "label": "inicia sesión"},
        {"from": "Web app", "to": "Sentry", "label": "reporta errores"},
    ],
}


def with_containers(boundaries=None):
    spec = copy.deepcopy(SPEC)
    spec["containers"] = copy.deepcopy(CONTAINERS)
    if boundaries is not None:
        spec["containers"]["boundaries"] = boundaries
    return spec


def headings(root):
    return {
        "".join(list(t)[0].itertext()): float(t.get("y"))
        for t in tags(root, "text")
        if t.get("data-type") == "text" and list(t) and list(t)[0].get("font-weight") == "bold"
    }


class NamesOnly(unittest.TestCase):
    """A box of the Context and Containers diagrams carries its name and nothing else, even when the spec describes it."""

    def test_every_box_says_only_its_name(self):
        root = build(with_containers())
        names = {SPEC["product"]["name"]} | {e["name"] for e in SPEC["context"]["externals"]}
        names |= {c["name"] for b in CONTAINERS["boundaries"] for c in b["containers"]}
        names |= {e["name"] for e in CONTAINERS["externals"]}
        boxes = {r.get("id") for r in shapes(root)}
        said = ["".join(t.itertext()).strip() for t in tags(root, "text") if t.get("belongs-to") in boxes]
        self.assertEqual(len(said), len(names))
        for text in said:
            self.assertIn(text, names)


class NoLegendOrNotes(unittest.TestCase):
    """A diagram stands on its own: besides its heading, its boxes and its arrows, nothing is written beside it."""

    def test_every_text_is_a_heading_a_name_or_an_arrow_label(self):
        spec = with_states()
        spec["containers"] = copy.deepcopy(CONTAINERS)
        root = build(spec)
        shape_ids = {e.get("id") for e in tags(root, "rect")}
        for text in tags(root, "text"):
            heading = text.get("data-type") == "text" and list(text) and list(text)[0].get("font-weight") == "bold"
            actor_name = text.get("data-type") == "text" and text.get("id", "").endswith("-name")
            box = text.get("belongs-to") in shape_ids
            arrow = text.get("data-type") == "pathLabel"
            self.assertTrue(heading or actor_name or box or arrow, "".join(text.itertext()))


class ContainersDiagram(unittest.TestCase):
    def test_it_has_a_containers_heading_with_its_description(self):
        root = build(with_containers())
        self.assertIn("Containers", headings(root))
        said = [t for t in tags(root, "text") if "Containers" in "".join(t.itertext())]
        self.assertIn(CONTAINERS["description"], "".join(said[0].itertext()))

    def test_one_boundary_section_per_place_with_its_title(self):
        root = build(with_containers())
        sections = [r for r in tags(root, "rect") if r.get("data-type") == "section"]
        self.assertEqual([s.get("data-title") for s in sections],
                         [b["name"] for b in CONTAINERS["boundaries"]])

    def test_each_piece_sits_inside_its_boundary(self):
        root = build(with_containers())
        sections = {s.get("id"): s for s in tags(root, "rect") if s.get("data-type") == "section"}
        pieces = [r for r in tags(root, "rect")
                  if r.get("data-type") == "shape" and r.get("belongs-to") in sections]
        self.assertEqual(len(pieces), 3)
        for piece in pieces:
            section = sections[piece.get("belongs-to")]
            self.assertGreaterEqual(float(piece.get("x")), float(section.get("x")))
            self.assertGreaterEqual(float(piece.get("y")), float(section.get("y")))
            self.assertLessEqual(float(piece.get("x")) + 220, float(section.get("x")) + float(section.get("width")))
            self.assertLessEqual(float(piece.get("y")) + 160, float(section.get("y")) + float(section.get("height")))

    def test_a_store_is_drawn_as_a_database(self):
        root = build(with_containers())
        stores = [r for r in tags(root, "rect") if r.get("data-shape") == "database"]
        self.assertEqual(len(stores), 1)
        label = [t for t in tags(root, "text") if t.get("belongs-to") == stores[0].get("id")]
        self.assertIn("Postgres", "".join(label[0].itertext()))

    def test_the_containers_diagram_sits_below_the_context_one(self):
        root = build(with_containers())
        marks = headings(root)
        self.assertGreater(marks["Containers"], marks["Context"])
        context_bottom = max(float(r.get("y")) + float(r.get("height"))
                             for r in tags(root, "rect") if r.get("id", "").startswith("ctx-"))
        container_top = min(float(r.get("y")) for r in tags(root, "rect") if r.get("id", "").startswith("con-"))
        self.assertGreater(container_top, context_bottom)

    def test_an_external_system_of_the_diagram_is_gray(self):
        root = build(with_containers())
        gray = [r for r in tags(root, "rect")
                if r.get("fill") == EXTERNAL and r.get("id", "").startswith("con-")]
        self.assertEqual(len(gray), 1)

    def test_one_arrow_with_its_label_per_relation(self):
        root = build(with_containers())
        connectors = [p for p in tags(root, "polyline") if p.get("id", "").startswith("con-")]
        self.assertEqual(len(connectors), len(CONTAINERS["relations"]))
        said = ["".join(t.itertext()).strip() for t in tags(root, "text")
                if t.get("data-type") == "pathLabel" and t.get("id", "").startswith("con-")]
        for relation in CONTAINERS["relations"]:
            self.assertIn(relation["label"], said)

    def test_a_single_piece_gets_no_containers_diagram(self):
        spec = with_containers(boundaries=[
            {"name": "Cloudflare Pages (gratuito)", "containers": [{"name": "Web app", "description": "todo"}]}])
        spec["containers"]["relations"] = []
        root = build(spec)
        self.assertNotIn("Containers", headings(root))
        self.assertEqual([r for r in tags(root, "rect") if r.get("data-type") == "section"], [])

    def test_a_product_with_no_containers_gets_no_containers_diagram(self):
        root = build(SPEC)
        self.assertNotIn("Containers", headings(root))

    def test_an_arrow_to_an_element_of_the_other_diagram_is_rejected(self):
        spec = with_containers()
        spec["containers"]["relations"].append(
            {"from": "Web app", "to": "Administrador", "label": "le muestra el kanban"})
        with self.assertRaises(ValueError) as caught:
            build_architecture.build(spec)
        self.assertIn("Administrador", str(caught.exception))


DATA_MODEL = {
    "description": "Qué se guarda y cómo se relaciona",
    "entities": [
        {"name": "Clase", "fields": ["id", "nombre", "horario", "cupo"]},
        {"name": "Reserva", "fields": ["id", "clase_id", "nombre", "teléfono"]},
        {"name": "Dueña", "fields": ["id", "correo"]},
    ],
    "relations": [
        {"from": "Reserva", "to": "Clase", "label": "muchas reservas por clase"},
        {"from": "Dueña", "to": "Clase", "label": "administra muchas clases"},
    ],
}


def with_data_model(**changes):
    spec = copy.deepcopy(SPEC)
    spec["data_model"] = copy.deepcopy(DATA_MODEL)
    spec["data_model"].update(changes)
    return spec


class DataModelDiagram(unittest.TestCase):
    def test_it_has_a_data_model_heading_with_its_description(self):
        root = build(with_data_model())
        self.assertIn("Data model", headings(root))
        said = [t for t in tags(root, "text") if "Data model" in "".join(t.itertext())]
        self.assertIn(DATA_MODEL["description"], "".join(said[0].itertext()))

    def test_one_box_per_entity_with_its_fields(self):
        root = build(with_data_model())
        boxes = [r for r in shapes(root, shape="process") if r.get("id", "").startswith("dat-")]
        self.assertEqual(len(boxes), len(DATA_MODEL["entities"]))
        said = {}
        for box in boxes:
            label = [t for t in tags(root, "text") if t.get("belongs-to") == box.get("id")]
            said[box.get("id")] = "".join(label[0].itertext())
        for entity in DATA_MODEL["entities"]:
            text = next(v for v in said.values() if v.startswith(entity["name"]))
            for field in entity["fields"]:
                self.assertIn(field, text)

    def test_one_arrow_with_its_label_per_relation(self):
        root = build(with_data_model())
        connectors = [p for p in tags(root, "polyline") if p.get("id", "").startswith("dat-")]
        self.assertEqual(len(connectors), len(DATA_MODEL["relations"]))
        said = ["".join(t.itertext()).strip() for t in tags(root, "text")
                if t.get("data-type") == "pathLabel" and t.get("id", "").startswith("dat-")]
        for relation in DATA_MODEL["relations"]:
            self.assertIn(relation["label"], said)

    def test_every_arrow_joins_two_boxes_of_the_diagram(self):
        root = build(with_data_model())
        ids = {r.get("id") for r in tags(root, "rect") if r.get("id", "").startswith("dat-")}
        for connector in [p for p in tags(root, "polyline") if p.get("id", "").startswith("dat-")]:
            self.assertIn(connector.get("begins-at"), ids)
            self.assertIn(connector.get("ends-at"), ids)

    def test_the_boxes_of_a_row_leave_room_for_the_label_of_their_arrow(self):
        root = build(with_data_model())
        a, b = [r for r in tags(root, "rect") if r.get("id") in ("dat-b0", "dat-b1")]
        gap = float(b.get("x")) - (float(a.get("x")) + float(a.get("width")))
        longest = max(len(r["label"]) for r in DATA_MODEL["relations"])
        self.assertGreaterEqual(gap, longest * 9)

    def test_the_data_model_sits_below_the_context_diagram(self):
        root = build(with_data_model())
        y = headings(root)
        self.assertGreater(y["Data model"], y["Context"])

    def test_the_data_model_sits_below_containers_when_there_are_some(self):
        spec = with_containers()
        spec["data_model"] = copy.deepcopy(DATA_MODEL)
        y = headings(build(spec))
        self.assertGreater(y["Data model"], y["Containers"])

    def test_a_relation_to_an_entity_that_is_not_there_is_rejected(self):
        spec = with_data_model()
        spec["data_model"]["relations"].append({"from": "Reserva", "to": "Pago", "label": "se paga con"})
        with self.assertRaises(ValueError) as caught:
            build_architecture.build(spec)
        self.assertIn("Pago", str(caught.exception))

    def test_an_entity_with_no_fields_is_rejected(self):
        spec = with_data_model()
        spec["data_model"]["entities"].append({"name": "Pago", "fields": []})
        with self.assertRaises(ValueError) as caught:
            build_architecture.build(spec)
        self.assertIn("Pago", str(caught.exception))

    def test_a_relation_with_no_label_is_rejected(self):
        spec = with_data_model()
        spec["data_model"]["relations"][0] = {"from": "Reserva", "to": "Clase"}
        with self.assertRaises(ValueError) as caught:
            build_architecture.build(spec)
        self.assertIn("Reserva", str(caught.exception))

    def test_a_spec_with_no_data_model_gets_no_data_model_diagram(self):
        self.assertNotIn("Data model", headings(build(SPEC)))

    def test_a_data_model_with_no_entities_gets_no_diagram(self):
        root = build(with_data_model(entities=[], relations=[]))
        self.assertNotIn("Data model", headings(root))


RESERVA = {
    "entity": "Reserva",
    "description": "Cómo cambia una reserva",
    "initial": {"state": "Apartada", "event": "la alumna aparta su lugar"},
    "states": ["Apartada", "Cancelada", "Asistida"],
    "transitions": [
        {"from": "Apartada", "to": "Cancelada", "event": "la alumna cancela su lugar"},
        {"from": "Apartada", "to": "Asistida", "event": "la dueña marca la asistencia"},
    ],
}


def with_states(*diagrams):
    spec = with_data_model()
    spec["states"] = [copy.deepcopy(d) for d in (diagrams or [RESERVA])]
    return spec


def of(root, prefix, tag):
    return [e for e in tags(root, tag) if e.get("id", "").startswith(prefix)]


class StateDiagram(unittest.TestCase):
    def test_it_has_a_heading_naming_the_entity_with_its_description(self):
        root = build(with_states())
        self.assertIn("States of Reserva", headings(root))
        said = [t for t in tags(root, "text") if "States of Reserva" in "".join(t.itertext())]
        self.assertIn(RESERVA["description"], "".join(said[0].itertext()))

    def test_one_box_per_state(self):
        root = build(with_states())
        boxes = [r for r in of(root, "st0-", "rect") if r.get("data-shape") == "process"]
        self.assertEqual(len(boxes), len(RESERVA["states"]))
        said = ["".join(t.itertext()).strip() for t in tags(root, "text") if t.get("belongs-to") in {b.get("id") for b in boxes}]
        for state in RESERVA["states"]:
            self.assertIn(state, said)

    def test_one_arrow_with_its_event_per_transition_and_one_for_the_start(self):
        root = build(with_states())
        connectors = of(root, "st0-", "polyline")
        self.assertEqual(len(connectors), len(RESERVA["transitions"]) + 1)
        said = ["".join(t.itertext()).strip() for t in tags(root, "text")
                if t.get("data-type") == "pathLabel" and t.get("id", "").startswith("st0-")]
        for transition in RESERVA["transitions"]:
            self.assertIn(transition["event"], said)
        self.assertIn(RESERVA["initial"]["event"], said)

    def test_the_start_arrow_ends_at_the_initial_state(self):
        root = build(with_states())
        initial = next(t for t in tags(root, "text")
                       if "".join(t.itertext()).strip() == "Apartada" and t.get("belongs-to"))
        start = [c for c in of(root, "st0-", "polyline") if c.get("id").endswith("-r1")][0]
        self.assertEqual(start.get("ends-at"), initial.get("belongs-to"))

    def test_each_entity_with_states_gets_its_own_diagram(self):
        clase = {"entity": "Clase", "description": "Cómo cambia una clase",
                 "initial": {"state": "Abierta", "event": "la dueña la publica"},
                 "states": ["Abierta", "Llena"],
                 "transitions": [{"from": "Abierta", "to": "Llena", "event": "se ocupa el último lugar"}]}
        root = build(with_states(RESERVA, clase))
        y = headings(root)
        self.assertIn("States of Reserva", y)
        self.assertIn("States of Clase", y)
        self.assertGreater(y["States of Clase"], y["States of Reserva"])

    def test_the_states_of_a_row_leave_room_for_the_label_of_their_arrow(self):
        root = build(with_states())
        boxes = sorted([r for r in of(root, "st0-", "rect") if r.get("data-shape") == "process"],
                       key=lambda r: float(r.get("x")))
        gap = float(boxes[1].get("x")) - (float(boxes[0].get("x")) + float(boxes[0].get("width")))
        longest = max(len(t["event"]) for t in RESERVA["transitions"])
        self.assertGreaterEqual(gap, longest * 9)

    def test_the_start_marker_leaves_room_for_the_label_of_its_arrow(self):
        root = build(with_states())
        start = next(r for r in tags(root, "rect") if r.get("id") == "st0-start")
        first = next(r for r in tags(root, "rect") if r.get("id") == "st0-b1")
        gap = float(first.get("x")) - (float(start.get("x")) + float(start.get("width")))
        self.assertGreaterEqual(gap, len(RESERVA["initial"]["event"]) * 9)

    def test_the_states_sit_below_the_data_model(self):
        y = headings(build(with_states()))
        self.assertGreater(y["States of Reserva"], y["Data model"])

    def test_a_transition_with_no_event_is_rejected(self):
        bad = copy.deepcopy(RESERVA)
        bad["transitions"][0] = {"from": "Apartada", "to": "Cancelada"}
        with self.assertRaises(ValueError) as caught:
            build_architecture.build(with_states(bad))
        self.assertIn("Apartada", str(caught.exception))

    def test_a_transition_to_an_unknown_state_is_rejected(self):
        bad = copy.deepcopy(RESERVA)
        bad["transitions"].append({"from": "Apartada", "to": "Pagada", "event": "paga"})
        with self.assertRaises(ValueError) as caught:
            build_architecture.build(with_states(bad))
        self.assertIn("Pagada", str(caught.exception))

    def test_an_initial_state_that_is_not_listed_is_rejected(self):
        bad = copy.deepcopy(RESERVA)
        bad["initial"]["state"] = "Pagada"
        with self.assertRaises(ValueError) as caught:
            build_architecture.build(with_states(bad))
        self.assertIn("Pagada", str(caught.exception))

    def test_an_entity_that_is_not_in_the_data_model_is_rejected(self):
        bad = copy.deepcopy(RESERVA)
        bad["entity"] = "Pago"
        with self.assertRaises(ValueError) as caught:
            build_architecture.build(with_states(bad))
        self.assertIn("Pago", str(caught.exception))

    def test_a_spec_with_no_states_draws_none(self):
        y = headings(build(with_data_model()))
        self.assertFalse([h for h in y if h.startswith("States of")])


if __name__ == "__main__":
    unittest.main()
