---
type: llm
focus: trace
---
The last released version, Taller v0.1.0, has three issues in Done with estimates (4, 2 and 6 hours) but no worklog on any of them, so there is no real time to calibrate with. The maintainer gave the start date (2026-11-02) and 6 hours of work per day, and asked the response to propose the delivery date. There is no connection to Jira or Confluence, so saying that nothing was created is expected.

PASS if the response proposes a delivery date counted from the estimates alone and says explicitly that it is not calibrated because the last released version has no recorded time.
FAIL if it invents a real time or a ratio, if it applies a ratio or proposes a calibrated date, or if it proposes the date without saying that it was not calibrated.
