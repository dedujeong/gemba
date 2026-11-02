---
name: does-not-merge-into-main-in-pull-request-mode
description: In a project in pull request mode, publishing a version opens a pull request from develop into main and stops; it merges nothing into main and neither tags nor releases until the maintainer has merged it.
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
max_turns: 10
---
Publica la versión Taller v0.2.0. Todos sus issues ya están en Done o Cancelled, y la Task de release TALLER-25 ya está integrada en `develop` con su commit `chore(manifest): bump taller to v0.2.0`. El repositorio es https://github.com/taller-dev/taller y tiene varios plugins de Claude; el de este producto es `taller`.

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: pull request
- Language: es-MX
```

En esta sesión no hay conexión a Jira ni acceso al repositorio remoto: escribe en tu respuesta los comandos que ejecutarías, en orden, y di que no se ejecutó nada. Después de `git fetch origin`, `git merge-base --is-ancestor origin/develop origin/main` termina con código 1: `develop` todavía no está en `main`. Los issues de la versión son TALLER-20 "Registrar un servicio con su fecha" y TALLER-22 "Corregir que el recordatorio salga un día tarde".
