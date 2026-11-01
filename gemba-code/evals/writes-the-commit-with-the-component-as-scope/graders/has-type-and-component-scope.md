---
type: regex
pattern: '(feat|fix|perf|refactor|docs|test|build|chore|ci|style|revert)\(notifications\): [a-z]'
target: last_message
---
The commit message has a type, the issue's component as scope and a description.
