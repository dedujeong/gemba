"""Print the estimate, the recorded time and the ratio between them, per issue and in total.

Usage: python3 time_totals.py <issues.json>

The file is what searchJiraIssuesUsingJql returned for the issues of a fix version (its `data`, or
just its `issues`), with each issue's `timetracking`. Only the delivered issues count: those in Done.
It prints a JSON object with `issues`, one entry per issue with `estimateSeconds`, `timeSeconds` and
`ratio` (the time over the estimate), and `total`, the same three added up.
An issue with no recorded time has `timeSeconds` and `ratio` null: it is without time, not zero, so it
stays out of the totals and `total.withoutTime` lists it. One with no estimate, or a zero one, is treated the same way.
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
    estimate = sum(row["estimateSeconds"] for row in counted)
    time = sum(row["timeSeconds"] for row in counted)
    return {"issues": rows, "total": {"estimateSeconds": estimate, "timeSeconds": time,
                                      "ratio": ratio(time, estimate),
                                      "withoutTime": [row["key"] for row in rows if row["ratio"] is None]}}


if __name__ == "__main__":
    print(json.dumps(totals(read_issues(sys.argv[1]))))
