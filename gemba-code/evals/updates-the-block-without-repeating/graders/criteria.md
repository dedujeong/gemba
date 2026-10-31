---
type: llm
---
The CLAUDE.md already has a Gemba section with Jira project MESA, Confluence space MESA, integration merge and language es-MX, between a title section and a Commands section. The person runs setup again to change the integration to pull request.

Judge only the CLAUDE.md content itself; the explanation around it may mention the old value.

The session cannot write files, so the CLAUDE.md is expected as content in the response; saying that nothing was written to disk is correct and is not a failure.

PASS if the full CLAUDE.md in the response has exactly one Gemba section, the Jira project, the Confluence space and the language appear once each with their same values, the integration appears once and says pull request (merge no longer appears as the integration), and the title, the description and the Commands section are still there.
FAIL if any of the project values appears more than once, if there are two Gemba sections, if the integration still says merge, if existing content is lost, or if the response holds no CLAUDE.md content.
