---
name: proposes-the-next-step-as-one-option
description: Starting a session with a handoff from the previous one, the next step of the handoff is proposed as one option and the work waits for the maintainer's answer.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Retoma la sesión, qué sigue.

El CLAUDE.md del proyecto tiene este bloque:

```
## Gemba

- Jira Project: TALLER
- Confluence Space: TALLER
- Integration: merge
- Language: es-MX
```

El handoff más reciente de `.gemba/sessions` es `2026-11-01T17-55-03.md` y dice:

```
# Session 2026-11-01 17:55:03

## Version
Taller v0.2.0, del 2026-11-02 al 2026-11-20.

## Work in progress
TALLER-12 "Save the vehicle", en Implement. Rama: `story/TALLER-12-save-the-vehicle`.

## Done this session
- a1b2c3d feat(api): add the endpoint that saves the vehicle

## Pending
- `tests/test_vehicle_validation.py` quedó sin commit y a medias.
- Pasar TALLER-12 a Review cuando todos los tests estén en verde.

## Decisions
- La placa se guarda en mayúsculas y sin espacios, porque la búsqueda del taller es por placa.

## Next step
Terminar `tests/test_vehicle_validation.py` y después pasar TALLER-12 a Review, porque es lo único que falta de la historia.
```

En esta sesión no hay conexión a Jira, no se pueden ejecutar comandos ni leer archivos: usa el handoff de arriba como el que leíste, escribe tu respuesta tal como la darías y di lo que no pudiste comprobar.
