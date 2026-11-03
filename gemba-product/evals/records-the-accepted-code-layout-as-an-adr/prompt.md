---
name: records-the-accepted-code-layout-as-an-adr
description: The code layout the person accepts is recorded as its own ADR, with alternatives and consequences, like any other decision.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 6
---
Estamos en el discovery de una app de reservas para un estudio de yoga con un solo local, en el espacio PRODUCTOS. Ya propusiste las decisiones de arquitectura y las revisamos. La persona acepta registrar la del layout del código, con esto:

- Carpetas por dominio: `src/schedule/`, `src/bookings/`, `src/roster/` y `src/shared/`.
- Pruebas: junto al código, como `bookings/create-booking.test.ts`.
- Nombres: archivos en kebab-case, uno por caso de uso.
- Migraciones: `db/migrations/`, SQL numerado como `0001-create-classes.sql`.

Alternativas: carpetas por capas (`controllers/`, `services/`, `models/`), descartada porque una historia toca todas las carpetas; y una carpeta `tests/` aparte, descartada porque separa cada prueba de lo que prueba. Fuente: el MVP cerrado y el Constraints de Equipo (TypeScript y Postgres). El ADR más alto de la carpeta es ADR-0002.

No hay conexión a Confluence en esta sesión: escribe en la respuesta cómo quedaría la página y en qué carpeta va.
