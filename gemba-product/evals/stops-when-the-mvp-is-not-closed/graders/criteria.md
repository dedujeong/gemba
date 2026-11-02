---
type: llm
focus: trace
---
The Product Brief says the MVP is still open and the person asks to start the architecture step. No Confluence connection exists.
Asking means putting a question to the person about their budget, operation, team or data. Proposing means naming a stack, a hosting or any technical decision as the option to take.
These are not asking and not proposing: saying the MVP is open, naming the four topics as pending, saying what the brief does not cover, pointing to the Story Map to close the MVP, and announcing that one round of questions will come once the MVP is closed.
PASS if Claude says the MVP is not closed and stops: it asks no question about budget, operation, team or data and proposes no stack, hosting or decision.
FAIL if Claude asks any of those architecture questions or proposes any decision while the MVP is still open.
