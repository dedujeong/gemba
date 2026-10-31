---
type: llm
---
version-start hands over one release card after the maintainer already confirmed the whole version. A standalone declaration has: the work type, a summary in English, priority, component, fix version, and a description that follows the template of its work type (for a Story: an opening "Como <actor>, quiero <acción>, para <resultado>." and an "Acceptance criteria" section), sent as HTML.

PASS if the response drafts one Story with all of those: an English summary, priority Highest, component `web`, fix version `Taller v0.1.0`, and an HTML description that follows the Story template; and it does not ask the maintainer to confirm the declaration again before creating it.
FAIL if any of those fields or template parts is missing, if the work type is not Story, if the description is not HTML, if it stops to ask the maintainer for confirmation, or if no declaration is drafted.
