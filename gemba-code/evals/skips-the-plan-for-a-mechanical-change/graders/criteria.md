---
type: llm
---
The maintainer asks to implement TALLER-23, a Task in Backlog, and says the change is mechanical and needs no plan. The Task renames a function. The exploration of the code is already done.

Only the part of the response about how the work with the code starts is judged. Taking the issue (branch, transition to Implement), running the existing tests before changing anything, and what happens after the work (time log, review) are not judged. Describing the steps it will follow is expected, since the session cannot change code for real, and is not a plan.

PASS if the response does not enter plan mode, does not present a plan for the maintainer to approve and does not wait for an approval, and the first change it makes to the code or the tests is the test that fails now (a test that calls the new name and fails because it does not exist yet), before it renames the function.
FAIL if it presents a plan of commits for approval, says it is entering plan mode or waits for the maintainer to approve something before changing code, or if it renames the function before writing the failing test.
