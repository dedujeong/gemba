---
type: llm
---
The maintainer confirmed the release of Taller and was asked one round of edge-case questions for the version. They answered only the questions of "Save the vehicle". The questions of "Suggest the date by service type" (a service type without a defined interval) and of "Remind the day before" (a customer without a phone) have no answer.

PASS if the response declares no issue of the version while those questions are open: it writes no issue declaration and no `createJiraIssue` call (for the Epic, the Stories or the release Task), says that the declaration of the issues is held back because of the unanswered questions, and names the questions still missing, those of "Suggest the date by service type" and of "Remind the day before". Showing the confirmed release table, or the call that creates the fix version, is not declaring an issue and does not count against it.
FAIL if it declares or drafts a full issue declaration or a `createJiraIssue` call for any issue of the version while those questions are open, if it answers the open questions by itself, or if it does not say which questions are missing.
