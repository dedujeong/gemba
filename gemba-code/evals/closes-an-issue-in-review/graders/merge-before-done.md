---
type: regex
pattern: 'git merge[\s\S]*transitionJiraIssue[^\n]*Done'
target: last_message
---
The merge comes before the move to Done.
