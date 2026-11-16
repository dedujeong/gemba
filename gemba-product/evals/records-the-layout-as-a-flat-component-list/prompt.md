---
name: records-the-layout-as-a-flat-component-list
description: The code layout the person accepts is recorded as an ADR with one flat list of components, each with its type and path, and the validator that checks the two rules.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 6
---
Estamos en el discovery de una app de reservas para un estudio de yoga con un solo local, en el espacio PRODUCTOS. Ya propusiste las decisiones de arquitectura y las revisamos. La persona acepta registrar la del layout del código, derivado así:

- Dominios con carpeta propia: `src/schedule/` (clases y horario), `src/bookings/` (reservas) y `src/roster/` (quién está anotado). Cada dominio tiene su archivo de entrada `index.ts`.
- Sentido de las dependencias: `bookings` usa `schedule`, `roster` usa `bookings`; nunca al revés.
- Área compartida: `src/shared/` (fechas, errores).
- Validador: un script `scripts/check-layout.ts` que revisa las dos reglas (lo junto cambia junto; dependencias en un solo sentido por la entrada pública).

Alternativas: carpetas por capas (`controllers/`, `services/`, `models/`), descartada porque una historia toca todas las carpetas; y un solo dominio `studio/`, descartado porque mezcla reservas con horario. Fuente: el MVP cerrado y el Constraints de Equipo (TypeScript y Postgres). El ADR más alto de la carpeta es ADR-0002.

No hay conexión a Confluence en esta sesión: escribe en la respuesta cómo quedaría la página y en qué carpeta va.
