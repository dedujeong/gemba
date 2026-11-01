---
type: llm
---
The board's MVP is delivered (gray). Release 2 has two cards with two stories each: "Record a service" (Save the vehicle, Suggest the date by service type) and "Remind" (See who to remind this week, Remind the day before). Both are declared as an Epic. There is no connection to Jira or Confluence, so saying that nothing was created is expected.

The maintainer gave no dates and no hours of work per day.

PASS if the response asks, in one message, for the start date, the delivery date and the hours of work per day before showing the table of the release with the Epics' due dates, and says that the hours per day are not saved in the CLAUDE.md (or does not write them there).
FAIL if it shows the release table with due dates without asking for them first, if it invents the dates or the hours per day, if it asks for them one at a time over several messages, or if it writes the hours per day into the CLAUDE.md.
