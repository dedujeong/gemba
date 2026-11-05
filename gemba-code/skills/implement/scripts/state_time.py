"""Print the time an issue spent in a state, from its Jira changelog.

Usage: python3 state_time.py <changelog.json> <State>

The file is what listJiraIssueChangelogs returned (its `data`, or just its `values`). The time
runs from each status change that moved the issue into the state to the one that moved it out;
an issue that entered the state twice adds up both spans.
It prints a JSON object with `seconds`, `timeSpent` in the form Jira takes for a worklog
(`1h 5m`) and `started`, when the issue entered the state.
"""
import json
import sys
from datetime import datetime


def read_entries(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("data", data).get("values", [])
    return data


def status_changes(entries):
    """Every status change as (created, from, to), oldest first."""
    changes = []
    for entry in entries:
        for item in entry.get("items", []):
            if item.get("field") == "status":
                changes.append((entry["created"], item.get("fromString"), item.get("toString")))
    return sorted(changes, key=lambda change: datetime.fromisoformat(change[0]))


def time_in_state(entries, state):
    first = entered = None
    seconds = 0
    for created, source, target in status_changes(entries):
        if target == state and entered is None:
            entered = created
            first = first or created
        elif source == state and entered is not None:
            seconds += int((datetime.fromisoformat(created) - datetime.fromisoformat(entered)).total_seconds())
            entered = None
    return {"seconds": seconds, "timeSpent": time_spent(seconds), "started": first}


def time_spent(seconds):
    minutes = max(1, round(seconds / 60))
    hours, minutes = divmod(minutes, 60)
    return " ".join(part for part in (f"{hours}h" if hours else "", f"{minutes}m" if minutes else "") if part)


if __name__ == "__main__":
    print(json.dumps(time_in_state(read_entries(sys.argv[1]), sys.argv[2])))
