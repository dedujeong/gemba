---
type: regex
pattern: '^(?![^\n]*\b(no|sin|ni|nunca|tampoco|hasta|todavía|aún|después|luego)\b)[^\n]*git merge '
match: not_contains
flags: im
target: last_message
---
Nothing is merged here.
