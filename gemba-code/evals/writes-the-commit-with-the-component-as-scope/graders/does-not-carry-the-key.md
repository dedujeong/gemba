---
type: regex
pattern: '\(notifications\):[^\n|]*TALLER-24'
match: not_contains
target: last_message
---
The commit message does not repeat the issue key; only the branch carries it.
