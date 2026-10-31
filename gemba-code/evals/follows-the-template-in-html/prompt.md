---
name: follows-the-template-in-html
description: A declared issue's description follows the template of its work type and is sent as HTML.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Necesitamos una tarea técnica: dejar el deploy a producción automático cada vez que se integra a main, para que las historias de la versión se puedan probar en producción. Prioridad alta, component `platform`, sin bloqueos.

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
