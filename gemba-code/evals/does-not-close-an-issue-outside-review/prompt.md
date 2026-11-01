---
name: does-not-close-an-issue-outside-review
description: An issue that is not in Review is not merged and does not move to Done, and its state is named.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Cierra TALLER-41.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira ni cambios reales de git. Sigue el flujo y entrega las acciones como una tabla con las columnas Acción, Herramienta y valores, una fila por acción.

TALLER-41 es una Story en Implement, con la rama `story/TALLER-41-list-todays-customers`. Sus tests están en verde, pero no se ha revisado.
