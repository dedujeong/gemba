---
name: reviews-that-a-spike-is-reproducible
description: Reviewing a Spike verifies that what was tested is reproducible by running the test again in its worktree, and reports the verdict without closing it.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Revisa TALLER-51.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira ni a Confluence, ni cambios reales de git. Sigue el flujo hasta terminar la revisión y entrega el resultado como una tabla con las columnas Acción, Herramienta y valores, una fila por acción.

TALLER-51 es un Spike en Implement, trabajado en el worktree `.claude/worktrees/TALLER-51-can-we-import-the-old-spreadsheet` con la rama `spike/TALLER-51-can-we-import-the-old-spreadsheet`. Su prueba es el script `probe.py` de ese worktree, que importa la hoja de cálculo vieja. Su página de findings, `TALLER-51 Can we import the old spreadsheet`, está en Rough draft y dice que la hoja se importa completa en 3 segundos. Al volver a correr `probe.py` en el worktree, la hoja se importa completa en 3 segundos.
