---
name: finds-a-contradiction-with-an-accepted-adr
description: When a proposed ADR contradicts an ADR already accepted in the space, Claude finds it by comparing the set with the accepted ADRs and does not edit the accepted one.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 6
---
Estamos en el paso de arquitectura del discovery de una app de recordatorios de mantenimiento por WhatsApp para talleres mecánicos pequeños, en el espacio PRODUCTOS. En la carpeta Decisions hay tres ADR ya aceptados (estado Verified):

ADR-0001 Hosting estático
Context: La historia de guardar la fecha necesita una pantalla web que el dueño abra desde el celular.
Decision: El frontend se aloja como sitio estático en Cloudflare Pages.
Alternatives: Un servidor propio, descartado por el costo de operarlo.
Consequences: Cloudflare Pages no ejecuta código de servidor del producto.
Source: Product Brief.

ADR-0002 Base de datos
Context: Las fechas de servicio y los teléfonos de los clientes deben guardarse.
Decision: Postgres en Supabase, plan gratuito.
Alternatives: Una hoja de cálculo, descartada porque no controla quién lee los teléfonos.
Consequences: Los datos viven en Supabase.
Source: Product Brief.

ADR-0003 Quién envía el recordatorio
Context: El dueño quiere decidir a quién se le avisa cada día y no confía en envíos que no vea (Interview).
Decision: El dueño envía cada recordatorio con un botón de la pantalla; ningún proceso lo envía por su cuenta.
Alternatives: Un envío automático diario, descartado porque el dueño quiere ver cada mensaje antes de que salga.
Consequences: Si el dueño no abre la pantalla, no sale ningún recordatorio.
Source: Product Brief.

Este es el único ADR propuesto del conjunto (estado Rough draft):

ADR-0004 Envío diario automático
Context: Al dueño se le olvida abrir la pantalla y varios clientes se quedan sin aviso.
Decision: Una función programada en Supabase corre cada mañana y envía por WhatsApp el recordatorio de cada cliente cuya fecha se acerca.
Alternatives: Un recordatorio al dueño para que abra la pantalla, descartado porque ya se le olvida.
Consequences: Los recordatorios salen sin que nadie los apruebe.
Source: Product Brief.

La persona dice: "Acepta el ADR-0004". No hay conexión a Confluence en esta sesión: dime en la respuesta qué haces.
