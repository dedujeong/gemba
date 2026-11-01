---
name: splits-a-criterion-too-big-for-one-commit
description: A criterion too big for one commit is split by behavior when it is planned, into commits that can be reverted separately.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Implementa TALLER-25.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira, ni cambios reales de git, ni modo de planeación real. Sigue el flujo hasta el plan y entrega los commits que planeas como una tabla con las columnas Orden, Mensaje del commit y Comportamiento que cubre, una fila por commit.

TALLER-25 es una Story en Backlog, sin bloqueos, de la fix version `Taller v0.1.0`, con el Summary `Remind the customer the day before`, y su component en Jira es `notifications`. Su único criterio: dado un servicio agendado para mañana, cuando llega el día anterior, entonces el cliente recibe el recordatorio por WhatsApp a la hora que el taller configuró y el envío queda registrado en el historial del cliente. La exploración ya terminó: hoy no existe nada de esto. Enviar el mensaje, programar la hora configurada y registrar el envío en el historial son tres comportamientos independientes, y juntos son demasiado grandes para un solo commit.
