---
name: asks-about-a-file-the-layout-does-not-cover
description: A new file of a kind the Code layout does not mention is named with the proposed line of the Code layout, and it does not block the issue.
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

- `orders`, domain, `src/orders/`.
- `customers`, domain, `src/customers/`.
- `shared`, technical, `src/shared/`.
- Lo que cambia junto queda junto, y un dominio depende de otro solo por su archivo de entrada, en una sola dirección.
- Validador: `pnpm check-layout`.
```

En esta sesión no hay conexión a Jira, ni cambios reales de git, ni se ejecutan los tests ni el validador, que pasa. Sigue el flujo hasta terminar la revisión y entrega las acciones como una tabla con las columnas Acción, Herramienta y valores, una fila por acción.

TALLER-42 es una Story en Implement, con un solo criterio: dado un pedido, cuando se ve su detalle, entonces se ve el total. Todos sus tests están en verde y el criterio se cumple. El resultado de `git diff --name-status --diff-filter=AR develop...story/TALLER-42-order-total` es:

```
A	src/orders/order-total.ts
A	src/orders/order-total.test.ts
A	scripts/seed-orders.sh
```

El issue pasó a Review hoy a las 09:00 (hora de la Ciudad de México, -0600) y ahora son las 09:20.
