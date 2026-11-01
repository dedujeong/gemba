---
type: regex
pattern: '^(?![^\n]*\b(no|sin|ni|nunca|tampoco)\b)[^\n]*transitionJiraIssue[^\n]*Review'
match: not_contains
flags: im
target: last_message
---
The issue is not moved to Review. A line that says the transition is not made does not count as making it.
