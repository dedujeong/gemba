---
type: regex
pattern: '^(?![^\n]*\b(no|sin|ni|nunca|tampoco)\b)[^\n]*transitionJiraIssue[^\n]*Done'
match: not_contains
flags: im
target: last_message
---
The issue is not moved to Done.
