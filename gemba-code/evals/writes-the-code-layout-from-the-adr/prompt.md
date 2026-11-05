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

Organizar el código por dominio. Gana porque cada historia toca sobre todo una carpeta, y lo compartido queda aparte.

- `src/lib/business`, `src/lib/menu` y `src/lib/order`, cada una con `components`, `services`, `types.ts` e `index.ts`; `src/lib/shared` con `ui`, `supabase` y `r2`.
- Rutas: `(public)/[business]`, `(auth)/login` y `(admin)/dashboard`.
- Las pruebas unitarias con Vitest van junto al archivo, con su mismo nombre (`business.server.test.ts`); `tests/e2e` con Playwright y `supabase/migrations` van en la raíz del repositorio.
- Archivos en kebab-case y componentes de Svelte en PascalCase.
</adr>

En esta sesión no hay conexión a Jira ni a Confluence y no puedes escribir archivos: escribe en tu respuesta el contenido completo del CLAUDE.md tal como quedaría.
