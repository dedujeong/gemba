---
name: declares-an-epic-with-its-stories
description: A release card with two or more stories that version-start hands over is declared as an Epic with the Story Map in Source and one Story per story as its children.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Esto viene de version-start: el maintainer ya revisó y confirmó la versión `Taller v0.1.0` completa, así que no hace falta volver a preguntarle. Declara esta tarjeta del release con start.

- Story Map: https://example.atlassian.net/wiki/spaces/TALLER/whiteboard/123
- Actividad del Story Map: Avisar. Al terminarla, el dueño avisa a cada cliente cuando le toca su siguiente servicio.
- Historia 1: Lista de clientes a avisar hoy. El dueño del taller ve cada mañana a qué clientes les toca su siguiente servicio. Component: `web`.
- Historia 2: Aviso por WhatsApp. El dueño abre el mensaje listo para enviarlo a un cliente de la lista. Component: `notifications`.
- Priority: High para el Epic y para ambas historias. Due date del Epic: 2026-11-20. Sin bloqueos.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

La fix version abierta es `Taller v0.1.0`. Los components del proyecto en Jira son `web`, `notifications` y `platform`.

En esta sesión no hay conexión a Jira ni a Confluence: escribe en tu respuesta las declaraciones completas en el orden en que las crearías (work type, summary, campos, parent y descripción en el formato en que se enviaría) y di que no se creó nada.
