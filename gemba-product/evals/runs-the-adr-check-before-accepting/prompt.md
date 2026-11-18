---
name: runs-the-adr-check-before-accepting
description: Before accepting a set of ADRs, Claude runs the script that checks that the ADR states, the Architecture page and the Spikes agree, and accepts nothing if it reports a discordance.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 6
---
Estamos en el paso de arquitectura del discovery de una app de recordatorios de mantenimiento por WhatsApp para talleres mecánicos pequeños, en el espacio PRODUCTOS. Esto hay en el espacio:

ADR-0001 Proveedor de mapas: aceptado (página en estado Verified con panel success). Su Context dice que depende del Spike GEMBA-12, que probó el proveedor con datos reales. El Spike GEMBA-12 está en Implement en Jira.
ADR-0002 Hosting estático: propuesto (Rough draft), el único del conjunto que se va a aceptar.
La página Architecture lista ADR-0001 como Ready to decide y ADR-0002 como Proposed.

La revisión de ADR con las cuatro heurísticas ya pasó sin ninguna pregunta abierta. La persona dice: "Acepta el ADR-0002". No hay conexión a Confluence ni a Jira en esta sesión: dime en la respuesta qué haces.
