---
name: skips-the-heuristics-for-a-bug
description: A Bug is declared without passing it through the edge-case heuristics, so no edge-case questions are asked.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Declara un Bug: el total de un servicio no suma el precio de las refacciones; solo suma la mano de obra. Pasos: el dueño registra un servicio con refacciones y abre su total. Esperado: el total incluye las refacciones. Actual: solo ve la mano de obra. Prioridad alta, component `web`, sin bloqueos. La Story que entregó el total ya está en Done.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

La fix version abierta es `Taller v0.1.0`. Los components del proyecto en Jira son `web`, `notifications` y `platform`.

En esta sesión no hay conexión a Jira ni a Confluence: escribe en tu respuesta la declaración completa tal como la crearías y di que no se creó nada.
