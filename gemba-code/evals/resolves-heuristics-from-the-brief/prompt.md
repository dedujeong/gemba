---
name: resolves-heuristics-from-the-brief
description: A gap found by the edge-case heuristics becomes a criterion or an Out of scope line only when the brief decides it, a question otherwise, and the declared Story never mentions the heuristics.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Declara una Story: el dueño del taller marca un servicio como pagado. Prioridad alta, component `web`, sin bloqueos.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

La fix version abierta es `Taller v0.1.0`. Los components del proyecto en Jira son `web`, `notifications` y `platform`.

Esto es lo único que dice el Product Brief sobre pagos:

> Solo el dueño marca un servicio como pagado; los mecánicos solo lo ven.
> Fuera de alcance de esta versión: devolver un pago.

En esta sesión no hay conexión a Jira ni a Confluence: escribe en tu respuesta lo que harías con esta solicitud, tal como lo harías, y di que no se creó nada.
