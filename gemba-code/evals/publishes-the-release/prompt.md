---
name: publishes-the-release
description: Asked to publish a version whose release Task is merged into develop, the skill merges develop into main, pushes it, tags it with the plugin name and version, and creates the GitHub release with the repository's notes template.
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
max_turns: 10
---
Publica la versión Taller v0.2.0. Todos sus issues ya están en Done o Cancelled, y la Task de release TALLER-25 ya está integrada en `develop` con su commit `chore(manifest): bump taller to v0.2.0`. El repositorio es https://github.com/taller-dev/taller y tiene varios plugins de Claude; el de este producto es `taller`. El repositorio tiene `.github/release-notes.md` con la plantilla de las notas (una frase de apertura, secciones Added, Changed, Fixed y Removed, y una línea **Full Changelog**). El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira ni acceso al repositorio remoto: escribe en tu respuesta los comandos que ejecutarías, en orden, y di que no se ejecutó nada. La versión anterior del plugin es `taller--v0.1.0`. En esta versión se agregó "Registrar un servicio con su fecha" y se corrigió que "el recordatorio salía un día tarde".
