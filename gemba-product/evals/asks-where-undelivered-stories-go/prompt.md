---
name: asks-where-undelivered-stories-go
description: For Stories not delivered, Claude proposes the matching sticky and asks whether it goes to the next release or Later, without moving anything first.
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
max_turns: 10
---
Estamos revisando el cierre de v1.0.0 (el MVP) de la app de recordatorios. Ya vimos que APP-103 y APP-104 no se entregaron. Quiero decidir qué hacemos con ellas en el Story Map. En esta sesión no hay conexión a Jira ni a Confluence: los datos de Jira están pegados abajo, y este es el SVG del whiteboard tal como lo devuelve la lectura, con el número de línea al inicio de cada línea.

<jira>
Fix version v1.0.0, Stories (estado, original estimate, tiempo registrado):
- APP-101 "Guardar la fecha de servicio" — Done — estimate 4h — spent 5h
- APP-102 "Recordatorio por WhatsApp" — Done — estimate 6h — spent 4h 30m
- APP-103 "Aviso de la víspera" — Implement — estimate 3h — spent 2h. Descripción: enviar el aviso el día anterior al servicio, no solo el mismo día.
- APP-104 "Confirmación de lectura" — Backlog — estimate 5h — spent 0h. Descripción: saber si el cliente abrió el mensaje antes de contarlo como avisado.
</jira>

