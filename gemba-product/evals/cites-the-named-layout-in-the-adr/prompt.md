---
name: cites-the-named-layout-in-the-adr
description: When the derived layout matches a layout that has a name, the ADR of the layout cites it.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 6
---
Estamos en el discovery de una app de reservas para un estudio de yoga con un solo local, en el espacio PRODUCTOS. Ya propusiste las decisiones de arquitectura y la persona acepta registrar la del layout del código, derivado así:

- Cada dominio es una rebanada vertical con su carpeta: `src/schedule/`, `src/bookings/` y `src/roster/`. Dentro de cada una van sus pantallas, su lógica y su acceso a datos; no hay carpetas por capas.
- Cada dominio expone un solo archivo público, `index.ts`, y los demás archivos son privados.
- Sentido de las dependencias: `bookings` usa `schedule` y `roster` usa `bookings`.
- Área compartida: `src/shared/`.
- Validador: `scripts/check-layout.ts`.

El ADR más alto de la carpeta es ADR-0002. No hay conexión a Confluence en esta sesión: escribe en la respuesta cómo quedaría la página del ADR del layout.
