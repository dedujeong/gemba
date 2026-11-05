---
name: checks-only-the-added-and-renamed-files
description: Review checks against the Code layout only the files the branch adds or renames, and leaves a modified file alone even if it sits outside the layout.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Revisa TALLER-43.

El CLAUDE.md del proyecto tiene este contenido:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX

## Code layout

- **Folders:** por dominio en `src/orders` y `src/customers`, y lo compartido en `src/shared`.
- **Tests:** las pruebas van junto al archivo, con su mismo nombre y la terminación `.test.ts`.
- **File names:** archivos en kebab-case.
- **Migrations:** `db/migrations`, SQL numerado.
```

En esta sesión no hay conexión a Jira, ni cambios reales de git, ni se ejecutan los tests. Sigue el flujo hasta terminar la revisión y entrega las acciones como una tabla con las columnas Acción, Herramienta y valores, una fila por acción.

TALLER-43 es una Story en Implement, con un solo criterio: dado un cliente, cuando se ve su detalle, entonces se ve su teléfono. Todos sus tests están en verde y el criterio se cumple. Los archivos de la rama frente a `develop` son:

```
git diff --name-status --diff-filter=AR develop...story/TALLER-43-customer-phone
A	src/customers/customer-phone.ts
R100	src/old/phone-format.ts	src/shared/phone-format.ts

git diff --name-status develop...story/TALLER-43-customer-phone (todos los cambios)
A	src/customers/customer-phone.ts
R100	src/old/phone-format.ts	src/shared/phone-format.ts
M	legacy/Utils.js
```

legacy/Utils.js ya existía en `develop` con ese lugar y ese nombre, y la rama sólo lo modificó. El issue pasó a Review hoy a las 09:00 (hora de la Ciudad de México, -0600) y ahora son las 09:20.
