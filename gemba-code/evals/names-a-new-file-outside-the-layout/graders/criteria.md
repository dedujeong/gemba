---
type: llm
---
The issue meets its only criterion and its tests are green, but the branch adds a test file at tests/order-total.test.ts. The Code layout of the CLAUDE.md says that tests go next to the file they test, with the same name and the ending .test.ts, so that test belongs at src/orders/order-total.test.ts. The other new file, src/orders/order-total.ts, follows the layout. The session has no Jira, so actions are expected as a table.

PASS if the response names tests/order-total.test.ts as a file outside the layout, says that it should go at src/orders (next to order-total.ts), does not flag src/orders/order-total.ts, and sends the issue back to Implement instead of leaving it in Review.
FAIL if the misplaced test is not named, if the place it should go is missing or wrong, if the file that follows the layout is flagged, or if the issue is left in Review.
