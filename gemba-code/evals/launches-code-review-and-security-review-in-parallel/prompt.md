---
name: launches-code-review-and-security-review-in-parallel
description: A code change that review decides to review launches code-review at a level chosen by size and risk and security-review in parallel, and says what it launched and why.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Revisa TALLER-52.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira, ni cambios reales de git, ni se ejecutan los tests ni las revisiones de código: no las lances de verdad, di cuáles lanzarías. Sigue el flujo hasta terminar la revisión y entrega las acciones como una tabla con las columnas Acción, Herramienta y valores, una fila por acción.

TALLER-52 es una Story en Implement, con un solo criterio: dado un dueño de taller con sesión iniciada, cuando abre el detalle de un cliente de otro taller, entonces se le niega el acceso. Todos sus tests están en verde y el criterio se cumple. Los archivos de la rama frente a `develop` (`git diff --name-only develop...story/TALLER-52-deny-other-shops`) son:

```
src/auth/session.ts
src/auth/permissions.ts
src/customers/customer-detail.ts
src/customers/customer-detail.test.ts
db/migrations/0007-customer-shop-policy.sql
```

Y `git diff --shortstat` dice: 5 files changed, 312 insertions(+), 48 deletions(-). El issue pasó a Review hoy a las 09:00 (hora de la Ciudad de México, -0600) y ahora son las 09:20.
