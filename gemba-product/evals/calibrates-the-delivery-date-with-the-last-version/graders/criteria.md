---
type: llm
focus: trace
---
The product Taller has one released version, Taller v0.1.0, whose three issues are Done with worklogs: 12 hours estimated (4 + 2 + 6) and 18 hours of real time (6 + 3 + 9), a ratio of 1.5. The maintainer gave the start date (2026-11-02), the delivery date (2026-11-20) and 6 hours of work per day. There is no connection to Jira or Confluence, so saying that nothing was created is expected.

PASS if the response shows the two totals of the last released version (12 hours estimated and 18 hours of real time) and the ratio 1.5, and applies that ratio to the total estimate of the new version to propose a calibrated delivery date, showing the estimated total of the new version, the calibrated hours and the date.
FAIL if it does not show the two totals and the ratio, if it does not apply the ratio to the total of the new version, or if it proposes a delivery date without saying it was calibrated with the real time of the last version.
