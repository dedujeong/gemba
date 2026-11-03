---
type: llm
---
In the prompt the person ran the pre-mortem of the MVP and wrote three reasons, and for each one they already decided where it goes. The first reason, that the owner tires of typing each customer, goes to the map as the story "Importar los clientes de la libreta" in Release 2, in the column of the task "Guardar al cliente". The second reason, that WhatsApp changes its rules, goes to the Product Brief as a risk, in the table Riskiest assumptions, and the person did not say how high the risk is. The third reason, that customers may not accept a notice from an unknown number, goes to the map as an open question, a red sticky, in the column of the task "Mandar el mensaje".

There is no Confluence connection, so nothing can be published. A reason counts as placed when the response says where it goes, whether it writes the patch, the command of a script or a plain sentence. The response may also close the MVP or refuse to close it, recount it, or add the open question to the Open decisions of the brief: none of that is required or penalized, and neither is the form of the answer.

Only the destination of the three reasons and the risk level of the second one are judged.

PASS if the response places the first reason as a story of Release 2 under "Guardar al cliente" and the third as a red sticky under "Mandar el mensaje", and for the second reason it asks the person how high the risk is (High, Medium or Lower) or leaves the level pending, without choosing a level itself.
FAIL if the response places any of the three reasons somewhere else than the person decided, leaves one out, or chooses a risk level for the second reason that the person never gave.
