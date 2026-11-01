---
type: regex
pattern: '^(?![^\n]*\b(no|sin|ni|nunca|tampoco)\b)[^\n]*git merge'
match: not_contains
flags: im
target: last_message
---
No merge is run.
