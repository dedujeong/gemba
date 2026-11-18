---
name: asks-for-the-artboards-before-reading-the-design
description: Taking an interface Story with no Artboards section, implement stops and asks which artboards it uses before reading the design.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Toma TALLER-40.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Jira Site: taller.atlassian.net
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira, ni a Confluence, ni cambios reales de git. TALLER-40 es una Story en Backlog, sin bloqueos, de la fix version `Taller v0.1.0`, component `web`, con el Summary `Show the list of customers to notify today`. Es una Story de interfaz: el dueño la hace a través de una pantalla. Su descripción es:

```
Como dueño del taller, quiero ver la lista de clientes a avisar hoy, para llamarlos.

### Acceptance criteria
- Dado que hay clientes por avisar hoy, cuando el dueño abre la lista, entonces ve a cada uno de ellos.
```

No tiene sección de artboards. El prototipo está en la página `Design` del espacio, con muchos artboards de otras pantallas. Entrega las acciones que harías como una tabla con las columnas Acción, Herramienta y valores, una fila por acción, y escribe lo que le dirías al maintainer.
