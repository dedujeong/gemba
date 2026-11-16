---
name: names-the-artboards-of-an-interface-story
description: An interface Story is declared with an Artboards section that lists only the artboards the Design page assigns to it.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Declara esta Story, prioridad alta, component `web`, sin bloqueos: como dueño del taller, quiero ver la lista de clientes a avisar hoy, para llamarlos. Su único criterio ya está decidido: dado que hay clientes por avisar hoy, cuando el dueño abre la lista, entonces ve a cada uno de ellos. No hay más reglas, ni fuera de alcance, ni dudas pendientes: declárala sin hacer preguntas.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

La fix version abierta es `Taller v0.1.0`. Los components del proyecto en Jira son `web`, `notifications` y `platform`.

La sección `Prototype` de la página `Design` del espacio dice:

```
Prototype
- Superficie Admin web, 6 artboards.
- `Notices-Today-Default`: lista de clientes a avisar hoy (Story: lista de avisos de hoy).
- `Notices-Today-Empty`: la misma lista sin clientes (Story: lista de avisos de hoy).
- `Notice-Detail-Default`: detalle de un aviso (Story: detalle de un aviso).
- `Notice-Detail-Sent`: detalle de un aviso ya enviado (Story: detalle de un aviso).
- `Login-Default`: inicio de sesión (Story: inicio de sesión).
- `Login-Error`: inicio de sesión con error (Story: inicio de sesión).
```

La Story de este pedido es «lista de avisos de hoy».

En esta sesión no hay conexión a Jira ni a Confluence: escribe en tu respuesta la declaración completa tal como la crearías (work type, summary, campos y descripción en el formato en que se enviaría) y di que no se creó nada.
