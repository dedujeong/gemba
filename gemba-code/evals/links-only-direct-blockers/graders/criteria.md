---
type: llm
---
TALLER-10 blocks TALLER-11, and the new Story needs both. The new Story is therefore blocked by TALLER-11 directly, and by TALLER-10 only through TALLER-11.

There is no connection to Jira, so the new issue's key is a placeholder and the links are drafted calls. Saying that nothing was created, and asking the maintainer to confirm the declaration, is expected: a link counts as declared when its call is drafted in the response.

In the link call, `linkType: "Blocks"` reads inwardIssue blocks outwardIssue: `inwardIssue: "TALLER-11"` with the new issue as `outwardIssue` is the right direction. Only the link calls count. Mentioning TALLER-10 in the explanation of why it gets no link is fine.

PASS if the response drafts one blocking link where TALLER-11 blocks the new Story, and drafts no link from TALLER-10 to the new Story. Saying that TALLER-10 is already covered through TALLER-11 is fine.
FAIL if it drafts a link from TALLER-10 to the new Story, if it drafts no link from TALLER-11, or if the direction is reversed.
