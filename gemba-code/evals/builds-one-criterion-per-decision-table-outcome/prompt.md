---
name: builds-one-criterion-per-decision-table-outcome
description: A rule that depends on two conditions is worked out in a decision table inside, and the Story gets one criterion per distinct result and no table.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Declara una Story: el dueño del taller registra un pago de un servicio. Prioridad alta, component `web`, sin bloqueos.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

La fix version abierta es `Taller v0.1.0`. Los components del proyecto en Jira son `web`, `notifications` y `platform`.

Esto es lo único que dice el Product Brief sobre pagos:

> Un pago es un anticipo o una liquidación. Un anticipo menor al saldo reduce el saldo del servicio. Un anticipo igual o mayor al saldo se rechaza, porque para eso es la liquidación. Una liquidación igual al saldo deja el servicio pagado. Una liquidación distinta del saldo se rechaza.

El mantenedor ya respondió todas las preguntas de las demás heurísticas: ninguna otra aplica a esta Story. En esta sesión no hay conexión a Jira ni a Confluence: escribe en tu respuesta la declaración completa tal como la crearías y di que no se creó nada.
