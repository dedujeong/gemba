---
name: writes-the-readme-from-the-template
description: A repository with no README and no stack gets one from the template with only the title, its description and What it is, from the Product Brief.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Quiero dejar listo este repositorio para trabajar con Gemba Code. El proyecto de Jira es TALLER, el espacio de Confluence es TALLER, trabajo solo, así que cierro con merge local, y todo va en español de México. El repositorio es nuevo: no tiene código, ni CLAUDE.md, ni README, ni archivos de dependencias. Este es el Product Brief del espacio de Confluence:

<product-brief>
# Taller

## Problem

Los talleres mecánicos pequeños avisan a mano a cada cliente cuándo le toca su siguiente servicio y a veces se les olvida. El cliente deja de volver a tiempo y el taller pierde ingresos.

## Primary job

> Cuando termino un servicio, quiero que el cliente reciba un recordatorio de su siguiente servicio, para que vuelva a tiempo sin que yo tenga que acordarme.

## Actors and permissions

| Actor | Can do |
| --- | --- |
| Dueño del taller | Registra los servicios y ve a quién le toca recordar. |
| Cliente | Recibe el recordatorio. |
</product-brief>

En esta sesión no hay conexión a Jira ni a Confluence, no puedes ejecutar comandos ni escribir archivos: escribe en tu respuesta el contenido completo del README.md tal como quedaría.
