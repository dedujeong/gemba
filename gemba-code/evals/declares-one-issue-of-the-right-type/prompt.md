---
name: declares-one-issue-of-the-right-type
description: Work the maintainer describes becomes a single issue of the work type it is.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Encontré algo: cuando el dueño marca un aviso como enviado, la lista de clientes a avisar hoy lo sigue mostrando. Eso lo entregó TALLER-8, que ya está en Done. Decláralo, prioridad alta, component `web`, sin bloqueos.

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
