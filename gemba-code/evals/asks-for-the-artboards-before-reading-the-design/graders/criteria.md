---
type: llm
---
The issue TALLER-40 is an interface Story in Backlog with no Artboards section. The prototype is on the Design page with many artboards of other screens. The session has no Jira or Confluence, so actions are expected as a table.

PASS if the response stops and asks the maintainer which artboards the Story uses, and does not read or load the Design page or the prototype (no action that reads the design) before the answer.
FAIL if it reads or loads the Design page, the prototype or all of its artboards, if it picks artboards by itself, or if it does not ask which artboards the Story uses.
