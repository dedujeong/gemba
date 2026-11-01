---
name: reviews-an-epic-by-its-children
description: Reviewing an Epic verifies that all its child issues are finished; if one is not, the Epic does not move to Review and the open child is named.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Revisa TALLER-34.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira, ni cambios reales de git. Sigue el flujo y entrega las acciones como una tabla con las columnas Acción, Herramienta y valores, una fila por acción, y toma como resultado de las lecturas lo siguiente.

TALLER-34 es un Epic en Implement, de la fix version `Taller v0.1.0`. Sus hijos:

| Key | Type | Summary | Status |
| --- | --- | --- | --- |
| TALLER-35 | Story | Save the vehicle | Done |
| TALLER-36 | Task | Create the customers table | Cancelled |
| TALLER-37 | Story | List today's customers | Implement |
