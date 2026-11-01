---
type: llm
---
The maintainer asks to implement TALLER-22, a Story with one criterion. The plan is approved and the criterion is about to be built.

PASS if the response builds the criterion test first: it writes the test before the code that satisfies it, says that the test fails before the code exists and for which expected reason (the function does not return the phone), and only then writes the least code that makes it pass. It commits only once the test is green, with the test and the code in the same commit, and never commits the failing test on its own.
FAIL if it writes the code before the test, never has the test fail first, commits the test while it is red, or commits the test and the code in separate commits.
