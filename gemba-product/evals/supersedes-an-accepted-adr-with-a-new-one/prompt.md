---
name: supersedes-an-accepted-adr-with-a-new-one
description: When the decision of an accepted ADR changes, Claude creates a new ADR that replaces it and leaves the content of the accepted one unchanged.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 6
---
Estamos en el paso de arquitectura del discovery de una app de órdenes de reparación para un taller de bicicletas, en el espacio PRODUCTOS. En la carpeta Decisions hay dos ADR de arquitectura, ambos aceptados (estado Verified):

ADR-0001 Cloudflare Pages
Context: El taller cobrará por sus servicios, así que el hosting debe permitir uso comercial.
Decision: El frontend se aloja en Cloudflare Pages.
Alternatives: Vercel Hobby, descartado porque no permite uso comercial (Vercel Fair Use Guidelines, consultado el 2026-11-02).
Consequences: El despliegue depende de Cloudflare; el plan gratuito cubre el MVP.
Source: Product Brief.

ADR-0002 Supabase con Postgres
Context: Una sola persona opera el sistema y sabe Postgres.
Decision: Backend y base de datos en Supabase.
Alternatives: Servidor propio con FastAPI, descartado por el costo de operarlo.
Consequences: Los datos viven en Supabase.
Source: Product Brief.

El taller decidió abrir una segunda sucursal y el plan gratuito de Cloudflare Pages ya no alcanza, así que el hosting cambia a Vercel Pro, que sí permite uso comercial. No hay conexión a Confluence en esta sesión: dime en la respuesta qué páginas se crean y qué cambia en cada una.
