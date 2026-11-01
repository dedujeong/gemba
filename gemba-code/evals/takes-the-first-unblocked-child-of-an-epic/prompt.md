---
name: takes-the-first-unblocked-child-of-an-epic
description: Taking an Epic in Backlog moves it to Implement and takes its first child that is in Backlog and not blocked.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Toma TALLER-30.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira ni cambios reales de git: escribe en tu respuesta cada lectura, transición y comando que harías, y toma como resultado de las lecturas lo siguiente.

TALLER-30 es un Epic en Backlog, de la fix version `Taller v0.1.0`, sin issues que lo bloqueen. Sus hijos, en orden de rank:

| Key | Type | Summary | Status | Blocked by |
| --- | --- | --- | --- | --- |
| TALLER-31 | Story | Save the vehicle | Backlog | TALLER-32 (Backlog) |
| TALLER-32 | Task | Create the customers table | Backlog | none |
| TALLER-33 | Story | List today's customers | Backlog | TALLER-31 (Backlog) |
