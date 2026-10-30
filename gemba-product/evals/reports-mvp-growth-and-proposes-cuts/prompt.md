---
name: reports-mvp-growth-and-proposes-cuts
description: When the MVP grew during the review, Claude says by how much and proposes which stories move to the next release.
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
max_turns: 10
---
Estamos revisando el Story Map de la app de recordatorios para talleres mecánicos, que está en un whiteboard de Confluence. Cuando lo armé, el MVP tenía 6 historias y el Release 2 tenía 3. Después revisamos el mapa con el dueño del taller y agregamos historias al tablero. En esta sesión no hay conexión a Confluence: este es el SVG del whiteboard tal como lo devuelve la lectura, con el número de línea al inicio de cada línea.

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
22  <rect width="240.05" height="144.03" id="s1" data-type="sticky" fill="#eed7fc" x="318.51" y="-185.02"/>
23  <text x="438.53" y="-113.01" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s1-text" belongs-to="s1">
24  <tspan font-size="15.47px">Dueño del taller (usuario principal)</tspan>
25  </text>
26  <rect width="240.05" height="144.03" id="s2" data-type="sticky" fill="#eed7fc" x="621.84" y="-185.02"/>
27  <text x="741.87" y="-113.01" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s2-text" belongs-to="s2">
28  <tspan font-size="15.47px">Cliente</tspan>
29  </text>
30  <rect width="240.05" height="144.03" id="s3" data-type="sticky" fill="#baf3db" x="318.51" y="65.66"/>
31  <text x="438.53" y="137.68" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s3-text" belongs-to="s3">
32  <tspan font-size="15.47px">Registrar el servicio</tspan>
33  </text>
34  <rect width="240.05" height="144.03" id="s4" data-type="sticky" fill="#baf3db" x="925.17" y="65.66"/>
35  <text x="1045.19" y="137.68" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s4-text" belongs-to="s4">
36  <tspan font-size="15.47px">Avisar</tspan>
37  </text>
38  <rect width="240.05" height="144.03" id="s5" data-type="sticky" fill="#cfe1fd" x="318.51" y="316.34"/>
39  <text x="438.53" y="388.35" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s5-text" belongs-to="s5">
40  <tspan font-size="15.47px">Guardar al cliente</tspan>
41  </text>
42  <rect width="240.05" height="144.03" id="s6" data-type="sticky" fill="#cfe1fd" x="621.84" y="316.34"/>
43  <text x="741.87" y="388.35" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s6-text" belongs-to="s6">
44  <tspan font-size="15.47px">Anotar la fecha</tspan>
45  </text>
46  <rect width="240.05" height="144.03" id="s7" data-type="sticky" fill="#cfe1fd" x="925.17" y="316.34"/>
47  <text x="1045.19" y="388.35" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s7-text" belongs-to="s7">
48  <tspan font-size="15.47px">Ver a quién avisar</tspan>
49  </text>
50  <rect width="240.05" height="144.03" id="s8" data-type="sticky" fill="#cfe1fd" x="1228.5" y="316.34"/>
51  <text x="1348.53" y="388.35" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s8-text" belongs-to="s8">
52  <tspan font-size="15.47px">Mandar el mensaje</tspan>
53  </text>
54  <text x="-120.56" y="561.94" width="344.12" text-anchor="start" font-size="15.47px" font-scale="1" fill="#172b4d" id="label-release-0" data-type="text">
55  <tspan font-size="15.47px"> </tspan>
56  <tspan font-weight="bold" font-size="27px" dy="1">MVP</tspan>
57  <tspan font-size="15.47px" dy="1">Lo que el dueño necesita para dejar la libreta.</tspan>
58  </text>
59  <rect width="240.05" height="144.03" id="s9" data-type="sticky" fill="#fce4a6" x="318.51" y="561.94"/>
60  <text x="438.53" y="633.96" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s9-text" belongs-to="s9">
61  <tspan font-size="15.47px">Guardar nombre y teléfono</tspan>
62  </text>
63  <rect width="240.05" height="144.03" id="s10" data-type="sticky" fill="#fce4a6" x="318.51" y="745.97"/>
64  <text x="438.53" y="817.99" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s10-text" belongs-to="s10">
65  <tspan font-size="15.47px">Importar clientes desde la libreta</tspan>
66  </text>
67  <rect width="240.05" height="144.03" id="s11" data-type="sticky" fill="#fce4a6" x="621.84" y="561.94"/>
68  <text x="741.87" y="633.96" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s11-text" belongs-to="s11">
69  <tspan font-size="15.47px">Anotar la fecha del próximo servicio</tspan>
70  </text>
71  <rect width="240.05" height="144.03" id="s12" data-type="sticky" fill="#fce4a6" x="621.84" y="745.97"/>
72  <text x="741.87" y="817.99" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s12-text" belongs-to="s12">
73  <tspan font-size="15.47px">Sugerir la fecha según el tipo de servicio</tspan>
74  </text>
75  <rect width="240.05" height="144.03" id="s13" data-type="sticky" fill="#fce4a6" x="925.17" y="561.94"/>
76  <text x="1045.19" y="633.96" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s13-text" belongs-to="s13">
77  <tspan font-size="15.47px">Lista de clientes a avisar hoy</tspan>
78  </text>
79  <rect width="240.05" height="144.03" id="s14" data-type="sticky" fill="#fce4a6" x="925.17" y="745.97"/>
80  <text x="1045.19" y="817.99" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s14-text" belongs-to="s14">
81  <tspan font-size="15.47px">Filtrar la lista por tipo de servicio</tspan>
82  </text>
83  <rect width="240.05" height="144.03" id="s15" data-type="sticky" fill="#ffd5d2" x="925.17" y="930.0"/>
84  <text x="1045.19" y="1002.01" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s15-text" belongs-to="s15">
85  <tspan font-size="15.47px">¿Desde qué número salen los avisos?</tspan>
86  </text>
87  <rect width="240.05" height="144.03" id="s16" data-type="sticky" fill="#fce4a6" x="1228.5" y="561.94"/>
88  <text x="1348.53" y="633.96" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s16-text" belongs-to="s16">
89  <tspan font-size="15.47px">Abrir WhatsApp con el mensaje listo</tspan>
90  </text>
91  <rect width="240.05" height="144.03" id="s17" data-type="sticky" fill="#fce4a6" x="1228.5" y="745.97"/>
92  <text x="1348.53" y="817.99" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s17-text" belongs-to="s17">
93  <tspan font-size="15.47px">No avisar dos veces por el mismo servicio</tspan>
94  </text>
95  <rect width="240.05" height="144.03" id="s18" data-type="sticky" fill="#fce4a6" x="1228.5" y="930.0"/>
96  <text x="1348.53" y="1002.01" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s18-text" belongs-to="s18">
97  <tspan font-size="15.47px">Plantillas de mensaje editables</tspan>
98  </text>
99  <rect width="240.05" height="144.03" id="s19" data-type="sticky" fill="#fce4a6" x="1228.5" y="1114.03"/>
100  <text x="1348.53" y="1186.05" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s19-text" belongs-to="s19">
101  <tspan font-size="15.47px">Reporte de quién volvió a tiempo</tspan>
102  </text>
103  <text x="-120.56" y="1348.63" width="344.12" text-anchor="start" font-size="15.47px" font-scale="1" fill="#172b4d" id="label-release-1" data-type="text">
104  <tspan font-size="15.47px"> </tspan>
105  <tspan font-weight="bold" font-size="27px" dy="1">Release 2</tspan>
106  <tspan font-size="15.47px" dy="1">Lo que no entra al MVP.</tspan>
107  </text>
108  <rect width="240.05" height="144.03" id="s20" data-type="sticky" fill="#f0f1f2" x="318.51" y="1359.63"/>
109  <text x="438.53" y="1431.65" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s20-text" belongs-to="s20">
110  <tspan font-size="15.47px">Registrar vehículo</tspan>
111  </text>
112  <rect width="240.05" height="144.03" id="s21" data-type="sticky" fill="#f0f1f2" x="925.17" y="1359.63"/>
113  <text x="1045.19" y="1431.65" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s21-text" belongs-to="s21">
114  <tspan font-size="15.47px">Aviso de la víspera</tspan>
115  </text>
116  <rect width="240.05" height="144.03" id="s22" data-type="sticky" fill="#f0f1f2" x="1228.5" y="1359.63"/>
117  <text x="1348.53" y="1431.65" width="216" text-anchor="middle" font-size="15.47px" fill="#172b4d" id="s22-text" belongs-to="s22">
118  <tspan font-size="15.47px">Envío automático</tspan>
119  </text>
120  </svg>
</board>

Ya terminamos la revisión con el dueño. ¿Cómo quedó el MVP?
