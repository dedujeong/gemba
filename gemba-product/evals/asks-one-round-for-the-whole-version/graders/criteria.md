---
type: llm
---
The maintainer confirmed the release of Taller (an Epic "Record a service" with the Stories "Save the vehicle" and "Suggest the date by service type", and the Story "Remind the day before"). The edge cases of "Remind the day before" are fully decided; those of the other two Stories are not, and nothing has been answered.

PASS if the response, before creating or drafting as ready any issue of the version, asks the edge-case questions of the whole version in one single round written in Spanish, grouped by Story, where each question says its criterion and its heuristic; the Story "Remind the day before" does not appear in the round; and it says that nothing was created and that the version waits for the answers.
FAIL if it creates or presents issues of the version as ready to create while questions are open, if it asks the questions Story by Story across several rounds, if a question lacks its criterion or heuristic, or if "Remind the day before" appears in the round.
