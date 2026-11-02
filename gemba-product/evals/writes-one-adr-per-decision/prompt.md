---
name: writes-one-adr-per-decision
description: Each architecture decision the person accepts to record gets its own ADR in the Decisions folder, with the title and sections the skill defines.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 6
---
Estamos en el discovery de una app de órdenes de reparación para un taller de bicicletas con un solo local, en el espacio PRODUCTOS. Ya propusiste las decisiones de arquitectura y las revisamos. Quedaron tres, todas por registrar:

1. Frontend: una SPA en React con TypeScript. Alternativas: páginas renderizadas en el servidor con Django, y una app móvil. Se descartó la app móvil porque el cliente consulta su orden con un enlace. Fuente: historia 3 del Story Map.
2. Backend y base de datos: Supabase con Postgres. Alternativa: un servidor propio con FastAPI y Postgres administrado. Se descartó porque una sola persona lo opera y solo quiere alertas de error. Fuente: el Constraints de Operación del brief.
3. Hosting: Cloudflare Pages. Alternativa: Vercel Hobby, descartado porque no permite uso comercial (Vercel Fair Use Guidelines, consultado el 2026-11-02).

La persona acepta registrar las tres. No hay conexión a Confluence en esta sesión: escribe en la respuesta cómo quedaría cada página y en qué carpeta va.
