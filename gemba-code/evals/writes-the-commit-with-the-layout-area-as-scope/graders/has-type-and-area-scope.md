---
type: regex
pattern: '(feat|fix|perf|refactor|docs|test|build|chore|ci|style|revert)\(shared\): [a-z]'
target: last_message
---
The commit message has a type, the Code layout area the change touches as scope and a description.
