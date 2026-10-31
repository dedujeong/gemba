---
type: llm
---
APP-103 "Aviso de la víspera" (send the notice the day before the service) matches the MVP sticky "Avisar un día antes del servicio". APP-104 "Confirmación de lectura" matches the MVP sticky "Confirmar que el cliente recibió el aviso".

PASS if the response proposes, for each of the two Stories not delivered, the sticky of the board it matches (by its text), and asks the person whether each one goes to the next release (Release 2) or to Later, and waits for the answer. It may recommend a destination, but it must leave the decision to the person.
FAIL if it moves or says it moved any sticky before the person answers, decides the destination without asking, matches a Story to the wrong sticky, or asks the person to move the stickies by hand in Confluence.
