---
type: llm
---
The board in the prompt has five tasks in the backbone, left to right: "Guardar al cliente", "Anotar la fecha", "Ver a quién avisar", "Mandar el mensaje" and "Marcar el servicio como hecho". The MVP has 5 stories, which cover the first four tasks; "Marcar el servicio como hecho", under the activity "Cerrar el servicio", has no story in the MVP.

The person asked to close the MVP, and this check runs before the close, so naming the gaps and leaving the close to the person is the expected behavior, not a failure. Only the walk of the map is judged here: anything else the response adds, such as the entities, the states, the handoffs or what it recommends, is neither required nor penalized, and so is the form it walks the map in, whether a table, a list or prose.

PASS if the response goes through the tasks of the map and names "Marcar el servicio como hecho", the task of the activity "Cerrar el servicio", as a step the MVP leaves with no story.
FAIL if the response never goes through the tasks of the map, if it does not name that task as left without a story, or if it says one of the other four tasks has no story in the MVP.
