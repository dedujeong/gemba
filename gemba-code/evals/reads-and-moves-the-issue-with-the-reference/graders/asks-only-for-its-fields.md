---
type: regex
pattern: '(?=[\s\S]*getJiraIssue)(?=[\s\S]*"responseFields")(?![\s\S]*"view"\s*:\s*"evidence")'
target: last_message
---
The issue is read with its fields and responseFields, never with the evidence view.
