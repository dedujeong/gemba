---
type: llm
---
The issue meets its only criterion and its tests are green. Two of the three new files follow the Code layout (src/orders/order-total.ts and its test next to it). The third, scripts/seed-orders.sh, is a kind of file that the layout does not mention anywhere. The session has no Jira, so actions are expected as a table.

PASS if the response names scripts/seed-orders.sh as a file the layout does not cover and asks whether the layout should cover it, and it does not send the issue back to Implement because of that file (the issue stays in Review, ready for the maintainer).
FAIL if that file is not named, if the question about covering it is missing, if it says where the file should go as if the layout required it, or if the issue is returned to Implement over it.
