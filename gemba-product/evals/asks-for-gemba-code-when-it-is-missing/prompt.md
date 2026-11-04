---
name: asks-for-gemba-code-when-it-is-missing
description: Without Gemba Code installed, version-start says it is required and creates and declares nothing.
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
max_turns: 10
---
Abre la versión de Taller. Ya vi las tarjetas del release y las confirmo tal como están. Esta versión es la 0.2.0, empieza el 2026-11-02 y se entrega el 2026-11-20. El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Confluence ni a Jira.
