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

    def test_the_product_is_an_internal_box_with_its_description(self):
        root = build(SPEC)
        product = [r for r in shapes(root, shape="process") if r.get("fill") == INTERNAL]
        self.assertEqual(len(product), 1)
        self.assertEqual((product[0].get("width"), product[0].get("height")), ("220", "160"))
        label = [t for t in tags(root, "text") if t.get("belongs-to") == product[0].get("id")]
        self.assertEqual(len(label), 1)
        said = "".join(label[0].itertext())
        self.assertIn("Periplo", said)
        self.assertIn("web app para tour operadoras", said)

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


if __name__ == "__main__":
    unittest.main()
