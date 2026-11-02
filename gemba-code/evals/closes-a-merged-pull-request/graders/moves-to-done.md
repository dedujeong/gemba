---
type: regex
pattern: 'transitionJiraIssue[^\n]*Done|Done[^\n]*transitionJiraIssue'
flags: i
target: last_message
---
The issue is moved to Done.
