---
name: moves-an-issue-in-implement-to-review
description: An issue in Implement with every test green moves to Review when it is reviewed by its key.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Revisa TALLER-30.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira, ni cambios reales de git, ni se ejecutan los tests. Sigue el flujo hasta mover el issue y entrega las acciones como una tabla con las columnas Acción, Herramienta y valores, una fila por acción.

TALLER-30 es una Story en Implement, sin bloqueos, de la fix version `Taller v0.1.0`, con el Summary `Show the phone of each customer in today's list`. Su construcción terminó y todos sus tests están en verde.
