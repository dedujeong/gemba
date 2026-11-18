import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "skills", "version-close", "scripts", "time_totals.py")

HOUR = 3600


def issue(key, status="Done", estimate=None, spent=None, summary="Do something"):
    """An issue as searchJiraIssuesUsingJql returns it."""
    timetracking = {}
    if estimate is not None:
        timetracking["originalEstimateSeconds"] = estimate
    if spent is not None:
        timetracking["timeSpentSeconds"] = spent
    return {"key": key, "fields": {"summary": summary, "status": {"name": status},
                                   "timetracking": timetracking}}


def totals(issues):
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "issues.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"data": {"issues": issues}}, f)
        result = subprocess.run([sys.executable, SCRIPT, path], capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def result_of(test, issues):
    code, out, err = totals(issues)
    test.assertEqual(code, 0, err)
    return json.loads(out)


class TotalsOfAClosedVersion(unittest.TestCase):
    issues = [
        issue("GEMBA-1", estimate=2 * HOUR, spent=3 * HOUR),
        issue("GEMBA-2", estimate=4 * HOUR, spent=2 * HOUR),
    ]

    def run_script(self):
        return result_of(self, self.issues)

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

    def test_only_the_delivered_issues_count(self):
        result = result_of(self, self.issues + [issue("GEMBA-7", status="Cancelled", estimate=HOUR, spent=HOUR),
                                                issue("GEMBA-8", status="Implement", estimate=HOUR)])
        self.assertEqual([row["key"] for row in result["issues"]], ["GEMBA-1", "GEMBA-2"])
        self.assertEqual(result["total"]["estimateSeconds"], 6 * HOUR)


class AnIssueWithoutWorklog(unittest.TestCase):
    issues = [
        issue("GEMBA-1", estimate=2 * HOUR, spent=3 * HOUR),
        issue("GEMBA-2", estimate=4 * HOUR),
        issue("GEMBA-3", estimate=1 * HOUR, spent=0),
    ]

    def run_script(self):
        return result_of(self, self.issues)

    def test_it_is_marked_as_without_time_and_not_as_zero(self):
        _, without, zero = self.run_script()["issues"]
        self.assertEqual((without["key"], without["timeSeconds"], without["ratio"]), ("GEMBA-2", None, None))
        self.assertEqual((zero["key"], zero["timeSeconds"], zero["ratio"]), ("GEMBA-3", 0, 0.0))

    def test_it_does_not_enter_the_totals_and_the_total_names_it(self):
        total = self.run_script()["total"]
        self.assertEqual((total["estimateSeconds"], total["timeSeconds"], total["ratio"]),
                         (3 * HOUR, 3 * HOUR, 1.0))
        self.assertEqual(total["withoutTime"], ["GEMBA-2"])

    def test_a_null_time_tracking_or_a_zero_estimate_is_without_data_and_does_not_crash(self):
        null = issue("GEMBA-4", estimate=HOUR, spent=HOUR)
        null["fields"]["timetracking"] = None
        result = result_of(self, [null, issue("GEMBA-5", estimate=0, spent=HOUR),
                                  issue("GEMBA-6", estimate=2 * HOUR, spent=HOUR)])
        self.assertEqual([row["ratio"] for row in result["issues"]], [None, None, 0.5])
        self.assertEqual(result["total"]["withoutTime"], ["GEMBA-4"])
        self.assertEqual(result["total"]["withoutEstimate"], ["GEMBA-4", "GEMBA-5"])


class AnIssueWithoutEstimate(unittest.TestCase):
    issues = [
        issue("GEMBA-1", estimate=2 * HOUR, spent=3 * HOUR),
        issue("GEMBA-8", spent=HOUR),
    ]

    def run_script(self):
        return result_of(self, self.issues)

    def test_its_time_enters_the_total_of_time(self):
        self.assertEqual(self.run_script()["total"]["timeSeconds"], 4 * HOUR)

    def test_the_total_names_it_as_without_estimate_and_not_as_without_time(self):
        total = self.run_script()["total"]
        self.assertEqual(total["withoutEstimate"], ["GEMBA-8"])
        self.assertEqual(total["withoutTime"], [])

    def test_a_zero_estimate_is_without_estimate_too(self):
        total = result_of(self, [issue("GEMBA-9", estimate=0, spent=HOUR)])["total"]
        self.assertEqual((total["timeSeconds"], total["withoutEstimate"]), (HOUR, ["GEMBA-9"]))


if __name__ == "__main__":
    unittest.main()
