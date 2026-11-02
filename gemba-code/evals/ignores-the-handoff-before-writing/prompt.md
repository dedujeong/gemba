---
name: ignores-the-handoff-before-writing
description: Before writing a handoff, the session close makes sure .gemba/sessions is ignored by .gitignore, with a comment that says what it ignores and a blank line after the previous section.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Guarda el estado de la sesión, termino por hoy.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

La rama es `story/TALLER-12-save-the-vehicle`, TALLER-12 está en Implement, la fix version es `Taller v0.2.0` y no hay nada más que decir de la sesión. El `.gitignore` del proyecto tiene hoy exactamente esto y todavía no ignora `.gemba/sessions/`:

```
# Python bytecode
__pycache__/

# Local environment
.env
```

En esta sesión no hay conexión a Jira ni se pueden ejecutar comandos ni escribir archivos: describe en tu respuesta, en el orden en que lo harías, cómo dejarías el `.gitignore` (con el texto exacto resultante) y el handoff, y di que no se escribió nada.
