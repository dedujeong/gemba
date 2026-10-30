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

PERSONA, ACTIVITY, TASK = "#eed7fc", "#baf3db", "#cfe1fd"
CURRENT, LATER, OPEN = "#fce4a6", "#f0f1f2", "#ffd5d2"

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
        self.assertEqual(texts["Import dates from the notebook"], LATER)

    def test_open_question_is_red_in_any_release(self):
        texts = stickies(build_story_map.build(SPEC))
        self.assertEqual(texts["Who sends it when the owner is away?"], OPEN)


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

    def test_trace_table_lists_each_mvp_story_with_its_origin(self):
        self.assertEqual(
            build_story_map.trace_table(SPEC),
            [("Save a date per customer", "Primary job"), ("Send a WhatsApp reminder", "Problem")],
        )


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
