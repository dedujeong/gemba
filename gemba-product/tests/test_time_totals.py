import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "skills", "version-close", "scripts", "time_totals.py")

HOUR = 3600


def issue(key, status="Done", estimate=None, spent=None, summary="Do something", kind="Story"):
    """An issue as searchJiraIssuesUsingJql returns it."""
    timetracking = {}
    if estimate is not None:
        timetracking["originalEstimateSeconds"] = estimate
    if spent is not None:
        timetracking["timeSpentSeconds"] = spent
    return {"key": key, "fields": {"summary": summary, "status": {"name": status},
                                   "issuetype": {"name": kind}, "timetracking": timetracking}}


def totals(issues):
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "issues.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"data": {"issues": issues}}, f)
        result = subprocess.run([sys.executable, SCRIPT, path], capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


class TotalsOfAClosedVersion(unittest.TestCase):
    issues = [
        issue("GEMBA-1", estimate=2 * HOUR, spent=3 * HOUR),
        issue("GEMBA-2", estimate=4 * HOUR, spent=2 * HOUR),
    ]

    def run_script(self):
        code, out, err = totals(self.issues)
        self.assertEqual(code, 0, err)
        return json.loads(out)

    def test_each_issue_shows_its_estimate_its_time_and_the_ratio_between_them(self):
        first, second = self.run_script()["issues"]
        self.assertEqual((first["key"], first["estimateSeconds"], first["timeSeconds"], first["ratio"]),
                         ("GEMBA-1", 2 * HOUR, 3 * HOUR, 1.5))
        self.assertEqual((second["key"], second["estimateSeconds"], second["timeSeconds"], second["ratio"]),
                         ("GEMBA-2", 4 * HOUR, 2 * HOUR, 0.5))

    def test_the_total_shows_the_estimate_the_time_and_the_ratio_between_them(self):
        total = self.run_script()["total"]
        self.assertEqual((total["estimateSeconds"], total["timeSeconds"], total["ratio"]),
                         (6 * HOUR, 5 * HOUR, round(5 / 6, 2)))


if __name__ == "__main__":
    unittest.main()
