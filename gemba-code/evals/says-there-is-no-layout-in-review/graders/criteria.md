---
type: llm
---
The project has no Code layout section in its CLAUDE.md. The issue meets its only criterion and its tests are green. The session has no Jira, so actions are expected as a table.

PASS if the response says that the CLAUDE.md has no Code layout section, so the new files were not checked against a layout, and it does not propose or assume any layout (no folder structure, no place where the files should go), and it does not send the issue back to Implement because of the files.
FAIL if the response does not mention that there is no layout, if it invents or suggests a layout or a place for the files, or if it returns the issue to Implement over the files.
