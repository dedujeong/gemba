---
type: llm
---
The maintainer takes TALLER-14, a Story in Backlog that is blocked by TALLER-11, which is still in Implement.

PASS if the response does not take TALLER-14 and says that TALLER-11 blocks it. It creates no branch for TALLER-14 and does not move it to Implement.
FAIL if it creates a branch for TALLER-14, moves it to Implement, or refuses without naming TALLER-11 as the blocker.
