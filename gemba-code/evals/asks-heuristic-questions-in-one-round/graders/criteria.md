---
type: llm
---
The maintainer asks for a Story to apply a discount to an order. The Product Brief decides almost nothing about the edge cases, and the maintainer has answered none of them.

PASS if the response asks the edge-case questions in one single round (one message with all of them, not one at a time), written in Spanish, where each question says which acceptance criterion it comes from and which heuristic found it (for example nothing, many, limit, duplicate, no permission, undo, other state), and the response does not present a Story as declared: it says that nothing was created and that the Story waits for the answers, naming the questions still missing.
FAIL if the response asks one question and waits for it before the others, if a question does not say its criterion and its heuristic, if the questions are not in Spanish, or if it declares or presents the Story as ready to create with the questions still unanswered.
