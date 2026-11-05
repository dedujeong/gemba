---
name: returns-to-implement-when-a-test-fails-after-simplify
description: With the findings resolved, review runs simplify and then the tests again, and an issue with a failing test does not pass.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Revisa TALLER-54.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira, ni cambios reales de git, ni se ejecutan los tests, las revisiones ni /simplify; los resultados te los doy aquí. Sigue el flujo hasta terminar la revisión y entrega las acciones como una tabla con las columnas Acción, Herramienta y valores, una fila por acción.

TALLER-54 es una Story en Implement, de la fix version `Taller v0.1.0`, con un solo criterio: dado un pedido, cuando se calcula su total, entonces incluye el descuento. Todos sus tests estaban en verde y el criterio se cumple. El cambio toca `src/orders/total.ts` y su test (180 líneas); review lanzó `/code-review` en nivel `high` y `/security-review`, y los dos terminaron sin hallazgos. Después se corrió `/simplify`, y al volver a correr los tests de nuevo falla uno: `total.test.ts › aplica el descuento a un pedido con dos productos` (esperaba 90 y obtuvo 100). El issue pasó a Review hoy a las 15:00 (hora de la Ciudad de México, -0600) y ahora son las 15:25.
