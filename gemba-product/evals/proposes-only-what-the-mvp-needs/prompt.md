---
name: proposes-only-what-the-mvp-needs
description: With the MVP closed and the round answered, every architecture decision Claude proposes points to a story of the MVP or a constraint of the brief, and nothing the MVP does not ask for is proposed.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 6
---
Estamos en el discovery de una app de reservas para un estudio de yoga con un solo local, en el espacio PRODUCTOS. Ya hicimos la ronda de preguntas de arquitectura y sus respuestas ya están en el Constraints del brief. Este es el contenido del Product Brief:

Problem: La dueña lleva las reservas en un grupo de WhatsApp y a veces se llenan las clases por encima del cupo (Interview).
Primary job: Cuando quiero tomar una clase, quiero ver los lugares libres y apartar uno, para llegar sin dudar si hay cupo (Interview).
Constraints:
- **Costo:** debe caber en planes gratuitos (Interview).
- **Operación:** la dueña no opera nada; lo opera una sola persona que solo quiere alertas de error (Interview).
- **Equipo:** quien lo desarrolla sabe TypeScript y Postgres (Interview).
- **Datos:** guarda nombre y teléfono de cada alumno (Interview).

El release actual del Story Map, con el MVP cerrado, tiene estas historias:
1. Ver el horario de clases con sus lugares libres.
2. Apartar un lugar en una clase.
3. Cancelar mi lugar.
4. Ver, como dueña, quién está anotado en cada clase.

Ahora toca proponer las decisiones de arquitectura. No hay conexión a Confluence en esta sesión: escribe tu propuesta en la respuesta.
