---
name: asks-the-adr-review-in-one-round
description: When the review of a set of ADRs finds several gaps, Claude asks all its questions in one single round, each naming its ADR and its heuristic.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 6
---
Estamos en el paso de arquitectura del discovery de una app de recordatorios de mantenimiento por WhatsApp para talleres mecánicos pequeños, en el espacio PRODUCTOS. El brief dice que el taller manda unos 400 recordatorios al mes y que los manda el dueño, que no abre el sistema todos los días. El MVP tiene dos historias: guardar la fecha del siguiente servicio de cada cliente y enviarle un recordatorio por WhatsApp cuando se acerca esa fecha. En la carpeta Decisions no hay ADR aceptados. Estos son los tres ADR propuestos (estado Rough draft):

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
Decision: El frontend llama directo a la API de un proveedor de WhatsApp con su clave, en su plan gratuito de 100 mensajes al mes.
Alternatives: Enviar los mensajes a mano desde el WhatsApp del dueño, descartado porque es lo que se quiere dejar de hacer.
Consequences: Cada recordatorio se manda desde la pantalla del dueño.
Source: Product Brief.

La persona dice: "Revisa los tres y pregúntame lo que haga falta antes de aceptarlos". No hay conexión a Confluence en esta sesión: dime en la respuesta qué haces.
