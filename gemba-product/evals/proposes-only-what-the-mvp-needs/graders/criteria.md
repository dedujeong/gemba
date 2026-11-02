---
type: llm
focus: trace
---
The MVP has four stories (see the schedule with free spots, hold a spot, cancel it, the owner sees who is signed up) for a single studio, and the Constraints say free plans only, one person operating it with error alerts only, TypeScript and Postgres, and name and phone of each student.
PASS if Claude proposes architecture decisions and every one of them says which story of the MVP or which constraint of the brief needs it, and none of them is something no story or constraint asks for.
FAIL if any proposed decision does not say what in the MVP or the brief needs it, or if Claude proposes something the MVP does not ask for (for example payments, offline use, push notifications, isolation between several studios, or a separate microservice), or if Claude proposes no decisions.
