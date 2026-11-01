---
type: regex
pattern: '(?=[\s\S]*Criterio 1[^\n]*\b(cumple|cumplido)\b)(?=[\s\S]*Criterio 2[^\n]*\b(cumple|cumplido)\b)'
flags: i
target: last_message
---
The review gives a verdict for each of the two criteria.
