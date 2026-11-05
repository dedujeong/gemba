---
name: proposes-only-the-missing-readme-sections
description: A repository that already has a README keeps it untouched and setup proposes only the template sections it lacks, counting an equivalent heading as present.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Quiero dejar listo este repositorio para trabajar con Gemba Code. El proyecto de Jira es TALLER, el espacio de Confluence es TALLER, trabajo solo, así que cierro con merge local, y todo va en español de México. El repositorio ya tiene este README.md:

<readme>
# Taller

Recordatorios del siguiente servicio para talleres mecánicos.

## What it is

Los talleres mecánicos pequeños avisan a mano a cada cliente cuándo le toca su siguiente servicio y a veces se les olvida. Taller se lo recuerda al cliente.

## Installation

Instala las dependencias con `pnpm install`.
</readme>

En esta sesión no hay conexión a Jira ni a Confluence, no puedes ejecutar comandos ni escribir archivos. Dime qué pasa con el README.md del repositorio: si cambia, qué se propone y qué queda como está.
