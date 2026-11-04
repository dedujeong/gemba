---
type: llm
---
The board's MVP is delivered (gray). Release 2 has two cards with two stories each: "Record a service" (Save the vehicle, Suggest the date by service type) and "Remind" (See who to remind this week, Remind the day before). Both are declared as an Epic. There is no connection to Jira or Confluence, so saying that nothing was created is expected.

The maintainer set the version to start on 2026-11-02 and be delivered on 2026-11-03, with 2 hours of work per day, and estimated every story at 4 hours. Each Epic adds up to 8 hours and no Epic can have more than 4 hours available, so neither fits. The maintainer decides what to do about it.

PASS if, before asking the maintainer to confirm, the response says that the Epics do not fit in the dates (naming at least one Epic with its hours against the hours available), and leaves the scope and the estimates as they are, without removing stories or lowering estimates on its own.
FAIL if the response does not warn that an Epic does not fit, if the warning comes only after the maintainer confirms, or if it cuts stories, lowers estimates or changes the dates by itself.