<board>
1<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="50000" height="50000" viewBox="-25120.56 -25484.45 50000 50000" font-family="Atlassian Sans, ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, Ubuntu, Helvetica Neue, sans-serif">
2  <text x="-120.56" y="-418.23" width="1445.17" text-anchor="start" font-size="15.47px" font-scale="1.29" fill="#172b4d" id="board-header" data-type="text">
3  <tspan font-size="15.47px"> </tspan>
4  <tspan font-weight="bold" font-size="27px" dy="1">Recordatorios para talleres</tspan>
5  <tspan font-size="15.47px" dy="1">Una app para que el dueño de un taller avise por WhatsApp cuándo toca servicio.</tspan>
6  </text>
7  <text x="-120.56" y="-201.02" width="344.12" text-anchor="start" font-size="15.47px" font-scale="1" fill="#172b4d" id="label-persona" data-type="text">
8  <tspan font-size="15.47px"> </tspan>
9  <tspan font-weight="bold" font-size="27px" dy="1">User persona</tspan>
10  <tspan font-size="15.47px" dy="1">Quién usa el producto.</tspan>
11  </text>
12  <text x="-120.56" y="60.66" width="344.12" text-anchor="start" font-size="15.47px" font-scale="1" fill="#172b4d" id="label-activities" data-type="text">
13  <tspan font-size="15.47px"> </tspan>
14  <tspan font-weight="bold" font-size="27px" dy="1">Activities</tspan>
15  <tspan font-size="15.47px" dy="1">Lo que pasa, en orden.</tspan>
16  </text>
17  <text x="-120.56" y="322.34" width="344.12" text-anchor="start" font-size="15.47px" font-scale="1" fill="#172b4d" id="label-tasks" data-type="text">
18  <tspan font-size="15.47px"> </tspan>
19  <tspan font-weight="bold" font-size="27px" dy="1">Tasks</tspan>
20  <tspan font-size="15.47px" dy="1">Los pasos de cada actividad.</tspan>
21  </text>
22  <rect width="240.05" height="144.03" id="s1" data-type="sticky" fill="#f5e989" x="318.51" y="-185.02"/>
23  <text x="438.53" y="-113.01" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s1-text" belongs-to="s1">
24  <tspan font-size="15.47px">Dueño del taller (usuario principal)</tspan>
25  </text>
26  <rect width="240.05" height="144.03" id="s2" data-type="sticky" fill="#eed7fc" x="318.51" y="65.66"/>
27  <text x="438.53" y="137.68" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s2-text" belongs-to="s2">
28  <tspan font-size="15.47px">Registrar un servicio</tspan>
29  </text>
30  <rect width="240.05" height="144.03" id="s3" data-type="sticky" fill="#eed7fc" x="621.84" y="65.66"/>
31  <text x="741.87" y="137.68" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s3-text" belongs-to="s3">
32  <tspan font-size="15.47px">Avisar</tspan>
33  </text>
34  <rect width="240.05" height="144.03" id="s4" data-type="sticky" fill="#cfe1fd" x="318.51" y="316.34"/>
35  <text x="438.53" y="388.35" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s4-text" belongs-to="s4">
36  <tspan font-size="15.47px">Guardar la fecha del próximo servicio</tspan>
37  </text>
38  <rect width="240.05" height="144.03" id="s5" data-type="sticky" fill="#cfe1fd" x="621.84" y="316.34"/>
39  <text x="741.87" y="388.35" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s5-text" belongs-to="s5">
40  <tspan font-size="15.47px">Enviar el aviso</tspan>
41  </text>
42  <text x="-120.56" y="612.94" width="344.12" text-anchor="start" font-size="15.47px" font-scale="1" fill="#172b4d" id="label-release-0" data-type="text">
43  <tspan font-size="15.47px"> </tspan>
44  <tspan font-weight="bold" font-size="27px" dy="1">MVP</tspan>
45  <tspan font-size="15.47px" dy="1">Lo que entra primero.</tspan>
46  </text>
47  <rect width="240.05" height="144.03" id="s6" data-type="sticky" fill="#baf3db" x="318.51" y="561.94"/>
48  <text x="438.53" y="633.96" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s6-text" belongs-to="s6">
49  <tspan font-size="15.47px">Guardar la fecha de servicio por cliente</tspan>
50  </text>
51  <rect width="240.05" height="144.03" id="s7" data-type="sticky" fill="#baf3db" x="621.84" y="561.94"/>
52  <text x="741.87" y="633.96" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s7-text" belongs-to="s7">
53  <tspan font-size="15.47px">Enviar el recordatorio por WhatsApp</tspan>
54  </text>
55  <rect width="240.05" height="144.03" id="s8" data-type="sticky" fill="#baf3db" x="621.84" y="745.97"/>
56  <text x="741.87" y="817.99" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s8-text" belongs-to="s8">
57  <tspan font-size="15.47px">Avisar un día antes del servicio</tspan>
58  </text>
59  <rect width="240.05" height="144.03" id="s9" data-type="sticky" fill="#baf3db" x="621.84" y="930.0"/>
60  <text x="741.87" y="1002.01" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s9-text" belongs-to="s9">
61  <tspan font-size="15.47px">Confirmar que el cliente recibió el aviso</tspan>
62  </text>
63  <text x="-120.56" y="1226.6" width="344.12" text-anchor="start" font-size="15.47px" font-scale="1" fill="#172b4d" id="label-release-1" data-type="text">
64  <tspan font-size="15.47px"> </tspan>
65  <tspan font-weight="bold" font-size="27px" dy="1">Release 2</tspan>
66  <tspan font-size="15.47px" dy="1">Lo que no entra en el primero.</tspan>
67  </text>
68  <rect width="240.05" height="144.03" id="s10" data-type="sticky" fill="#fce4a6" x="318.51" y="1175.6"/>
69  <text x="438.53" y="1247.62" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s10-text" belongs-to="s10">
70  <tspan font-size="15.47px">Importar las fechas del cuaderno</tspan>
71  </text>
72  <text x="-120.56" y="1472.2" width="344.12" text-anchor="start" font-size="15.47px" font-scale="1" fill="#172b4d" id="label-release-2" data-type="text">
73  <tspan font-size="15.47px"> </tspan>
74  <tspan font-weight="bold" font-size="27px" dy="1">Later</tspan>
75  <tspan font-size="15.47px" dy="1">Todavía sin release asignado.</tspan>
76  </text>
77  <rect width="240.05" height="144.03" id="s11" data-type="sticky" fill="#fff5db" x="621.84" y="1421.2"/>
78  <text x="741.87" y="1493.22" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s11-text" belongs-to="s11">
79  <tspan font-size="15.47px">Reporte mensual de servicios</tspan>
80  </text>
81  </svg>
</board>
