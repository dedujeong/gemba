---
name: skips-code-reviews-for-docs-and-skills
description: A change that only touches docs, skills or behavior launches no code review and says that it is verified with evals or another mechanism.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Revisa TALLER-50.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira, ni cambios reales de git, ni se ejecutan los tests ni las revisiones de código. Sigue el flujo hasta terminar la revisión y entrega las acciones como una tabla con las columnas Acción, Herramienta y valores, una fila por acción.

TALLER-50 es una Story en Implement, con un solo criterio: dado un recordatorio, cuando la skill lo redacta, entonces usa el nombre del taller. Todos sus tests están en verde y el criterio se cumple. Los archivos de la rama frente a `develop` (`git diff --name-only develop...story/TALLER-50-reminder-text`) son:

```
plugin/skills/remind/SKILL.md
plugin/evals/uses-the-shop-name/prompt.md
plugin/evals/uses-the-shop-name/graders/criteria.md
README.md
```

Y `git diff --shortstat` dice: 4 files changed, 41 insertions(+), 6 deletions(-). El issue pasó a Review hoy a las 09:00 (hora de la Ciudad de México, -0600) y ahora son las 09:20.
