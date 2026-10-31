---
type: llm
---
The Jira data in the prompt has 4 Stories: APP-101 and APP-102 are Done; APP-103 (Implement) and APP-104 (Backlog) are not. Estimates are 4h, 6h, 3h and 5h (18h in total); time spent is 5h, 4h 30m, 2h and 0h (11h 30m in total). The delivered Stories (Done) have 10h estimated and 9h 30m spent.

PASS if the response says that APP-101 and APP-102 were delivered and APP-103 and APP-104 were not, and gives the time spent against the original estimate with correct figures: either per Story and in total (11h 30m against 18h) or for the delivered ones (9h 30m against 10h), clearly labeled which. The response must not invent Stories or figures.
FAIL if it counts a not-delivered Story as delivered, gets the totals wrong, ignores the time against the estimate, or asks the person to look the data up themselves.
