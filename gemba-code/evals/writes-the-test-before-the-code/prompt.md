---
name: writes-the-test-before-the-code
description: Each criterion gets a test that fails before the code that satisfies it is written, and only green is committed, test and code together.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Implementa TALLER-22.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira, ni cambios reales de git, ni se ejecuta código. Sigue el flujo hasta que el plan ya esté aprobado y entrega la construcción del criterio como una tabla con las columnas Acción, Resultado esperado y Commit, una fila por acción.

TALLER-22 es una Story en Backlog, sin bloqueos, de la fix version `Taller v0.1.0`, con el Summary `Show the phone of each customer in today's list`. Su criterio: dado un cliente de la lista de hoy, cuando se ve la lista, entonces se ve su teléfono. La exploración ya terminó: la función que entrega los clientes a la pantalla hoy no devuelve el teléfono, y esa función tiene tests. El plan que se aprobó es un solo commit para este criterio.
