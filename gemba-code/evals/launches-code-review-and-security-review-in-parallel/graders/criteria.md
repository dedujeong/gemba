---
type: llm
---
The branch changes authentication, permissions and a database migration, 312 lines added and 48 removed: a large change of high risk. The session cannot run reviews, so the response says which ones it would launch, as a report and a table of actions.

PASS if the response launches /code-review and /security-review together in the same step (in parallel), chooses a level for /code-review among low, medium, high or xhigh and picks a high one (high or xhigh) because of the size and the risk, never max or ultra, and says what it launched and why.
FAIL if one of the two reviews is missing, if they are launched one after the other instead of together, if the level is missing or is max or ultra, if the level is low or medium for this change, or if the reason is not given.
