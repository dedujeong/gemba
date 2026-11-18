---
name: writes-the-commit-with-the-layout-area-as-scope
description: The commit of a criterion is one line with the type, the Code layout area the change touches as scope, not the issue's component, and a description, and it does not carry the issue key.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Implementa TALLER-24.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Jira Site: taller.atlassian.net
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX

## Code layout

- `notifications`, domain, `src/notifications/`.
- `shared`, technical, `src/shared/`.
- Lo que cambia junto queda junto, y un dominio depende de otro solo por su archivo de entrada, en una sola dirección.
- Validador: `pnpm check-layout`.
```

En esta sesión no hay conexión a Jira, ni cambios reales de git, ni se ejecuta código. Sigue el flujo hasta que el único criterio ya está construido y su test pasa en verde, y entrega el commit como una tabla con las columnas Acción, Resultado esperado y Commit, una fila por acción, con el mensaje exacto del commit.

TALLER-24 es una Story en Backlog, sin bloqueos, de la fix version `Taller v0.1.0`, con el Summary `Send the reminder the day before`, y su component en Jira es `notifications`, pero el cambio de este criterio solo toca `src/shared/dates.ts` y su test, que son del área `shared`. Su único criterio: dado un servicio agendado para mañana, cuando llega el día anterior, entonces el cliente recibe el recordatorio. El plan aprobado es un solo commit para este criterio.
