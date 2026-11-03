---
type: llm
focus: trace
---
The person accepted the code layout decision and asks to record it. The highest ADR in the folder is ADR-0002. No Confluence connection exists, so Claude drafts the page in the reply.
PASS if Claude drafts one ADR titled `ADR-0003 <Decision>` for the code layout, places it in the `Decisions` folder, and the draft has the sections Context, Decision, Alternatives, Consequences and Source; the Decision states the four parts (folders by domain, where tests go, how files are named, where migrations go) and Alternatives records both rejected options (by layers, a separate tests folder) with why each lost.
FAIL if the title has no number or the wrong one, if the folder is not Decisions, if a section is missing, if the Decision leaves out one of the four parts, or if a rejected alternative is left out.
