---
type: llm
focus: trace
---
The person gives only the Jira project (PERIPLO). There is no Jira or Confluence connection, so the Confluence space, the integration mode and the language cannot be read.

PASS if Claude asks the person for the Confluence space, the integration mode (merge or pull request) and the language before writing any CLAUDE.md content.
FAIL if Claude fills in any of those three on its own (for example, assumes the space is PERIPLO, assumes merge, or assumes a language) in a CLAUDE.md it writes or drafts, or if it does not ask for one of them.
