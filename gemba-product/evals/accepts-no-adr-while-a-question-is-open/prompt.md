---
name: accepts-no-adr-while-a-question-is-open
description: When a question of the ADR review has no answer and the person asks to accept the ADRs, Claude accepts none of the set and says which question is missing.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 6
---
Estamos en el paso de arquitectura del discovery de una app de recordatorios de mantenimiento por WhatsApp para talleres mecánicos pequeños, en el espacio PRODUCTOS. Ya revisaste estos tres ADR propuestos (estado Rough draft) y me hiciste una sola ronda de tres preguntas:

ADR-0001 Hosting estático: el frontend se aloja como sitio estático en Cloudflare Pages.
ADR-0002 Base de datos: Postgres en Supabase, plan gratuito.
ADR-0003 Proveedor de WhatsApp: el frontend llama a la API de un proveedor con su clave, en su plan gratuito de 100 mensajes al mes.

Las preguntas de la ronda fueron:
1. ADR: ADR-0003. Heurística: frontera navegador/servidor. ¿Quién guarda la clave del proveedor si el frontend corre en el navegador del dueño?
2. ADR: el conjunto. Heurística: huecos entre ADR. ¿Qué envía los recordatorios en su fecha si el dueño no abre el sistema?
3. ADR: ADR-0003. Heurística: recurso limitado. ¿Cuántos recordatorios al mes manda el taller?

Te contesté la 2 (los recordatorios los manda el dueño desde un botón) y la 3 (unos 400 al mes). La pregunta 1 no la sé todavía y tengo que preguntarla en el taller. Aun así, "acepta los tres ADR". No hay conexión a Confluence en esta sesión: dime en la respuesta qué haces con cada ADR.
