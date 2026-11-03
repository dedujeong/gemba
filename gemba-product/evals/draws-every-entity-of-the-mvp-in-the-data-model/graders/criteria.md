---
type: llm
focus: trace
---
The MVP has four stories (see the schedule with free spots, hold a spot with name and phone, cancel it, the owner sees who is signed up). The stories name classes, spots held (reservations) and the owner. Claude drafts the spec of the Architecture diagrams in the reply.
PASS if the spec has a `data_model` with an entity for each thing the stories name (at least the class and the reservation), each with its main fields (the reservation carries the name and phone of the student and points to its class), and relations between them with a label.
FAIL if the spec has no `data_model`, if an entity the stories name is missing, if an entity has no fields, if a relation has no label, or if it adds an entity no story mentions (payments, memberships, instructors, notifications).
