---
type: llm
---
The current release is Release 2. Its story "Save the vehicle" is already the card of the issue TALLER-9, which exists, is in Backlog and has no fix version. The other stories of Release 2 are still rectangles.

PASS if the response treats TALLER-9 as already declared: it does not propose creating a new issue (a Story, or a child of an Epic) for "Save the vehicle", and it says that TALLER-9 takes the fix version of the version through `gemba-code:start` (or that its fix version will be set), while the stories that are still rectangles are the ones to declare.
FAIL if the response lists "Save the vehicle" as a story or card to declare as a new issue, ignores TALLER-9, or leaves TALLER-9 out of the version without saying why.
