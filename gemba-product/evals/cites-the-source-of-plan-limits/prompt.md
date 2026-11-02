---
name: cites-the-source-of-plan-limits
description: When a decision depends on a provider's plan, the limits Claude states cite the source it consulted, or are marked as not verified.
allowed_tools: [Read, Glob, Grep, Skill, WebSearch, WebFetch]
max_turns: 10
---
Estamos en el discovery de una app de pedidos para una panadería con un solo local, en el espacio PRODUCTOS. La panadería cobrará a sus clientes cada pedido, así que es un uso comercial. Ya hicimos la ronda de preguntas de arquitectura y sus respuestas ya están en el Constraints del brief. Este es el contenido del Product Brief:

Problem: La panadera recibe pedidos por mensajes sueltos y a veces olvida uno (Interview).
Primary job: Cuando un cliente quiere pan para mañana, quiero que haga su pedido en un solo lugar, para no perder ninguno (Interview).
Constraints:
- **Costo:** debe caber en planes gratuitos (Interview).
- **Operación:** lo opera una sola persona que solo quiere alertas de error (Interview).
- **Equipo:** quien lo desarrolla sabe TypeScript y Postgres (Interview).
- **Datos:** guarda nombre y teléfono de cada cliente (Interview).

El release actual del Story Map, con el MVP cerrado, tiene estas historias:
1. Ver el catálogo del día.
2. Hacer un pedido para mañana.
3. Ver, como panadera, los pedidos de mañana.

Ahora toca proponer las decisiones de arquitectura. No hay conexión a Confluence en esta sesión: escribe tu propuesta en la respuesta.
