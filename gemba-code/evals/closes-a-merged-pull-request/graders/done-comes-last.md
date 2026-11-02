---
type: regex
pattern: 'git pull origin develop[\s\S]*addOrEditJiraIssueWorklog[\s\S]*transitionJiraIssue'
target: last_message
---
The develop update comes first, then the worklog, and the move to Done is last.
