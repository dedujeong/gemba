---
type: llm
focus: trace
---
The MVP has four stories (see the schedule with free spots, hold a spot with name and phone, cancel it, the owner sees who is signed up). The stories name classes, spots held (reservations) and the owner. Claude drafts the spec of the Architecture diagrams in the reply.
The spec may also carry `questions` (open doubts drawn as red stickies), `states` and a `cardinality` on a relation: none of them is an entity, a field or a missing label, so they never decide this criterion.
PASS if the spec has a `data_model` with an entity for each thing the stories name (at least the class and the reservation), each with its main fields (the reservation carries the name and phone of the student and points to its class, either as a field of its own or as a relation from the class to the reservation), and relations between them with a label.
FAIL if the spec has no `data_model`, if an entity the stories name is missing, if an entity has no fields, if a relation has no label, or if it adds an entity no story mentions (payments, memberships, instructors, notifications).
