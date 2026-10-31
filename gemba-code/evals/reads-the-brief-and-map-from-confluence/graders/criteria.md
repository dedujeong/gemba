---
type: llm
focus: trace
---
The person asks to open the version. The Product Brief and the Story Map live in the Confluence space TALLER, and this session has no Confluence connection.

PASS if Claude says that it reads the Product Brief and the Story Map from the Confluence space TALLER (or tries to), and the trace shows no file written inside the project with the brief or the Story Map, and Claude does not ask the person to copy them into the repository as files.
FAIL if Claude writes a copy of the brief or the Story Map into the project (for example a Markdown or SVG file in the repository), asks the person to add such a copy to the repository, or reads them from anywhere other than Confluence.
