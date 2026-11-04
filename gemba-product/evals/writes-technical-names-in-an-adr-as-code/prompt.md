---
name: writes-technical-names-in-an-adr-as-code
description: Paths, files, folders, columns, domains and commands named in an ADR are written with code style.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 6
---
Estamos en el paso de arquitectura del discovery de una app de reservas para un estudio de yoga, en el espacio PRODUCTOS. La persona acepta registrar la decisión de guardar las reservas en una sola tabla y publicar la app en un subdominio propio. Los datos de la decisión, escritos tal como me los dieron:

- La tabla es bookings, con la columna starts_at para la hora de la clase y la columna student_id para la alumna.
- Las migraciones van en la carpeta db/migrations y el archivo de configuración de la base es supabase/config.toml.
- La app se publica en reservas.estudio-yoga.mx y la carpeta de salida es dist.
- Las migraciones se aplican con el comando supabase db push.

Contexto: el MVP cerrado necesita reservar clases y el equipo ya conoce SQL. Alternativa descartada: una tabla por tipo de clase, porque cada historia tendría que tocar varias tablas. Fuente: el MVP cerrado del Story Map. El ADR más alto de la carpeta es ADR-0003.

No hay conexión a Confluence en esta sesión: escribe en la respuesta cómo quedaría la página y en qué carpeta va.
