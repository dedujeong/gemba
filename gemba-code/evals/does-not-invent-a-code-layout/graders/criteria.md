---
type: llm
---
The project has no CLAUDE.md and its space has no ADR of the code layout, only ADRs about the stack and the database. The session cannot write files, so the CLAUDE.md is expected as content in the response.

PASS if the CLAUDE.md in the response has no Code layout section and proposes no folders, test location, file naming or migrations path, and the response says that the architecture step has not decided the code layout yet.
FAIL if the CLAUDE.md has a Code layout section or any invented layout for the stack, or if the response does not say that the layout was not decided yet.
