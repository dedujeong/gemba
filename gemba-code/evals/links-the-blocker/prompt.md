---
name: links-the-blocker
description: An issue that depends on another is declared with the blocking link between the two.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Declara una historia: el dueño del taller abre WhatsApp con el mensaje del aviso ya escrito para cada cliente de la lista de hoy. Depende de TALLER-10, la lista de clientes a avisar hoy, que sigue en Backlog. Prioridad alta, component `notifications`.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

La fix version abierta es `Taller v0.1.0`. Los components del proyecto en Jira son `web`, `notifications` y `platform`.

En esta sesión no hay conexión a Jira ni a Confluence: escribe en tu respuesta la declaración completa tal como la crearías (work type, summary, campos y descripción en el formato en que se enviaría) y di que no se creó nada.
