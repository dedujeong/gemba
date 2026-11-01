---
name: continues-when-all-issues-are-closed
description: A version whose issues are all Done or Cancelled, apart from its release Task, is not stopped and the close continues.
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
max_turns: 10
---
Cierra la versión Taller v0.2.0. El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira: escribe en tu respuesta la búsqueda que harías y toma como su resultado esta lista de los issues de la fix version `Taller v0.2.0`:

| Key | Type | Summary | Status |
| --- | --- | --- | --- |
| TALLER-21 | Epic | Record a service | Done |
| TALLER-22 | Story | Save the vehicle | Done |
| TALLER-23 | Story | Suggest the date by service type | Done |
| TALLER-24 | Story | Remind the day before | Cancelled |
| TALLER-25 | Task | Release Taller v0.2.0 | Review |
