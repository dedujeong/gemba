---
type: llm
focus: trace
---
The MVP has four stories for a single bike workshop (register an order, change its state, the customer checks the state with a link, the owner sees the open orders), and the Constraints say free plans only, one person operating it with error alerts only, Python and Postgres, and name and phone of each customer.
PASS if Claude proposes architecture decisions and every one of them shows three things: the proposed option, two or three alternatives, each with the reason it loses here, and the reason the proposed option was chosen.
FAIL if any decision is stated as a single option with no alternatives, if an alternative is only a name with no reason it loses, if a decision gives no reason for choosing its option, or if Claude proposes no decisions.
