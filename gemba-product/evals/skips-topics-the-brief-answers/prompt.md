---
name: skips-topics-the-brief-answers
description: The brief already answers team and budget; Claude asks nothing about those two topics and still asks about operation and data.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 5
---
Estamos en el discovery de una app de recordatorios de mantenimiento por WhatsApp para talleres mecánicos pequeños, en el espacio PRODUCTOS. El Story Map ya está cerrado con su MVP y toca decidir la arquitectura. Este es el contenido del Product Brief, con la fuente de cada hecho:

Problem: El dueño avisa a mano a cada cliente cuándo le toca su siguiente servicio y a veces se le olvida (Interview).
Primary job: Cuando le toca servicio a un cliente, quiero avisarle por WhatsApp sin revisar la libreta, para que vuelva a tiempo (Interview).
Actors and permissions: Dueño (usuario principal) y un mecánico que atiende el mostrador (Secondhand).
Current workflow: El dueño anota las fechas en una libreta de papel y escribe a mano desde su WhatsApp personal (Interview).
Context: Unos 40 clientes por semana (Interview).
Willingness to pay: Hoy el taller no paga ninguna herramienta (Interview).
Starting point: Lo va a desarrollar una sola persona, con Python y Postgres, que ya conoce (Interview).

Sin conexión a Confluence en esta sesión: con este contenido, empieza el paso de arquitectura y escribe tu respuesta.
