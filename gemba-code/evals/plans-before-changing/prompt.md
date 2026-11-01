---
name: plans-before-changing
description: After exploring, the plan is presented in plan mode with its commits, and nothing changes until the maintainer approves it.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Implementa TALLER-21.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX

```

En esta sesión no hay conexión a Jira, ni cambios reales de git, ni modo de planeación real. Sigue el flujo hasta el punto en que ya vas a cambiar código y escribe ahí el resultado: cómo presentarías el plan y lo que harías con el código mientras el maintainer no lo apruebe.

TALLER-21 es una Story en Backlog, sin bloqueos, de la fix version `Taller v0.1.0`, con el Summary `Show the phone of each customer in today's list`. Sus criterios: dado un cliente de la lista de hoy, cuando se ve la lista, entonces se ve su teléfono; dado un cliente sin teléfono, cuando se ve la lista, entonces se ve que no tiene. Toca la pantalla de la lista de hoy. La exploración del código ya terminó: la pantalla recibe a los clientes de una función que hoy no devuelve el teléfono, y no hay tests de esa pantalla.
