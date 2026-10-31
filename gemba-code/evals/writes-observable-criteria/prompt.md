---
name: writes-observable-criteria
description: A Story's acceptance criteria use the given, when, then form and describe what the person observes, without invented sample data or mechanisms.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Declara una Story: el dueño del taller ve el total de cada servicio que registró. Prioridad alta, component `web`, sin bloqueos. Notas de la reunión: «el total del servicio de Juan por 3 refacciones sumó $1,250; se calcula en el servidor con una consulta a la tabla de servicios y se muestra en un modal».

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
