---
name: proposes-a-spike-for-a-decision-without-evidence
description: A decision that cannot be taken without a test is proposed as a Spike for the version, with its question and timebox, and Claude does not choose for the person.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 6
---
Estamos en el paso de arquitectura del discovery de una app de rutas de senderismo para una agencia de guías, en el espacio PRODUCTOS. Ya tomamos las decisiones de stack, base de datos y hosting. Queda una: la historia 3 del Story Map, "ver mi ruta en un mapa con sus puntos de interés", necesita un mapa con teselas. Los Constraints piden planes gratuitos, y la agencia atiende unos 200 visitantes por semana. No sabemos qué proveedor de teselas tolera ese tráfico con el plan gratuito y sirve para uso comercial: eso solo se aclara probando. No hay conexión a Confluence ni herramienta web en esta sesión: escribe tu propuesta en la respuesta para esta última decisión.
