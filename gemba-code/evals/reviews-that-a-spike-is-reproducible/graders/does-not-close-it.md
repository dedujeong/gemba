---
type: regex
pattern: '^(?![^\n]*\b(no|sin|ni|nunca|tampoco)\b)[^\n]*(git merge|git worktree remove|transitionJiraIssue[^\n]*Done)'
match: not_contains
flags: im
target: last_message
---
The review does not merge, remove the worktree or move the Spike to Done.
