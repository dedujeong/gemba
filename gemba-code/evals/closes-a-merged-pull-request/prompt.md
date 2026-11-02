---
name: closes-a-merged-pull-request
description: In a project in pull request mode, closing an issue whose pull request the maintainer already merged brings develop up to date, deletes the branch, logs the Review time and moves the issue to Done, without merging anything.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Cierra TALLER-43.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: pull request
- Language: es-MX
```

En esta sesión no hay conexión a Jira ni cambios reales de git o de GitHub. Sigue el flujo hasta terminar y entrega las acciones como una tabla con las columnas Acción y Comando o herramienta, una fila por acción, en el orden en que se hacen.

TALLER-43 es una Story en Review, con la rama `story/TALLER-43-show-the-phone-of-each-customer`. Entró a Review hoy a las 15:00 (hora de la Ciudad de México, -0600) y ahora, a las 15:10, el maintainer te pide cerrarla. Su pull request #8 ya está mergeado: `gh pr view` devuelve `state: MERGED`, `mergedAt: 2026-11-01T14:58:00-0600` y la url `https://github.com/taller/app/pull/8`. La rama remota ya no existe.
