---
name: does-not-review-an-issue-outside-implement
description: An issue that is not in Implement is not moved to Review, and its current state is named.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Revisa TALLER-31.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira, ni cambios reales de git, ni se ejecutan los tests. Sigue el flujo y entrega las acciones como una tabla con las columnas Acción, Herramienta y valores, una fila por acción.

TALLER-31 es una Story en Backlog, sin bloqueos, de la fix version `Taller v0.1.0`, con el Summary `List today's customers`.
