---
type: llm
---
The project has no CLAUDE.md. The person gives the Jira project (TALLER), the Confluence space (TALLER), the integration mode (merge, because they work alone) and the language (Spanish from Mexico).

The session cannot write files, so the CLAUDE.md is expected as content in the response; saying that nothing was written to disk is correct and is not a failure.

PASS if the response contains the full CLAUDE.md content, and it holds the Jira project key TALLER, the Confluence space key TALLER, the integration mode as merge and the language as es-MX (or an equivalent tag for Spanish from Mexico), each one stated once.
FAIL if any of the four values is missing or wrong, if the content lists the project's components, or if the response holds no CLAUDE.md content.
