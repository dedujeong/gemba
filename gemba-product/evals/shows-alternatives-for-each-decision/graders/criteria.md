---
type: llm
focus: trace
---
The MVP has four stories for a single bike workshop (register an order, change its state, the customer checks the state with a link, the owner sees the open orders), and the Constraints say free plans only, one person operating it with error alerts only, Python and Postgres, and name and phone of each customer. The person asked for one decision only: the language and framework the application is built with. Judge that decision alone; ignore anything else the answer adds.
PASS if that decision passes four checks: the chosen option is named, in the title of the decision or in a line of its own; there are two or three alternatives; each alternative says why it loses here; and the decision says why the chosen option wins. Every one of those reasons, for each alternative and for the chosen option, names the story or the constraint of the brief it rests on (Costo, Operación, Equipo, Datos, or one of the four stories) or carries an Assumption mark for what could not be verified.
FAIL if the decision has no alternatives or only one, if an alternative is only a name with no reason it loses, if any of those reasons names no story and no constraint and carries no Assumption mark, if the decision gives no reason for choosing its option, or if Claude proposes no such decision.
