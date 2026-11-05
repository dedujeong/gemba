---
name: asks-about-a-file-the-layout-does-not-cover
description: A new file of a kind the Code layout does not mention is named with a question about covering it, and it does not block the issue.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Revisa TALLER-42.

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

TALLER-42 es una Story en Implement, con un solo criterio: dado un pedido, cuando se ve su detalle, entonces se ve el total. Todos sus tests están en verde y el criterio se cumple. El resultado de `git diff --name-status --diff-filter=AR develop...story/TALLER-42-order-total` es:

```
A	src/orders/order-total.ts
A	src/orders/order-total.test.ts
A	scripts/seed-orders.sh
```

El issue pasó a Review hoy a las 09:00 (hora de la Ciudad de México, -0600) y ahora son las 09:20.
