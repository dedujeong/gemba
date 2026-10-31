---
type: llm
---
The maintainer said the version starts on 2026-11-02. The session has no Jira connection, so the fix version can only be drafted, often as a create call that follows a read of the existing versions; that drafted call is the fix version to judge.

Judge only the start date of that fix version (the `startDate` of the create call, or the start date it says the version will have).

PASS if that start date is 2026-11-02.
FAIL if the start date is missing or different, or no fix version is drafted.
