---
type: llm
focus: trace
---
PASS if Claude answers with one single round of questions in one message, and the questions cover the four topics: budget, operation, team and data. Nothing is proposed or decided yet and nothing is written to Confluence.
FAIL if a topic is missing, if Claude proposes a stack or any decision before asking, if it splits the questions across several turns, or if it writes to Confluence.
