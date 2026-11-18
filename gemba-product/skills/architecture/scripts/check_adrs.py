"""Report where the ADRs of a space, its Architecture page and its Spikes disagree.

Usage: python3 check_adrs.py <space.json>

The file holds what the skill read from Confluence and Jira:
{
  "adrs": [{"id": "ADR-0001", "state": "Accepted", "spike": "KEY-12", "superseded_by": null}],
  "architecture": {"ADR-0001": "Accepted"},
  "spikes": {"KEY-12": "Done"}
}
`state` is one of the ADR states of SKILL.md. `spike` is the key of the Spike the ADR names, and
`architecture` the state the Architecture page shows for each ADR.
It prints one line per discordance and exits 1 when there is any.
"""
import json
import sys


def read_space(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def discordances(space):
    """One line per disagreement, in the order of the ADRs."""
    found = []
    for adr in space["adrs"]:
        spike = adr.get("spike")
        if adr["state"] == "Accepted" and spike:
            status = space["spikes"].get(spike)
            if status is None:
                found.append(f'{adr["id"]}: Accepted but its Spike {spike} is not in the space, so it cannot be confirmed Done')
            elif status != "Done":
                found.append(f'{adr["id"]}: Accepted but its Spike {spike} is {status}, not Done')
        shown = space["architecture"].get(adr["id"])
        if shown is not None and shown != adr["state"]:
            found.append(f'{adr["id"]}: its state is {adr["state"]} but the Architecture page shows {shown}')
    return found


if __name__ == "__main__":
    lines = discordances(read_space(sys.argv[1]))
    print("\n".join(lines), end="\n" if lines else "")
    sys.exit(1 if lines else 0)
