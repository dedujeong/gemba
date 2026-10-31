---
type: llm
---
The new Story depends on TALLER-10.

In the link call, `linkType: "Blocks"` reads inwardIssue blocks outwardIssue: `inwardIssue: "TALLER-10"` with the new issue as `outwardIssue` is the right direction. The session cannot create anything, so the new issue's key is a placeholder and the link is expected as a drafted call.

PASS if the declaration includes a blocking link where TALLER-10 blocks the new issue (the new issue is blocked by TALLER-10), as a link to create, not only as a mention in the description.
FAIL if there is no blocking link, if the direction is reversed (the new issue blocks TALLER-10), or if no declaration is drafted.
