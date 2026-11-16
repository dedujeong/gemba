---
type: llm
focus: trace
---
The person accepted the code layout decision and asks to record it. The highest ADR in the folder is ADR-0002. No Confluence connection exists, so Claude drafts the page in the reply.

The ADR records the layout as one flat list of components, each with its type (`domain` or `technical`) and its path, and names the validator that checks the two rules. The list is flat: components are not nested under one another.

PASS if Claude drafts one ADR titled `ADR-0003 <Decision>` for the code layout, in the `Decisions` folder, with the sections Context, Decision, Alternatives, Consequences and Source, and the ADR records a single flat list of components where every component has a type (`domain` or `technical`) and a path, and records the validator (`scripts/check-layout.ts`) that checks the two rules.
FAIL if the title has no number or the wrong one, if a section is missing, if the components are not a flat list or one lacks its type or its path, or if the validator is not recorded.
