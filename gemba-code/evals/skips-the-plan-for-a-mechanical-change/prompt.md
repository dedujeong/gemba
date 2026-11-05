---
name: skips-the-plan-for-a-mechanical-change
description: When the maintainer says the change is mechanical, implement explores and goes straight to the red test, without entering plan mode or presenting a plan.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Implementa TALLER-23. Es un cambio mecánico, no necesito plan.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX

```

En esta sesión no hay conexión a Jira, ni cambios reales de git, ni modo de planeación real. Sigue el flujo hasta el punto en que ya vas a cambiar código y escribe ahí el resultado: qué harías primero con el código.

TALLER-23 es una Task en Backlog, sin bloqueos, de la fix version `Taller v0.1.0`, con el Summary `Rename getCustomers to listCustomers`, del component `customers`. Su Done when: la función `listCustomers` existe y `getCustomers` ya no existe. La exploración del código ya terminó: `getCustomers` está definida en un archivo y la usan dos pantallas; hay un test que la llama por su nombre actual.
