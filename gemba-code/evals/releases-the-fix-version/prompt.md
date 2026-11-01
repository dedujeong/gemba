---
name: releases-the-fix-version
description: Once the release is published on GitHub, the skill releases the fix version in Jira, moves the release Task to Done, and reports from a Jira read made after the change.
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
max_turns: 10
---
Termina el cierre de Taller v0.2.0. El release `Taller v0.2.0` ya está publicado en GitHub sobre el tag `taller--v0.2.0`, y todos los issues de la versión están en Done o Cancelled salvo la Task de release TALLER-25, que está en Review con su tiempo de Review ya registrado en el worklog. La fix version `Taller v0.2.0` (id 10020) está sin liberar. El release se publicó hoy, 2026-11-20. El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira: escribe en tu respuesta las llamadas que harías, en orden, y di que no se cambió nada. Al final reporta cómo quedó el cierre.
