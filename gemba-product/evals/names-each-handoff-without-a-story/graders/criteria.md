---
type: llm
---
In the workflow of the prompt the work changes hands four times: the dueño enters the customer and the date into the app (dueño to app), the reminder leaves for the customer over WhatsApp (app or dueño to cliente), the cliente answers that message (cliente back to dueño), and the mecánico attends the service and the dueño learns it is done (mecánico to dueño). The MVP's 5 stories cover entering the data and sending the message; no story receives or records the customer's answer, and none records what the mecánico did.

The person asked to close the MVP, and this check runs before the close, so naming the gaps and leaving the close to the person is the expected behavior, not a failure. Only the handoff check is judged here: anything else the response adds, such as the walk of the map, the entities or the states, is neither required nor penalized.

PASS if the response goes through the handoffs of the workflow one by one, naming for each one who hands the work to whom, and says which of them no story of the MVP covers, among them the customer's answer coming back to the dueño and the mecánico's work reaching the dueño.
FAIL if the response never goes through the handoffs one by one, if it names a gap without naming the handoffs it belongs to, if it leaves the customer's answer unnamed, or if it claims a story of the MVP already receives or records that answer.
