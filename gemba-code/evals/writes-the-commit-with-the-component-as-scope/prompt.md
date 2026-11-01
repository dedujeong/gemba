---
name: writes-the-commit-with-the-component-as-scope
description: The commit of a criterion is one line with the type, the issue's component as scope and a description, and it does not carry the issue key.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Implementa TALLER-24.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira, ni cambios reales de git, ni se ejecuta código. Sigue el flujo hasta que el único criterio ya está construido y su test pasa en verde, y entrega el commit como una tabla con las columnas Acción, Resultado esperado y Commit, una fila por acción, con el mensaje exacto del commit.

TALLER-24 es una Story en Backlog, sin bloqueos, de la fix version `Taller v0.1.0`, con el Summary `Send the reminder the day before`, y su component en Jira es `notifications`. Su único criterio: dado un servicio agendado para mañana, cuando llega el día anterior, entonces el cliente recibe el recordatorio. El plan aprobado es un solo commit para este criterio.
