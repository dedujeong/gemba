---
type: llm
---
In the board, the MVP row is gray (delivered, 2 stories), Release 2 is green (the current release, 2 stories), Release 3 is orange (1 story) and Later is light orange (1 story).

PASS if the response reads the MVP as already delivered and leaves its 2 stories out of the scope, and says that the scope now in front is Release 2 with 2 stories (it may also mention Release 3 with 1 story as the one after).
FAIL if it counts the gray MVP stories in the scope (for example 4), calls the MVP the current scope, or reports a count for Release 2 other than 2.
