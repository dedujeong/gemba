---
name: cites-the-spike-sources-as-cards
description: The findings page of a Spike lists the ADR and the links consulted during its test as block cards in Sources.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
---
Termina el Spike TALLER-50.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

En esta sesión no hay conexión a Jira ni a Confluence, ni cambios reales de git. Sigue el flujo hasta publicar la respuesta y escribe el cuerpo HTML completo de la página de findings que crearías, tal como lo mandarías a Confluence.

TALLER-50 es un Spike en Implement, en la rama `spike/TALLER-50-can-we-send-whatsapp-reminders`, trabajado en el worktree `.claude/worktrees/TALLER-50-can-we-send-whatsapp-reminders`, con el Summary `Can we send WhatsApp reminders`. Su pregunta: si la API de WhatsApp Business permite enviar recordatorios de cita sin plantilla aprobada. La prueba acaba de terminar: no se puede, Meta exige una plantilla aprobada, que tarda unas 24 horas. Durante la prueba se consultaron el ADR https://taller.atlassian.net/wiki/spaces/TALLER/pages/4101/ADR-0003+Send+reminders+through+WhatsApp+Business y la documentación de Meta https://developers.facebook.com/docs/whatsapp/message-templates. La carpeta `Work` > `Spikes` ya existe en el espacio TALLER.
