---
name: reports-each-criterion-and-each-commit
description: The review says for each criterion whether it is met, compares the real commits one by one against the planned list, and integrates nothing.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Revisa TALLER-32.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira, ni cambios reales de git, ni se ejecutan los tests. Sigue el flujo hasta terminar la revisión y entrega el resultado como una tabla con las columnas Elemento y Veredicto.

TALLER-32 es una Story en Implement, de la fix version `Taller v0.1.0`, con el Summary `Show the phone of each customer in today's list`. Todos sus tests están en verde. Sus criterios:

- Criterio 1: dado un cliente de la lista de hoy, cuando se ve la lista, entonces se ve su teléfono.
- Criterio 2: dado un cliente sin teléfono, cuando se ve la lista, entonces se ve que no tiene.

La lista de commits planeados que se aprobó es:

1. `refactor(web): rename the customer list helper`
2. `feat(web): show the phone of each customer in today's list`
3. `feat(web): show when a customer has no phone`

El `git log` de la rama tiene exactamente esos tres commits, en ese orden. El diff renombra el helper en el primero; en el segundo agrega el test y el código que muestran el teléfono del cliente; en el tercero agrega el test y el código que muestran "Sin teléfono" cuando el cliente no lo tiene.
