---
type: llm
---
There is no connection to Jira, so saying that nothing was changed and writing the calls that would be made is expected: a call counts as done when it is drafted in the response.

PASS if the response drafts the call that releases the existing fix version `Taller v0.2.0` in Jira (an update of that version with `released: true`, such as `manageJiraProjectVersion` with `action: "update"`) with a release date.
FAIL if it does not draft that call, or if it drafts the creation of another version.
