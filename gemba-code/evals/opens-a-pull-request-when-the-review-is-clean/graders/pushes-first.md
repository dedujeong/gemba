---
type: regex
pattern: 'git push[^\n]*(TALLER-41|<rama>|<branch>)[\s\S]*gh pr create'
target: last_message
---
The branch is pushed before the pull request is opened.
