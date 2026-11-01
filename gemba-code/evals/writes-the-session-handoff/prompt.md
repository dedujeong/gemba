---
name: writes-the-session-handoff
description: Closing a session writes its state to a handoff file in .gemba/sessions with the fixed headings, the facts of the session and a single next step.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Cierra la sesión, termino por hoy. Son las 17:55:03 del 2026-11-01.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

Estado de esta sesión: la rama es `story/TALLER-12-save-the-vehicle` y TALLER-12 "Save the vehicle" está en Implement. Su fix version es `Taller v0.2.0`, del 2026-11-02 al 2026-11-20. La rama tiene un commit sobre develop: `a1b2c3d feat(api): add the endpoint that saves the vehicle`. En el árbol de trabajo queda sin commit `tests/test_vehicle_validation.py`, a medias. En la conversación se decidió guardar la placa en mayúsculas y sin espacios, porque la búsqueda del taller es por placa. Lo siguiente es terminar el test de validación y pasar TALLER-12 a Review. El `.gitignore` del proyecto ya ignora `.gemba/sessions/`.

En esta sesión no hay conexión a Jira ni se pueden ejecutar comandos ni escribir archivos: escribe en tu respuesta el handoff completo tal como lo guardarías, con su ruta, y di que no se escribió nada.
