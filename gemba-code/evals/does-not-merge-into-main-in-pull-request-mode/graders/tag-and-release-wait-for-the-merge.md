---
type: regex
pattern: '(claude plugin tag|gh release create)[\s\S]*gh pr create'
match: not_contains
target: last_message
---
No tag or release comes before the pull request is opened.
