---
type: llm
---
The brief in the prompt gives a servicio four states: pendiente, avisado, hecho and cancelado, and the events that move it: el dueño lo anota, sale el aviso, el cliente llega, el cliente avisa que no va a ir, and el taller cierra ese día. The MVP's 5 stories cover anotar el servicio (pendiente) and mandar el aviso (avisado); no story covers a servicio that is cancelled, whether the reminder already went out or not, and none covers a servicio that becomes hecho.

The person asked to close the MVP, and this check runs before the close, so naming the gaps and leaving the close to the person is the expected behavior, not a failure. Only the state and event check is judged here: anything else the response adds, such as the walk of the map or the entities, is neither required nor penalized.

PASS if the response crosses the states of a servicio with the events that can reach it, in a matrix or state by state, and names among the uncovered combinations that a servicio already avisado which the client cancels has no story in the MVP.
FAIL if the response never crosses states with events, if it leaves the cancellation of an avisado servicio unnamed, or if it claims a story of the MVP already covers cancelling a servicio.
