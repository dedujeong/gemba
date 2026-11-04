---
type: llm
---
The Product Brief gives a rule that depends on two conditions, the type of payment (advance or settlement) and the amount against the balance (lower, equal, higher). That makes six combinations and three distinct results: an advance lower than the balance reduces the balance; a settlement equal to the balance leaves the service paid; every other combination is rejected.

PASS if the drafted Story covers all three results in its acceptance criteria and does not write one criterion per combination (six criteria for the rule), and the Story's own description (the HTML that would be sent to Jira) has no decision table and does not mention a table or combinations. Writing the rejections as one criterion or as a few criteria that group combinations is fine. What the response says around the description, outside it, is not judged for this. The criteria use generic referents (no invented amounts).
FAIL if a result is missing, if the rule has one criterion per combination (five or more criteria for it), if the Story's description includes a table or mentions a decision table or combinations, or if a criterion has invented amounts.
