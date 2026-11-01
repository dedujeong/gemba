---
type: llm
---
The maintainer takes TALLER-30, an Epic in Backlog with no blockers, whose first child by rank (TALLER-31) is blocked by an open issue.

PASS if the response moves TALLER-30 to Implement and then takes TALLER-32 as the child: it creates the branch `task/TALLER-32-create-the-customers-table` from `develop` and moves TALLER-32 to Implement. It does not create a branch for TALLER-30 (an Epic has no branch), and it does not take TALLER-31 or TALLER-33 because they are blocked by open issues.
FAIL if it takes TALLER-31 or TALLER-33, creates a branch for the Epic, takes more than one child, leaves the Epic in Backlog, or stops without taking a child.
