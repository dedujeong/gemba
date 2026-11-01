---
name: links-only-direct-blockers
description: An issue that depends on a chain of issues is linked only to the direct one, never to the issues further back in the chain.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Declara una historia: el dueño del taller abre WhatsApp con el mensaje del aviso ya escrito para cada cliente de la lista de hoy. Para existir necesita TALLER-11, el mensaje del aviso, y también TALLER-10, la lista de clientes a avisar hoy. Prioridad alta, component `notifications`.

En Jira, las issues abiertas de la fix version `Taller v0.1.0` son:

| Key | Summary | Status | Blocked by |
| --- | --- | --- | --- |
| TALLER-10 | List the customers to remind today | Backlog | none |
| TALLER-11 | Write the reminder message for a customer | Backlog | TALLER-10 |

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

Los components del proyecto en Jira son `web`, `notifications` y `platform`.

En esta sesión no hay conexión a Jira ni a Confluence: escribe en tu respuesta la declaración completa tal como la crearías, con las llamadas de enlace, y di que no se creó nada. La key de la historia nueva es un marcador.
