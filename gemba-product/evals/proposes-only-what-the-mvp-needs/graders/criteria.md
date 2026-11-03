---
type: llm
focus: trace
---
The MVP has four stories (see the schedule with free spots, hold a spot, cancel it, the owner sees who is signed up) for a single studio, and the Constraints say free plans only, one person operating it with error alerts only, TypeScript and Postgres, and name and phone of each student.
PASS if Claude proposes architecture decisions and every one of them names the story of the MVP or the constraint of the brief that needs it. A decision about the code layout (folders, tests, file names, migrations) is always expected: it counts as naming its need when it names the closed MVP or the Equipo constraint. None of them is on the list of things the MVP does not ask for: payments, offline use, push notifications, isolation between several studios, a separate microservice, or any other capability no story or constraint mentions.
FAIL if any proposed decision does not name the story or the constraint that needs it, or if Claude proposes something on that list, or if Claude proposes no decisions.
