---
type: llm
focus: trace
---
The last released version, Taller v0.1.0, has four issues in the search result: two stories in Done (4 and 2 hours estimated, 6 and 3 hours of real time), one Cancelled story (5 hours estimated, 2 of real time) and the release Task `Release Taller v0.1.0` in Done (1 hour estimated, 4 of real time). The correct base for the ratio is only the two stories in Done: 6 hours estimated, 9 hours of real time, a ratio of 1.5. With the release Task the ratio would be 13 over 7, about 1.86, and with the Cancelled story it would be different again. The sandbox has no shell, so the response may add by hand: do not judge the tool used. There is no connection to Jira or Confluence, so saying that nothing was created is expected.

PASS if the totals and the ratio it shows come only from the two Done stories (6 hours estimated, 9 hours of real time, ratio 1.5), leaving out the release Task and the Cancelled story.
FAIL if the release Task or the Cancelled story enters the totals or the ratio, or if the response shows no ratio at all.
