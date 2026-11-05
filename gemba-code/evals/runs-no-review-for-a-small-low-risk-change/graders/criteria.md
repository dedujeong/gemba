---
type: llm
---
The branch changes two code files (one with its test), 14 lines added and 3 removed, in a way that touches none of the sensitive areas. The session cannot run reviews, so the response is expected as a report and a table of actions.

PASS if the response decides not to launch /code-review or /security-review for this change and says why, by naming that the change is small and of low risk.
FAIL if it launches or lists /code-review or /security-review as something to run, or if it decides not to run them without saying why.
