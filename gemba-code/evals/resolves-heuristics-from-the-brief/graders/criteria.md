---
type: llm
---
The maintainer asks for a Story to mark a service as paid. The Product Brief decides two edge cases: only the owner marks a service as paid (a permission rule), and refunding a payment is out of scope. It says nothing about marking a service that is already paid.

PASS if the response: (1) has at least one criterion in the given, when, then form that expresses the owner-only rule from the brief (it may be written as the owner can mark it or as a mechanic cannot); (2) puts the refund in an Out of scope line in the brief's words, not as a criterion; (3) raises the case of a service that is already paid as a question to the maintainer, among any other questions it asks, and has no criterion that decides it; and (4) keeps the drafted Story's own text free of any mention of heuristics, a decision table or a question round (the questions to the maintainer sit outside the Story and may be labeled as questions).
FAIL if the already-paid case is not raised or is answered by an invented criterion, if the refund appears as a criterion, if the owner-only rule is missing from the criteria, or if the drafted Story mentions heuristics, a decision table or a question round.
