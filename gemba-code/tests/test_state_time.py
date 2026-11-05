import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "skills", "implement", "scripts", "state_time.py")


def move(created, source, target):
    """A changelog entry that moves the issue from one status to another."""
    return {"id": "1", "created": created,
            "items": [{"field": "status", "fieldId": "status", "fromString": source, "toString": target}]}


def other_edit(created):
    return {"id": "2", "created": created,
            "items": [{"field": "Rank", "fieldId": "customfield_10019", "toString": "Ranked lower"}]}


def state_time(changelog, state, *extra):
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "changelog.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"data": {"values": changelog}}, f)
        result = subprocess.run([sys.executable, SCRIPT, path, state, *extra], capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


class TimeInAState(unittest.TestCase):
    changelog = [
        other_edit("2026-11-04T20:00:00.000-0600"),
        move("2026-11-04T20:50:00.000-0600", "Backlog", "Implement"),
        move("2026-11-04T21:55:00.000-0600", "Implement", "Review"),
        move("2026-11-04T22:10:00.000-0600", "Review", "Done"),
    ]

    def test_the_time_in_the_state_the_issue_left_is_read_from_the_changelog(self):
        code, out, err = state_time(self.changelog, "Implement")
        self.assertEqual(code, 0, err)
        result = json.loads(out)
        self.assertEqual(result["seconds"], 3900)
        self.assertEqual(result["timeSpent"], "1h 5m")

    def test_started_is_when_the_issue_entered_the_state(self):
        code, out, err = state_time(self.changelog, "Implement")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["started"], "2026-11-04T20:50:00.000-0600")

    def test_review_is_computed_the_same_way(self):
        code, out, err = state_time(self.changelog, "Review")
        self.assertEqual(code, 0, err)
        result = json.loads(out)
        self.assertEqual(result["seconds"], 900)
        self.assertEqual(result["timeSpent"], "15m")
        self.assertEqual(result["started"], "2026-11-04T21:55:00.000-0600")


if __name__ == "__main__":
    unittest.main()
