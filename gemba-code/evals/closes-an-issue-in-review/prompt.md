---
name: closes-an-issue-in-review
description: An issue in Review that the maintainer asks to close is merged into develop with --no-ff, develop is pushed, the branch is deleted, its Review time is logged and the issue moves to Done.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Cierra TALLER-40.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira ni cambios reales de git. Sigue el flujo hasta terminar y entrega las acciones como una tabla con las columnas Acción, Herramienta y valores, una fila por acción, en el orden en que se hacen.

TALLER-40 es una Story en Review, con la rama `story/TALLER-40-show-the-phone-of-each-customer`. Entró a Review hoy a las 15:00 (hora de la Ciudad de México, -0600), el maintainer revisó el resultado y ahora, a las 15:10, te pide cerrarla.
