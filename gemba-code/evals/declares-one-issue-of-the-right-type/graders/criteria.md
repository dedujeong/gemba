---
type: llm
---
The maintainer reports that something already delivered by an issue in Done does not behave as it should.

PASS if the response drafts exactly one issue and its work type is Bug.
FAIL if it drafts more than one issue, if the work type is anything other than Bug (for example a Story or a Task), or if no declaration is drafted.
