---
name: draws-an-open-question-as-a-sticky
description: A doubt nobody has answered about a diagram goes in the questions of the diagram, about one element, and not in a label or a note.
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 8
---
Estamos en el paso 7 de arquitectura del discovery de una app de gastos personales, en el espacio PRODUCTOS. Los ADR ya están aceptados: el frontend es la Web app, publicada en el proveedor de hosting estático; la base de datos y el acceso (Auth) están en el proveedor de datos, ambos operados por el equipo; las cuentas se leen del Banco, que opera una institución financiera. Del Story Map del MVP: la persona ahorradora registra y categoriza sus gastos; la persona asesora ve el resumen de gastos de quien la autorizó; el operador da de alta y desactiva cuentas. La Web app lee y escribe en la base de datos, valida la sesión con Auth y consulta el saldo en el Banco. Hay una duda que nadie ha respondido: no sabemos si una cuenta desactivada puede volver a estar Activa. Dibuja el diagrama de estados de Cuenta con sus estados Activa y Desactivada (el operador la da de Alta y la Desactiva).

No hay conexión a Confluence en esta sesión: escribe en la respuesta el spec JSON de los diagramas, como lo define la plantilla, y di que no publicaste nada.
