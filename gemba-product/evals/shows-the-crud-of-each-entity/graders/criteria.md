---
type: llm
---
The MVP on the board has 5 stories: "Guardar nombre y teléfono del cliente", "Anotar la fecha del próximo servicio", "Lista de clientes a avisar hoy", "Abrir WhatsApp con el mensaje listo" and "No avisar dos veces por el mismo servicio". Its entities are cliente, servicio and aviso. The MVP creates and reads a cliente, but no story changes a cliente, although the brief says phone numbers change, and no story deletes one or takes it off the list, although the brief says customers stop coming.

The person asked to close the MVP, and this check runs before the close, so naming the gaps and leaving the close to the person is the expected behavior, not a failure. Only the entity check is judged here: anything else the response adds, such as the walk of the map or what it recommends, is neither required nor penalized.

PASS if the response goes entity by entity, saying for cliente and for servicio whether the MVP creates, reads, changes and deletes each one, and names as missing that no story changes a cliente, so an old phone cannot be corrected, and that no story deletes a cliente or takes it off the list.
FAIL if the response never goes entity by entity, if it leaves either of those two missing operations unnamed, or if it says the MVP can change or delete a cliente.
