"""Print the estimate, the recorded time and the ratio between them, per issue and in total.

Usage: python3 time_totals.py <issues.json>

The file is what searchJiraIssuesUsingJql returned for the issues of a fix version (its `data`, or
just its `issues`), with each issue's `timetracking`. Only the delivered issues count: those in Done.
It prints a JSON object with `issues`, one entry per issue with `estimateSeconds`, `timeSeconds` and
`ratio` (the time over the estimate), and `total`, the same three added up.
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
    return round(time / estimate, 2)


def totals(issues):
    rows = []
    for issue in issues:
        fields = issue["fields"]
        if fields["status"]["name"] != "Done":
            continue
        tracking = fields.get("timetracking", {})
        estimate, time = tracking["originalEstimateSeconds"], tracking["timeSpentSeconds"]
        rows.append({"key": issue["key"], "summary": fields["summary"], "estimateSeconds": estimate,
                     "timeSeconds": time, "ratio": ratio(time, estimate)})
    estimate = sum(row["estimateSeconds"] for row in rows)
    time = sum(row["timeSeconds"] for row in rows)
    return {"issues": rows, "total": {"estimateSeconds": estimate, "timeSeconds": time,
                                      "ratio": ratio(time, estimate)}}


if __name__ == "__main__":
    print(json.dumps(totals(read_issues(sys.argv[1]))))
