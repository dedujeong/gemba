---
name: estimates-in-hours
description: A Story, Task or Bug is declared with an original estimate in hours.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Declara una tarea técnica: respaldar la base de datos de producción cada noche, para no perder los avisos registrados si algo falla. Prioridad media, component `platform`, sin bloqueos.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

La fix version abierta es `Taller v0.1.0`. Los components del proyecto en Jira son `web`, `notifications` y `platform`.

En esta sesión no hay conexión a Jira ni a Confluence: escribe en tu respuesta la declaración completa tal como la crearías (work type, summary, campos y descripción en el formato en que se enviaría) y di que no se creó nada.
