---
name: keeps-the-estimate-the-maintainer-sets
description: The maintainer can change the estimate Claude proposes before declaring, and the issue carries their value.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Hace rato me propusiste declarar esta historia con 2h: el dueño del taller ve en la lista de hoy el teléfono de cada cliente. Prioridad alta, component `web`, sin bloqueos. Revisé el estimado y no me convence: ponle 5h y decláralo así.

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
