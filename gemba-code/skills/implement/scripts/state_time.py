"""Print the time an issue spent in a state, from its Jira changelog.

Usage: python3 state_time.py <changelog.json> <State> [--now <ISO datetime>]

The file is what listJiraIssueChangelogs returned (its `data`, or just its `values`). The time
is the last span the issue spent in the state: from the status change that last moved it in to
the one that moved it out, or until --now (the current time when it is not given) when the issue
has not left the state yet. Earlier spans are not counted: the method logs each span when the
issue leaves the state, so they are logged already. A state the issue never entered prints an
error and exits 1.
It prints a JSON object with `seconds`, `timeSpent` in the form Jira takes for a worklog
(`1h 5m`) and `started`, when that last span began.
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
    """The last span in the state, the one not logged yet: still open, or the one that just closed."""
    started = left = None
    for created, source, target in status_changes(entries):
        if target == state:
            started, left = created, None
        elif source == state and started is not None:
            left = created
    if started is None:
        raise ValueError(f"the issue never entered {state}")
    end = datetime.fromisoformat(left) if left else now
    seconds = int((end - datetime.fromisoformat(started)).total_seconds())
    return {"seconds": seconds, "timeSpent": time_spent(seconds), "started": started}


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
