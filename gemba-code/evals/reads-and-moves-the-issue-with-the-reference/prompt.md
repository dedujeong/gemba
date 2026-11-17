---
name: reads-and-moves-the-issue-with-the-reference
description: Reviewing an issue reads it and moves it with the calls written in the Jira calls reference, asking only for the fields it uses.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Revisa TALLER-30.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Jira Site: taller.atlassian.net
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira, ni cambios reales de git, ni se ejecutan los tests. Sigue el flujo hasta mover el issue y entrega cada llamada a Jira como un bloque JSON con los argumentos exactos que mandarías, uno por llamada, en orden.

TALLER-30 es una Story en Implement, sin bloqueos, de la fix version `Taller v0.1.0`, con el Summary `Show the phone of each customer in today's list`. Su construcción terminó y todos sus tests están en verde.
