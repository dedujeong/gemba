---
type: llm
---
The board in the prompt has a story in the MVP for each of its five tasks and no red sticky, so nothing keeps the MVP from closing except the pre-mortem. The person said "Cierro el MVP", which is an explicit closing. There is no Confluence connection in this case, so nothing can be published either way.

Before closing, the skill runs a pre-mortem as Gary Klein proposes it: it asks the person to imagine that the product already failed and to write the reasons why. Anything else the response adds, such as the recount, the checks of the release or the form it answers in, is neither required nor penalized.

Only what the response does with the close and with the pre-mortem is judged.

PASS if the response asks the person to imagine that the MVP failed (the product launched and did not work) and to write down the reasons, and it does not close the MVP in this turn: it records no closing item and sets no page status.
FAIL if the response closes the MVP or records the closing, if it never asks the person to imagine the failure and write the reasons, or if it writes the reasons of the failure itself instead of asking the person for them.
