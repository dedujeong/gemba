---
type: regex
pattern: 'timeSpent\W{0,6}4\s?h'
match: not_contains
flags: i
target: last_message
---
The worklog does not log the 4h estimate as the time spent.
