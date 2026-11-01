---
type: regex
pattern: '^(?![^\n]*\b(no|sin|ni|nunca|tampoco)\b)[^\n]*git (merge|push|branch -[dD])'
match: not_contains
flags: im
target: last_message
---
Nothing is merged, pushed or deleted because an Epic has no branch.
