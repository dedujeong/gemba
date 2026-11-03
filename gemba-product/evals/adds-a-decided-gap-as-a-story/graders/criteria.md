---
type: llm
---
The board in the prompt has five tasks in the backbone, left to right: "Guardar al cliente", "Anotar la fecha", "Ver a quién avisar", "Mandar el mensaje" and "Marcar el servicio como hecho". Two of them have no story in the MVP: "Ver a quién avisar", under the activity "Avisar", and "Marcar el servicio como hecho", under "Cerrar el servicio". The person already decided both in the prompt: the first one enters the MVP as a list of the customers to call today, and the second one stays out of the MVP because they keep it in their notebook.

There is no Confluence connection in this case, so nothing can be published: a story drafted in the reply counts as added, whether it comes as a patch, as the command of a script with its task and its release, or as a sentence that names the story, its task and its release. The person asked to close the MVP, and deciding the gaps runs before the close, so not closing the MVP in this turn is expected and not a failure. The response may also go on with the rest of the review and ask the person about other gaps it finds, such as entities, states, handoffs or anything else: that is neither required nor penalized, and neither is the form it answers in.

Only what the response does with those two decided gaps is judged.

PASS if the response puts the gap the person decided into the MVP as a story of the task "Ver a quién avisar", and leaves "Marcar el servicio como hecho" out of the MVP naming the reason the person gave, that they keep it in their notebook.
FAIL if the response leaves the decided gap out of the MVP, if it puts it in another release or under another task, if it turns the discarded gap into a story anyway, if it drops the discarded gap without naming the reason the person gave, or if it asks the person again where either of those two gaps goes.
