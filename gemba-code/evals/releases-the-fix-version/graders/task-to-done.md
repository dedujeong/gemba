---
type: llm
---
There is no connection to Jira, so saying that nothing was changed and writing the calls that would be made is expected: a call counts as done when it is drafted in the response.

PASS if the response drafts moving TALLER-25, the release Task, to Done (a transition to Done), listed after the call that releases the fix version.
FAIL if it does not draft that transition, if the transition comes before the release of the fix version, or if it drafts transitions of other issues.
