---
type: llm
---
The branch only touches a skill file, the eval files of that skill and a README, so nothing in it is code. The session cannot run reviews, so the response is expected as a report and a table of actions.

PASS if the response does not launch /code-review or /security-review (nor lists them as actions to run) and says that the change is verified with evals or another mechanism instead of a code review.
FAIL if it launches or lists /code-review or /security-review as something to run, or if it does not say why no code review is run.
