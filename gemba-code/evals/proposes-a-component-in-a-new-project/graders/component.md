---
type: llm
---
The project has no components yet, the Product Brief says the product is an API in Python plus a web that consumes it, and the Story is the API endpoint that saves a vehicle.

PASS if the drafted Story carries one component that names the part the change touches (the API or the backend, such as `api` or `backend`), written in lowercase, and the draft says that this component is new or that the project has none.
FAIL if the Story has no component, if the component is not lowercase, if it names a business domain instead of the part touched (such as `vehiculos`), or if Claude only asks the maintainer to name the component without proposing one.
