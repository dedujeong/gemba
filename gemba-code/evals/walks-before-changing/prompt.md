---
name: walks-before-changing
description: Once an issue is in Implement, the issue, the code it touches, its existing tests and the recent history are explored without changing anything before any code is changed.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Implementa TALLER-20.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira ni cambios reales de git. Toma como resultado de las lecturas lo siguiente y responde solo con dos cosas: la lista de lo que leerías o correrías antes de cambiar cualquier archivo del proyecto, y si cambiarías algo en esa etapa.

TALLER-20 es una Story en Backlog, sin bloqueos, de la fix version `Taller v0.1.0`, con el Summary `Show the phone of each customer in today's list`. Su criterio: dado un cliente de la lista de hoy, cuando se ve la lista, entonces se ve su teléfono. Toca la pantalla de la lista de hoy.
