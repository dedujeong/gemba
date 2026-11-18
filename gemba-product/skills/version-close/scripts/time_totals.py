"""Print the estimate, the recorded time and the ratio between them, per issue and in total.

Usage: python3 time_totals.py <issues.json>

The file is what searchJiraIssuesUsingJql returned for the issues of a fix version (its `data`, or
just its `issues`), with each issue's `timetracking`. Only the delivered issues count: those in Done.
It prints a JSON object with `issues`, one entry per issue with `estimateSeconds`, `timeSeconds` and
`ratio` (the time over the estimate), and `total`, the same three added up. The total ratio is
calculated only over the issues that have both, and `total.ratioBasis` shows their two sums.
An issue with no recorded time has `timeSeconds` and `ratio` null: it is without time, not zero, and
`total.withoutTime` lists it and its estimate enters the total of estimate. One with no estimate, or a zero one, is listed in `total.withoutEstimate`
and its time enters the total of time.
"""
import json
import sys


def read_issues(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("data", data).get("issues", [])
    return data


def ratio(time, estimate):
    return None if time is None or not estimate else round(time / estimate, 2)


def totals(issues):
    rows = []
    for issue in issues:
        fields = issue["fields"]
        if fields["status"]["name"] != "Done":
            continue
        tracking = fields.get("timetracking") or {}
        estimate, time = tracking.get("originalEstimateSeconds"), tracking.get("timeSpentSeconds")
        rows.append({"key": issue["key"], "summary": fields["summary"], "estimateSeconds": estimate,
                     "timeSeconds": time, "ratio": ratio(time, estimate)})
    counted = [row for row in rows if row["ratio"] is not None]
    counted_estimate = sum(row["estimateSeconds"] for row in counted)
    counted_time = sum(row["timeSeconds"] for row in counted)
    estimate = sum(row["estimateSeconds"] or 0 for row in rows)
    time = sum(row["timeSeconds"] for row in rows if row["timeSeconds"] is not None)
    return {"issues": rows, "total": {"estimateSeconds": estimate, "timeSeconds": time,
                                      "ratio": ratio(counted_time, counted_estimate),
                                      "ratioBasis": {"estimateSeconds": counted_estimate, "timeSeconds": counted_time},
                                      "withoutEstimate": [row["key"] for row in rows if not row["estimateSeconds"]],
                                      "withoutTime": [row["key"] for row in rows if row["timeSeconds"] is None]}}


if __name__ == "__main__":
    print(json.dumps(totals(read_issues(sys.argv[1]))))
