---
type: llm
---
The board's MVP is delivered (gray). Release 2 has two cards with two stories each: "Record a service" (Save the vehicle, Suggest the date by service type) and "Remind" (See who to remind this week, Remind the day before). Both are declared as an Epic. There is no connection to Jira or Confluence, so saying that nothing was created is expected.

The maintainer gave the start date (2026-11-02), the delivery date (2026-11-20) and 6 hours of work per day, so the response shows the release for confirmation.

PASS if the release shown has both Epics, each with a due date of its own and the two dates are different from each other.
FAIL if an Epic has no due date, if the two Epics share a due date, or if the response asks the maintainer to set the due dates instead of proposing them.
