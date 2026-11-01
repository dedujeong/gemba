---
name: logs-the-real-time-not-the-estimate
description: When the implementation ends, the time worked in Implement is logged on the issue from when it entered Implement, never copied from the estimate.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Implementa TALLER-23.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira ni cambios reales de git. Sigue el flujo completo: el plan se aprobó y la construcción terminó con todos los tests en verde. Entrega el cierre de la etapa Implement como una tabla con las columnas Acción, Herramienta y valores, una fila por acción.

TALLER-23 es una Story en Backlog, sin bloqueos, con estimado original de 4h. Pasó a Implement hoy a las 10:00 (hora de la Ciudad de México, -0600) y ahora son las 10:40.
