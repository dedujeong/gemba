---
name: writes-answers-into-constraints
description: After the architecture round is answered, the answers go into the Constraints section of the brief, next to the constraint it already had.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 6
---
Estamos en el discovery de una app para que un grupo de amigos se reparta integrantes de grupos de K-pop, en el espacio PRODUCTOS. El Story Map está cerrado con su MVP y estamos en el paso de arquitectura. Este es el contenido actual del Product Brief:

Source (panel info): Este brief parte del relato de uno de los dos usuarios.
Problem (panel error): Dos amigos no saben con certeza quién tiene a cada integrante.
Primary job: Cuando quiero apartar a una integrante, quiero ver si ya tiene dueño, para repartirnos sin confusiones.
Constraints: **Costo:** debe caber en planes gratuitos (Interview).
Glossary: "Apartar" es reclamar a una integrante para que el otro no la pueda tener.
Open decisions: [ ] ¿La tier list ordena cada grupo por separado?

Ya contesté la ronda de preguntas de arquitectura. Mis respuestas: opero la app yo solo y solo quiero alertas de error; sé Python, TypeScript y Postgres; la app guarda datos personales de los miembros, incluida su edad.

Con eso termina la ronda. En esta sesión no hay conexión a Confluence: lo que escribirías en Confluence, ponlo en tu respuesta con el cuerpo completo del brief tal como quedaría.
