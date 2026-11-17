---
name: writes-the-code-layout-from-the-adr
description: Given an accepted ADR of the code layout, setup writes a Code layout section in the CLAUDE.md with the folders, the tests, the file names and the migrations of the ADR.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Quiero dejar listo este repositorio para trabajar con Gemba Code. Todavía no tiene CLAUDE.md. El proyecto de Jira es MESA, el espacio de Confluence también es MESA, trabajo solo, así que cierro con merge local, y todo va en español de México. Esta es la decisión de layout del código que dejó architecture en la carpeta Decisions del espacio. Su estado es Verified y ningún ADR posterior la reemplaza:

<adr>
# ADR-0008 Code layout por dominio

## Decision

Organizar el código por dominio, como en un layout por funcionalidad (feature-sliced). Gana porque cada historia toca sobre todo una carpeta, y lo compartido queda aparte.

- `business`, tipo `domain`, ruta `src/lib/business/`.
- `menu`, tipo `domain`, ruta `src/lib/menu/`.
- `order`, tipo `domain`, ruta `src/lib/order/`.
- `shared`, tipo `technical`, ruta `src/lib/shared/`.
- Validador: `pnpm check-layout`, que comprueba las dos reglas: lo que cambia junto queda junto, y cada dominio depende de otro solo por su archivo de entrada, en una sola dirección.
</adr>

En esta sesión no hay conexión a Jira ni a Confluence y no puedes escribir archivos: escribe en tu respuesta el contenido completo del CLAUDE.md tal como quedaría.
