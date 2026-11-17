---
type: regex
pattern: '(?=[\s\S]*"transitionName"\s*:\s*"to Review")(?![\s\S]*listJiraIssueTransitions)'
target: last_message
---
The issue is moved to Review by the name of its transition, without listing the transitions first.
