---
type: llm
focus: trace
---
The MVP has four stories for a single bike workshop (register an order, change its state, the customer checks the state with a link, the owner sees the open orders), and the Constraints say free plans only, one person operating it with error alerts only, Python and Postgres, and name and phone of each customer.
PASS if Claude proposes architecture decisions and every one of them passes four checks: the chosen option is named, in the title of the decision or in a line of its own; there are two or three alternatives; each alternative says why it loses here; and the decision says why the chosen option wins. A reason is a story, a constraint, a cited source, or an Assumption mark about a limit that could not be verified.
FAIL if any decision has no alternatives or only one, if an alternative is only a name with no reason it loses, if a decision gives no reason for choosing its option, or if Claude proposes no decisions.
