---
name: mvp-stories-trace-to-the-brief
description: Every MVP story says which problem, job or Quality bar condition of the brief it serves.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Estamos en el discovery de una app de recordatorios de mantenimiento por WhatsApp para talleres mecánicos pequeños, en el espacio PRODUCTOS. El Product Brief está listo. Este es su contenido:

Problem: El dueño avisa a mano a cada cliente cuándo le toca su siguiente servicio y a veces se le olvida; el cliente no vuelve a tiempo.
Primary job: Cuando le toca servicio a un cliente, quiero avisarle por WhatsApp sin revisar la libreta ni escribirle uno por uno, para que vuelva a tiempo.
Actors and permissions: Dueño del taller (usuario principal): registra servicios y manda recordatorios. Cliente: recibe el mensaje.
Current workflow: 1. Anota la fecha del próximo servicio en una libreta. 2. Cada mañana revisa la libreta. 3. Escribe a mano a cada cliente desde su WhatsApp personal.
Quality bar: (a) Un cliente nunca recibe dos recordatorios por el mismo servicio. (b) Solo el dueño puede cambiar el texto del recordatorio.
Open decisions: [ ] ¿Desde qué número de WhatsApp saldrían los avisos?

Arma el Story Map. En esta sesión no hay conexión a Confluence: escribe en tu respuesta el spec JSON del mapa, con todas sus historias, tal como se lo darías al script que construye el whiteboard.
