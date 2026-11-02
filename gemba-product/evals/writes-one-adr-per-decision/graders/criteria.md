---
type: llm
focus: trace
---
Three decisions were reviewed and the person asks to record them. No Confluence connection exists, so Claude drafts the pages in the reply.
PASS if Claude drafts exactly one separate ADR for each of the three decisions, each titled `ADR-000N <Decision>` (ADR-0001, ADR-0002, ADR-0003), places them in the `Decisions` folder of the space, and each draft has the sections Context, Decision, Alternatives, Consequences and Source, with the rejected alternative of that decision recorded in Alternatives.
FAIL if two decisions share one page, if an ADR has no number in its title, if the folder is not Decisions, if a section is missing, or if a rejected alternative is left out of its ADR.
