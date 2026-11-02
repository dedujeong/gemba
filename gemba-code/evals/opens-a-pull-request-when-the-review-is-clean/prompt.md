---
name: opens-a-pull-request-when-the-review-is-clean
description: In a project in pull request mode, a review that finds every criterion met pushes the branch and opens a pull request into develop titled with the key and the Summary, with the criteria in its body, and merges nothing.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Revisa TALLER-41.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: pull request
- Language: es-MX
```

En esta sesión no hay conexión a Jira, ni cambios reales de git o de GitHub, ni se ejecutan los tests. Sigue el flujo hasta terminar. Entrega las acciones como una tabla con las columnas Acción y Comando o herramienta, una fila por acción, en el orden en que se hacen; después de la tabla, muestra el cuerpo del pull request tal como quedaría.

TALLER-41 es una Story en Implement, con la rama `story/TALLER-41-show-the-phone-of-each-customer-in-todays-list` y el Summary `Show the phone of each customer in today's list`. Todos sus tests están en verde. Sus criterios:

- Criterio 1: dado un cliente de la lista de hoy, cuando se ve la lista, entonces se ve su teléfono.
- Criterio 2: dado un cliente sin teléfono, cuando se ve la lista, entonces se ve que no tiene.

La lista de commits planeados que se aprobó es:

1. `feat(web): show the phone of each customer in today's list`
2. `feat(web): show when a customer has no phone`

El `git log` de la rama tiene exactamente esos dos commits, en ese orden. El primero agrega el test y el código que muestran el teléfono del cliente; el segundo agrega el test y el código que muestran "Sin teléfono" cuando el cliente no lo tiene. Los dos criterios se cumplen.
