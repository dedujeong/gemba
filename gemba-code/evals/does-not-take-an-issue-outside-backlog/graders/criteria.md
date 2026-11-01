---
type: llm
---
The maintainer takes TALLER-15, a Story that is in Review and that no issue blocks.

PASS if the response does not take TALLER-15 and says that it is in Review. It creates no branch for TALLER-15 and does not move it to Implement.
FAIL if it creates a branch for TALLER-15, moves it to Implement, or refuses without saying that it is in Review.
