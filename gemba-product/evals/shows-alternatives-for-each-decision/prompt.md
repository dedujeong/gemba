---
name: shows-alternatives-for-each-decision
description: An architecture decision Claude proposes shows the proposed option, two or three real alternatives with the reason each loses, and why the proposed one was chosen.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 6
---
Estamos en el discovery de una app de órdenes de reparación para un taller de bicicletas con un solo local, en el espacio PRODUCTOS. Ya hicimos la ronda de preguntas de arquitectura y sus respuestas ya están en el Constraints del brief. Este es el contenido del Product Brief:

Problem: El dueño anota las reparaciones en una libreta y los clientes llaman para preguntar si su bicicleta ya está lista (Interview).
Primary job: Cuando un cliente deja su bicicleta, quiero registrar la orden y que él pueda ver su estado, para no contestar llamadas (Interview).
Constraints:
- **Costo:** debe caber en planes gratuitos (Interview).
- **Operación:** lo opera una sola persona que solo quiere alertas de error (Interview).
- **Equipo:** quien lo desarrolla sabe Python y Postgres (Interview).
- **Datos:** guarda nombre y teléfono de cada cliente (Interview).

El release actual del Story Map, con el MVP cerrado, tiene estas historias:
1. Registrar una orden con el cliente y su bicicleta.
2. Cambiar el estado de una orden.
3. Consultar el estado de mi orden con un enlace.
4. Ver, como dueño, las órdenes abiertas.

Las demás decisiones de arquitectura ya las tomamos y las registramos. Falta una sola: con qué se construye la aplicación, es decir el lenguaje y el framework. Propónmela ahora y no toques las otras. No hay conexión a Confluence en esta sesión: escribe tu propuesta en la respuesta.
