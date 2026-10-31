---
name: reviews-the-closed-release-against-jira
description: When asked to review a closed release, Claude shows which Stories were delivered and which not, and the real time against the estimate, from Jira.
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
max_turns: 10
---
Cerramos el MVP de la app de recordatorios para talleres mecánicos y salió como v1.0.0. Quiero revisar el release: qué se entregó, qué no, y cómo salió el tiempo contra lo estimado. En esta sesión no hay conexión a Jira ni a Confluence: los datos de Jira están pegados abajo.

<jira>
Fix version v1.0.0, Stories (estado, original estimate, tiempo registrado):
- APP-101 "Guardar la fecha de servicio" — Done — estimate 4h — spent 5h
- APP-102 "Recordatorio por WhatsApp" — Done — estimate 6h — spent 4h 30m
- APP-103 "Aviso de la víspera" — Implement — estimate 3h — spent 2h. Descripción: enviar el aviso el día anterior al servicio, no solo el mismo día.
- APP-104 "Confirmación de lectura" — Backlog — estimate 5h — spent 0h. Descripción: saber si el cliente abrió el mensaje antes de contarlo como avisado.
</jira>
