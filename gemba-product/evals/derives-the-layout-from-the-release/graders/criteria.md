---
type: llm
focus: trace
---
The MVP of the prompt is closed, has four stories and a data model (Clase, Alumno, Reserva) for a single yoga studio, and its Constraints say TypeScript and Postgres. The person asks Claude to propose the architecture decisions. There is no Confluence connection, so the proposal is written in the reply.

One of the decisions Claude proposes must be the layout of the code, derived from the work of the release: the stories and the data model. Every other decision of the proposal, its form and its length are neither required nor penalized.

The layout counts when it says three things, taken from the release and not from a fixed list of folders: which domains get their own folder (it names them from the stories or the data model), the direction of the dependencies between them (which domain may use which), and the entry file of each domain. It does not decide again the conventions of the framework.

PASS if the response proposes the layout of the code as one of its decisions and says the domains that get their own folder, the direction of the dependencies and the entry file of each domain.
FAIL if the response does not propose a layout decision, if it lacks the domains, the direction of the dependencies or the entry files, or if it only gives a fixed list of folders, tests, file names and migrations without deriving the domains from the release.
