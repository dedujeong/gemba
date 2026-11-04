---
type: llm
---
There is no connection to Jira, so writing the search that would be made and taking the given table as its result is expected.

The delivered issues are the ones in Done: TALLER-22, TALLER-23 and TALLER-25 (the Epic TALLER-21 is Done but has no estimate or time). TALLER-24 is Cancelled, so it was not delivered.

PASS if the handoff to learn lists each delivered issue with its original estimate and its logged time (TALLER-22: 2h and 1h 30m; TALLER-23: 3h and 50m; TALLER-25: 1h and 10m). The Epic may appear with none. TALLER-24 is not counted as delivered. Totals are optional; saying they are not added because no tool to add them is available is acceptable.
FAIL if an issue is missing or has the wrong estimate or time, if a total that is given is wrong (the right ones are 6h estimated and 2h 30m logged), if TALLER-24 counts as delivered or its estimate enters the totals, or if the handoff only describes the numbers without giving them.
