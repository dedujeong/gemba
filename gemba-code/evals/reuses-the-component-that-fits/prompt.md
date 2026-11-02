---
name: reuses-the-component-that-fits
description: When an existing component fits the part the change touches, the issue is declared with it instead of a new one.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Declara una Story: como dueño del taller, quiero guardar el vehículo de un cliente, para encontrarlo cuando regrese. Es el endpoint del servidor que recibe y guarda el vehículo. Prioridad media, estimado de 2 horas, sin Epic y sin bloqueos.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

La fix version abierta es `Taller v0.1.0`. Los components del proyecto en Jira son `api`, `web` y `ci`.

En esta sesión no hay conexión a Jira ni a Confluence: escribe en tu respuesta la declaración completa tal como la crearías (work type, summary, campos y descripción en el formato en que se enviaría) y di que no se creó nada.
