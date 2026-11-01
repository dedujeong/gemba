---
type: regex
pattern: '^(?![^\n]*\b(no|sin|ni|nunca|tampoco|hasta)\b)[^\n]*transitionJiraIssue[^\n]*Review'
match: not_contains
flags: im
target: last_message
---
The Epic is not moved to Review while a child is not finished.
