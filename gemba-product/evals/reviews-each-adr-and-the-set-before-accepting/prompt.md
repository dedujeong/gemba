---
name: reviews-each-adr-and-the-set-before-accepting
description: When the person is about to accept a set of proposed ADRs, Claude reviews each ADR and the whole set with the four heuristics before accepting any.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 6
---
Estamos en el paso de arquitectura del discovery de una app de recordatorios de mantenimiento por WhatsApp para talleres mecánicos pequeños, en el espacio PRODUCTOS. El MVP tiene dos historias: guardar la fecha del siguiente servicio de cada cliente y enviarle un recordatorio por WhatsApp cuando se acerca esa fecha. En la carpeta Decisions no hay ADR aceptados. Estos son los tres ADR propuestos (estado Rough draft):

ADR-0001 Hosting estático
Context: La historia de guardar la fecha necesita una pantalla web que el dueño abra desde el celular.
Decision: El frontend se aloja como sitio estático en Cloudflare Pages.
Alternatives: Un servidor propio, descartado por el costo de operarlo.
Consequences: Todo el código del frontend se ejecuta en el navegador del dueño.
Source: Product Brief.

ADR-0002 Base de datos
Context: Las fechas de servicio y los teléfonos de los clientes deben guardarse.
Decision: Postgres en Supabase, plan gratuito.
Alternatives: Una hoja de cálculo, descartada porque no controla quién lee los teléfonos.
Consequences: Los datos viven en Supabase.
Source: Product Brief.

ADR-0003 Proveedor de WhatsApp
Context: La historia del recordatorio necesita enviar mensajes por WhatsApp.
Decision: El frontend llama directo a la API de un proveedor de WhatsApp con su clave.
Alternatives: Enviar los mensajes a mano desde el WhatsApp del dueño, descartado porque es lo que se quiere dejar de hacer.
Consequences: Cada recordatorio se manda desde la pantalla del dueño.
Source: Product Brief.

La persona dice: "Los tres me convencen, acéptalos". No hay conexión a Confluence en esta sesión: dime en la respuesta qué haces con ellos.
