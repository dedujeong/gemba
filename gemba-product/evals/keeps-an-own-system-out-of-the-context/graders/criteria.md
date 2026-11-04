---
type: llm
focus: trace
---
The person asks for the spec JSON of the architecture diagrams of a product whose Web app, database and Auth are operated by the team and whose Bank is operated by a financial institution. No Confluence connection exists, so Claude writes the spec in the reply. Only the spec Claude writes is judged.
PASS if, in the spec, the Context diagram lists the Bank as an external system and does not list the Web app, the database or Auth as externals, and those three appear in Containers.
FAIL if the database, Auth or the Web app is an external system of the Context, or if the Bank is missing from the Context externals.
