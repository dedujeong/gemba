---
type: llm
---
The maintainer asks for a Task and gives no estimate. Every Story, Task and Bug is declared with an original estimate in hours of one person working with Claude.

PASS if the drafted Task carries an original estimate in hours (for example `3h`), shown in the declaration and sent in the create call (for example `timetracking: {"originalEstimate": "3h"}`).
FAIL if there is no original estimate, if it is given in days, weeks or story points instead of hours, or if no declaration is drafted.
