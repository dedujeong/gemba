import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "story-map", "scripts")
sys.path.insert(0, SCRIPTS)

import build_story_map  # noqa: E402

PERSONA, ACTIVITY, TASK = "#f5e989", "#eed7fc", "#cfe1fd"
CURRENT, NEXT, LATER, RELEASED, OPEN = "#baf3db", "#fce4a6", "#fff5db", "#f0f1f2", "#ffd5d2"

# The closed sticky palette of Confluence: a fill outside it is snapped to the nearest one.
PALETTE = {
    "#e9f2fe", "#cfe1fd", "#adcbfb", "#e7f9ff", "#c6edfb", "#b1e4f7",
    "#dcfff1", "#baf3db", "#97edc9", "#efffd6", "#d3f1a7", "#bde97c",
    "#fef7c8", "#f5e989", "#efdd4e", "#fff5db", "#fce4a6", "#fbd779",
    "#ffeceb", "#ffd5d2", "#ffb8b2", "#ffecf8", "#fdd0ec", "#fcb6e1",
    "#f8eefe", "#eed7fc", "#e3bdfa", "#ffffff", "#f0f1f2", "#b7b9be",
}

SPEC = {
    "title": "Reminders",
    "vision": "An app that sends maintenance reminders so customers come back on time.",
    "labels": {
        "persona": "Who uses the product.",
        "activities": "What happens, in order.",
        "tasks": "The steps inside each activity.",
    },
    "personas": ["Shop owner (primary)", "Customer"],
    "activities": [{"column": 0, "text": "Record a service"}, {"column": 1, "text": "Remind"}],
    "tasks": ["Save the next service date", "Send the reminder"],
    "releases": [
        {
            "name": "MVP",
            "description": "What the first release achieves for the shop owner.",
            "stories": [
                [{"text": "Save a date per customer", "traces": "Primary job"}],
                [
                    {"text": "Send a WhatsApp reminder", "traces": "Problem"},
                    {"text": "Who sends it when the owner is away?", "open": True},
                ],
            ],
        },
        {
            "name": "Release 2",
            "description": "What does not enter the first release.",
            "stories": [["Import dates from the notebook"], []],
        },
    ],
}

def delivered_first(spec):
    """The same map once the MVP shipped: Release 2 becomes the current release and must trace to the brief."""
    spec = copy.deepcopy(spec)
    spec["releases"][0]["released"] = True
    spec["releases"][0]["stories"] = [["Delivered story"], []]
    spec["releases"][1]["stories"] = [[{"text": "Import dates from the notebook", "traces": "Problem"}], []]
    return spec


NS = {"s": "http://www.w3.org/2000/svg"}


def stickies(svg):
    """Return {text: fill} for every sticky on the board."""
    root = ET.fromstring(svg)
    fills = {el.get("id"): el.get("fill") for el in root.iter("{%s}rect" % NS["s"]) if el.get("data-type") == "sticky"}
    out = {}
    for el in root.iter("{%s}text" % NS["s"]):
        owner = el.get("belongs-to")
        if owner in fills:
            out[("".join(el.itertext())).strip()] = fills[owner]
    return out


def labels(svg):
    root = ET.fromstring(svg)
    return ["".join(el.itertext()) for el in root.iter("{%s}text" % NS["s"]) if el.get("data-type") == "text"]


class BoardContent(unittest.TestCase):
    def test_board_shows_personas_activities_tasks_and_releases(self):
        svg = build_story_map.build(SPEC)
        texts = stickies(svg)
        for expected in [
            "Shop owner (primary)", "Customer",
            "Record a service", "Remind",
            "Save the next service date", "Send the reminder",
            "Save a date per customer", "Send a WhatsApp reminder",
            "Import dates from the notebook",
        ]:
            self.assertIn(expected, texts)
        joined = " ".join(labels(svg))
        for row in ["User persona", "Activities", "Tasks", "MVP", "Release 2"]:
            self.assertIn(row, joined)

    def test_more_story_columns_than_tasks_is_rejected(self):
        spec = copy.deepcopy(SPEC)
        spec["releases"][1]["stories"].append(["one column too many"])
        with self.assertRaises(ValueError):
            build_story_map.build(spec)


class FixedColors(unittest.TestCase):
    def test_each_row_uses_its_fixed_color(self):
        texts = stickies(build_story_map.build(SPEC))
        self.assertEqual(texts["Shop owner (primary)"], PERSONA)
        self.assertEqual(texts["Customer"], PERSONA)
        self.assertEqual(texts["Record a service"], ACTIVITY)
        self.assertEqual(texts["Save the next service date"], TASK)
        self.assertEqual(texts["Save a date per customer"], CURRENT)
        self.assertEqual(texts["Import dates from the notebook"], NEXT)

    def test_releases_are_current_next_then_later_by_position(self):
        spec = copy.deepcopy(SPEC)
        spec["releases"] += [
            {"name": "Release 3", "stories": [["Third story"], []]},
            {"name": "Release 4", "stories": [["Fourth story"], []]},
        ]
        texts = stickies(build_story_map.build(spec))
        self.assertEqual(
            [texts[t] for t in ["Save a date per customer", "Import dates from the notebook", "Third story", "Fourth story"]],
            [CURRENT, NEXT, LATER, LATER],
        )

    def test_a_delivered_release_is_gray_and_the_rest_shift_up(self):
        texts = stickies(build_story_map.build(delivered_first(SPEC)))
        self.assertEqual(texts["Delivered story"], RELEASED)
        self.assertEqual(texts["Import dates from the notebook"], CURRENT)

    def test_open_question_is_red_in_any_release(self):
        texts = stickies(build_story_map.build(SPEC))
        self.assertEqual(texts["Who sends it when the owner is away?"], OPEN)
        spec = delivered_first(SPEC)
        spec["releases"][0]["stories"][1] = [{"text": "Delivered open question", "open": True}]
        self.assertEqual(stickies(build_story_map.build(spec))["Delivered open question"], OPEN)

    def test_every_fill_written_belongs_to_the_confluence_palette(self):
        spec = delivered_first(SPEC)
        spec["releases"] += [{"name": "Release 3", "stories": [["Third story"], []]},
                             {"name": "Release 4", "stories": [["Fourth story"], []]}]
        fills = set(stickies(build_story_map.build(spec)).values())
        self.assertEqual(fills - PALETTE, set())
        self.assertEqual(fills, {PERSONA, ACTIVITY, TASK, RELEASED, CURRENT, NEXT, LATER})


