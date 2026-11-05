"""Print the time an issue spent in a state, from its Jira changelog.

Usage: python3 state_time.py <changelog.json> <State> [--now <ISO datetime>]

The file is what listJiraIssueChangelogs returned (its `data`, or just its `values`). The time
runs from each status change that moved the issue into the state to the one that moved it out;
an issue that entered the state twice adds up both spans. A span still open, because the issue
has not left the state, runs until --now (the current time when it is not given). A state the
issue never entered prints an error and exits 1.
It prints a JSON object with `seconds`, `timeSpent` in the form Jira takes for a worklog
(`1h 5m`) and `started`, when the issue entered the state.
"""
import json
import sys
from datetime import datetime, timezone


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


def time_in_state(entries, state, now):
    first = entered = None
    seconds = 0
    for created, source, target in status_changes(entries):
        if target == state and entered is None:
            entered = created
            first = first or created
        elif source == state and entered is not None:
            seconds += int((datetime.fromisoformat(created) - datetime.fromisoformat(entered)).total_seconds())
            entered = None
    if entered is not None:
        seconds += int((now - datetime.fromisoformat(entered)).total_seconds())
    if first is None:
        raise ValueError(f"the issue never entered {state}")
    return {"seconds": seconds, "timeSpent": time_spent(seconds), "started": first}


def time_spent(seconds):
    minutes = max(1, round(seconds / 60))
    hours, minutes = divmod(minutes, 60)
    return " ".join(part for part in (f"{hours}h" if hours else "", f"{minutes}m" if minutes else "") if part)


if __name__ == "__main__":
    arguments = sys.argv[1:]
    now = datetime.now(timezone.utc)
    if "--now" in arguments:
        position = arguments.index("--now")
        now = datetime.fromisoformat(arguments[position + 1])
        del arguments[position:position + 2]
    try:
        print(json.dumps(time_in_state(read_entries(arguments[0]), arguments[1], now)))
    except ValueError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
