---
name: declares-a-release-card-like-any-issue
description: A release card that version-start hands over is declared the same way as an issue the maintainer asks for.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Esto viene de version-start: el maintainer ya revisó y confirmó la versión `Taller v0.1.0` completa, así que no hace falta volver a preguntarle. Declara esta tarjeta del release con start.

- Actividad del Story Map: Avisar.
- Historia: Lista de clientes a avisar hoy.
- Lo que acordamos: el dueño del taller ve cada mañana a qué clientes les toca su siguiente servicio.
- Priority: Highest. Component: `web`. Sin bloqueos.

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
