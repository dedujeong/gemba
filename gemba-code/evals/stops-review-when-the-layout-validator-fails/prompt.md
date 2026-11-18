---
name: stops-review-when-the-layout-validator-fails
description: An issue in Implement with every test green stays in Implement when the layout validator of the Code layout fails.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Revisa TALLER-31.

El CLAUDE.md del proyecto tiene este contenido:

```
## Gemba

- Jira Project: TALLER
- Jira Site: taller.atlassian.net
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

En esta sesión no hay conexión a Jira, ni cambios reales de git. Sigue el flujo hasta terminar y entrega las acciones como una tabla con las columnas Acción, Herramienta y valores, una fila por acción.

TALLER-31 es una Story en Implement, sin bloqueos, de la fix version `Taller v0.1.0`, con el Summary `Show the phone of each customer in today's list`. Su construcción terminó y todos sus tests están en verde. Al correr `pnpm check-layout` el resultado es: `error: src/orders/order-list.ts imports src/customers/customer-store.ts, which is not the entry of customers`, y el comando termina con código 1.
