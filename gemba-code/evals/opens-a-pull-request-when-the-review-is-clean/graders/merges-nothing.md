---
type: regex
pattern: '^(?![^\n]*\b(no|sin|ni|nunca|tampoco|hasta|todavía|aún|después|luego)\b)[^\n]*(git merge|transitionJiraIssue[^\n]*Done)'
match: not_contains
flags: im
target: last_message
---
Nothing is merged and the issue is not moved to Done.
