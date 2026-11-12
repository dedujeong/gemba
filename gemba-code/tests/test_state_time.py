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


class TimeInAStateEnteredTwice(unittest.TestCase):
    changelog = [
        move("2026-11-04T20:00:00.000-0600", "Backlog", "Implement"),
        move("2026-11-04T20:40:00.000-0600", "Implement", "Review"),
        move("2026-11-04T20:50:00.000-0600", "Review", "Implement"),
        move("2026-11-04T21:20:00.000-0600", "Implement", "Review"),
    ]

    def test_only_the_last_span_counts_because_the_first_was_logged_when_it_ended(self):
        code, out, err = state_time(self.changelog, "Implement")
        self.assertEqual(code, 0, err)
        result = json.loads(out)
        self.assertEqual(result["seconds"], 1800)
        self.assertEqual(result["timeSpent"], "30m")

    def test_started_is_when_the_last_span_began(self):
        code, out, err = state_time(self.changelog, "Implement")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["started"], "2026-11-04T20:50:00.000-0600")

    def test_the_time_out_of_the_state_between_the_spans_is_not_counted(self):
        code, out, err = state_time(self.changelog, "Review", "--now", "2026-11-04T21:25:00.000-0600")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["seconds"], 300)


class TimeInAStateNotLeftYet(unittest.TestCase):
    changelog = [
        move("2026-11-04T20:00:00.000-0600", "Backlog", "Implement"),
    ]

    def test_the_time_runs_until_the_given_moment(self):
        code, out, err = state_time(self.changelog, "Implement", "--now", "2026-11-04T20:20:00.000-0600")
        self.assertEqual(code, 0, err)
        result = json.loads(out)
        self.assertEqual(result["seconds"], 1200)
        self.assertEqual(result["timeSpent"], "20m")

    def test_without_a_given_moment_the_time_runs_until_now(self):
        code, out, err = state_time(self.changelog, "Implement")
        self.assertEqual(code, 0, err)
        self.assertGreater(json.loads(out)["seconds"], 1200)

    def test_a_span_left_open_counts_alone_after_a_closed_one(self):
        changelog = [
            move("2026-11-04T20:00:00.000-0600", "Backlog", "Implement"),
            move("2026-11-04T20:30:00.000-0600", "Implement", "Review"),
            move("2026-11-04T20:40:00.000-0600", "Review", "Implement"),
        ]
        code, out, err = state_time(changelog, "Implement", "--now", "2026-11-04T20:55:00.000-0600")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["seconds"], 900)


class AnIssueBackFromReview(unittest.TestCase):
    """Implement, Review, back to Implement, Review again, Done: each log takes only what was not logged."""
    changelog = [
        move("2026-11-04T20:00:00.000-0600", "Backlog", "Implement"),
        move("2026-11-04T21:00:00.000-0600", "Implement", "Review"),
        move("2026-11-04T21:10:00.000-0600", "Review", "Implement"),
        move("2026-11-04T21:30:00.000-0600", "Implement", "Review"),
        move("2026-11-04T21:45:00.000-0600", "Review", "Done"),
    ]

    def test_review_returning_the_issue_logs_the_span_that_just_closed(self):
        code, out, err = state_time(self.changelog[:3], "Review", "--now", "2026-11-04T21:11:00.000-0600")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["seconds"], 600)

    def test_the_second_implement_log_has_only_the_second_span(self):
        code, out, err = state_time(self.changelog[:3], "Implement", "--now", "2026-11-04T21:30:00.000-0600")
        self.assertEqual(code, 0, err)
        result = json.loads(out)
        self.assertEqual(result["seconds"], 1200)
        self.assertEqual(result["started"], "2026-11-04T21:10:00.000-0600")

    def test_close_logs_only_the_last_review(self):
        code, out, err = state_time(self.changelog[:4], "Review", "--now", "2026-11-04T21:45:00.000-0600")
        self.assertEqual(code, 0, err)
        result = json.loads(out)
        self.assertEqual(result["seconds"], 900)
        self.assertEqual(result["started"], "2026-11-04T21:30:00.000-0600")


class StateNeverEntered(unittest.TestCase):
    def test_it_fails_instead_of_printing_a_zero_time(self):
        changelog = [move("2026-11-04T20:00:00.000-0600", "Backlog", "Implement")]
        code, out, err = state_time(changelog, "Review")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("Review", err)


if __name__ == "__main__":
    unittest.main()
