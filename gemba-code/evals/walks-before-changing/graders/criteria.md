---
type: llm
---
The maintainer asks to implement TALLER-20, a Story in Backlog with no blockers. Once it is taken and in Implement, the work starts.

PASS if, after taking the issue and before any step that creates or changes code, a test or any file of the project, the response explores without modifying any of them. Creating the branch and moving the issue to Implement are part of taking the issue and do not count as changes. The exploration covers: it reads the issue, the code the Story touches (the today's list screen), the existing tests of that code and the recent git history, and runs the existing tests.
FAIL if it writes or changes any file, test or code before that exploration (the branch and the transition do not count), or if the exploration leaves out the existing tests or the recent git history.
