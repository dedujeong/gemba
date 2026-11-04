---
name: writes-product-names-in-an-adr-as-plain-text
description: Product, provider and tool names in an ADR are plain text, while the technical names next to them keep code style.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 6
---
Estamos en el paso de arquitectura del discovery de una app de reservas para un estudio de yoga, en el espacio PRODUCTOS. La persona acepta registrar una sola decisión: usar Supabase como base de datos y Cloudflare Pages para el frontend, con el código en GitHub. Los datos, escritos tal como me los dieron:

- La base es Postgres dentro de Supabase; la configuración vive en supabase/config.toml y las migraciones se aplican con el comando supabase db push.
- El frontend se despliega en Cloudflare Pages desde GitHub; la carpeta de salida es dist.
- Alternativas descartadas: Firebase, porque el equipo ya conoce SQL y no Firestore; y Vercel Hobby, porque no permite uso comercial (Vercel Fair Use Guidelines, consultado el 2026-11-02).

Contexto: el MVP cerrado necesita reservar clases y el equipo ya conoce SQL. Fuente: el MVP cerrado del Story Map. El ADR más alto de la carpeta es ADR-0003.

No hay conexión a Confluence en esta sesión: escribe en la respuesta cómo quedaría la página y en qué carpeta va.
