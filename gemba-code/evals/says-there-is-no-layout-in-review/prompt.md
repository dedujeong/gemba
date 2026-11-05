---
name: says-there-is-no-layout-in-review
description: In a project whose CLAUDE.md has no Code layout section, review says there is no layout, invents none and does not block the issue.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Revisa TALLER-41.

El CLAUDE.md del proyecto tiene este contenido:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira, ni cambios reales de git, ni se ejecutan los tests. Sigue el flujo hasta terminar la revisión y entrega las acciones como una tabla con las columnas Acción, Herramienta y valores, una fila por acción.

TALLER-41 es una Story en Implement, con un solo criterio: dado un cliente, cuando se ve su detalle, entonces se ve su teléfono. Todos sus tests están en verde y el criterio se cumple. El resultado de `git diff --name-status --diff-filter=AR develop...story/TALLER-41-customer-phone` es:

```
A	src/customer-phone.ts
A	tests/customer-phone.test.ts
```

El issue pasó a Review hoy a las 09:00 (hora de la Ciudad de México, -0600) y ahora son las 09:20.
