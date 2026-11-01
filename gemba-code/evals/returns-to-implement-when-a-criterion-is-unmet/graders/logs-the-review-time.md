---
type: regex
pattern: 'addOrEditJiraIssueWorklog[^\n]*25\s?(m|min)'
flags: i
target: last_message
---
The 25 minutes really worked in Review are logged on the issue, not the 3h estimate.
