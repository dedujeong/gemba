---
name: asks-heuristic-questions-in-one-round
description: The edge-case questions of a Story come in one round, in the project language, each naming its criterion and heuristic, and the Story is not declared while one has no answer.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Declara una Story: el dueño de la tienda aplica un descuento a un pedido. Prioridad alta, component `web`, sin bloqueos.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TIENDA
- Confluence Space: TIENDA
- Integration: merge
- Language: es-MX
```

La fix version abierta es `Tienda v0.1.0`. Los components del proyecto en Jira son `web` y `platform`.

Esto es lo único que dice el Product Brief sobre descuentos:

> El dueño aplica un porcentaje de descuento a un pedido y el total se recalcula.

El mantenedor no ha respondido ninguna pregunta todavía. En esta sesión no hay conexión a Jira ni a Confluence: escribe en tu respuesta lo que harías con esta solicitud y di si algo quedó sin crear.