class LabelAlignment(unittest.TestCase):
    def test_each_release_label_is_level_with_the_first_row_of_its_stickies(self):
        spec = copy.deepcopy(SPEC)
        spec["releases"].append({"name": "Later", "description": "Not assigned to a release yet.", "stories": [[], ["Some day"]]})
        svg = build_story_map.build(spec)
        root = ET.fromstring(svg)
        ys = {}
        for el in root.iter("{%s}rect" % NS["s"]):
            ys[el.get("id")] = float(el.get("y"))
        sticky_y = {}
        for el in root.iter("{%s}text" % NS["s"]):
            if el.get("belongs-to") in ys:
                sticky_y[("".join(el.itertext())).strip()] = ys[el.get("belongs-to")]
        tops = {}
        for el in root.iter("{%s}text" % NS["s"]):
            if (el.get("id") or "").startswith("label-release-"):
                i = int(el.get("id").rsplit("-", 1)[1])
                height = build_story_map.label_height(spec["releases"][i]["description"])
                tops[i] = round(float(el.get("y")) - height / 2, 2)
        first_rows = {}
        for i, release in enumerate(spec["releases"]):
            texts = [build_story_map.split_story(st)[0] for column in release["stories"] for st in column]
            first_rows[i] = min(sticky_y[t] for t in texts)
        self.assertEqual(tops, first_rows)


class Traceability(unittest.TestCase):
    def test_mvp_story_without_traces_is_rejected(self):
        spec = copy.deepcopy(SPEC)
        spec["releases"][0]["stories"][0] = [{"text": "Save a date per customer"}]
        with self.assertRaises(ValueError) as ctx:
            build_story_map.build(spec)
        self.assertIn("Save a date per customer", str(ctx.exception))

    def test_plain_text_mvp_story_is_rejected(self):
        spec = copy.deepcopy(SPEC)
        spec["releases"][0]["stories"][0] = ["Save a date per customer"]
        with self.assertRaises(ValueError):
            build_story_map.build(spec)

    def test_open_question_and_later_stories_need_no_traces(self):
        build_story_map.build(SPEC)

    def test_traces_are_required_on_the_current_release_not_on_a_delivered_one(self):
        spec = delivered_first(SPEC)
        build_story_map.build(spec)
        spec["releases"][1]["stories"][0] = ["Import dates from the notebook"]
        with self.assertRaises(ValueError) as ctx:
            build_story_map.build(spec)
        self.assertIn("Import dates from the notebook", str(ctx.exception))
        self.assertEqual(build_story_map.trace_table(delivered_first(SPEC)),
                         [("Import dates from the notebook", "Problem")])

    def test_trace_table_lists_each_mvp_story_with_its_origin(self):
        self.assertEqual(
            build_story_map.trace_table(SPEC),
            [("Save a date per customer", "Primary job"), ("Send a WhatsApp reminder", "Problem")],
        )


class ReleaseNames(unittest.TestCase):
    """The reader finds a row by its label, so two rows must never share one or take a backbone label."""

    def test_two_releases_with_the_same_name_are_rejected(self):
        spec = copy.deepcopy(SPEC)
        spec["releases"][1]["name"] = "MVP"
        with self.assertRaises(ValueError) as ctx:
            build_story_map.build(spec)
        self.assertIn("MVP", str(ctx.exception))

    def test_a_release_named_like_a_backbone_row_is_rejected(self):
        for name in ["User persona", "Activities", "Tasks"]:
            spec = copy.deepcopy(SPEC)
            spec["releases"][1]["name"] = name
            with self.assertRaises(ValueError) as ctx:
                build_story_map.build(spec)
            self.assertIn(name, str(ctx.exception))


class Template(unittest.TestCase):
    def test_the_shipped_template_builds(self):
        path = os.path.join(ROOT, "skills", "story-map", "assets", "story-map-template.json")
        with open(path, encoding="utf-8") as f:
            spec = json.load(f)
        ET.fromstring(build_story_map.build(spec))


class CommandLine(unittest.TestCase):
    def test_writes_the_svg_and_reports_counts_and_traces(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec_path, svg_path = os.path.join(tmp, "spec.json"), os.path.join(tmp, "map.svg")
            with open(spec_path, "w", encoding="utf-8") as f:
                json.dump(SPEC, f)
            run = subprocess.run(
                [sys.executable, "-I", os.path.join(SCRIPTS, "build_story_map.py"), spec_path, svg_path],
                capture_output=True, text=True,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            ET.parse(svg_path)
            self.assertIn("MVP=3", run.stdout)
            self.assertIn("Save a date per customer", run.stdout)
            self.assertIn("Primary job", run.stdout)


if __name__ == "__main__":
    unittest.main()
