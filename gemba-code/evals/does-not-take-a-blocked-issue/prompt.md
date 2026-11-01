---
name: does-not-take-a-blocked-issue
description: An issue blocked by an open issue does not move to Implement, and the blocking issue is named.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Toma TALLER-14.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira ni cambios reales de git: escribe en tu respuesta cada lectura, transición y comando que harías, y toma como resultado de las lecturas lo siguiente.

TALLER-14 es una Story en Backlog, de la fix version `Taller v0.1.0`, con el Summary `Remind the day before`. Está bloqueada por TALLER-11, una Story que está en Implement.
