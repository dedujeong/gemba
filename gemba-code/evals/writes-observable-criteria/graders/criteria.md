---
type: llm
---
The maintainer asks for a Story and gives meeting notes with an invented example (a customer name, a quantity, an amount) and a mechanism (a server query, a table, a modal). The Product Brief states none of them.

PASS if the drafted Story has an "Acceptance criteria" section whose criteria use the form "Dado ..., cuando ..., entonces ...", and no criterion contains the example data from the notes (the customer's name, the quantity or the amount) or a mechanism (server, query, table, modal), only what the person observes, with generic referents.
FAIL if a criterion is not in the given, when, then form, or if any criterion (or the rest of the description) carries the invented name, quantity or amount, or says how it is achieved.
