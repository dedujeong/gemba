---
name: returns-to-implement-when-a-criterion-is-unmet
description: An issue with an unmet criterion returns to Implement with the missing criterion named, and the real time worked in Review is logged when it leaves Review.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Revisa TALLER-33.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira, ni cambios reales de git, ni se ejecutan los tests. Sigue el flujo hasta terminar la revisión y entrega las acciones como una tabla con las columnas Acción, Herramienta y valores, una fila por acción.

TALLER-33 es una Story en Implement, de la fix version `Taller v0.1.0`, con estimado original de 3h. Todos sus tests están en verde. Sus criterios:

- Criterio 1: dado un cliente de la lista de hoy, cuando se ve la lista, entonces se ve su teléfono.
- Criterio 2: dado un cliente sin teléfono, cuando se ve la lista, entonces se ve que no tiene.

El diff de la rama implementa y prueba el criterio 1, pero no hace nada para el criterio 2: la lista muestra un espacio vacío para un cliente sin teléfono. El issue pasó a Review hoy a las 15:00 (hora de la Ciudad de México, -0600), cuando empezó esta revisión, y ahora son las 15:25.
