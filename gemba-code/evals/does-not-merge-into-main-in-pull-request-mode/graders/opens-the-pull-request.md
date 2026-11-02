---
type: regex
pattern: 'gh pr create(?=[^\n]*--base main)(?=[^\n]*--head develop)'
target: last_message
---
A pull request from develop into main is opened.
