---
type: llm
---
The project already has the components `api`, `web` and `ci`, and the Story is the server endpoint that saves a vehicle, which belongs to `api`.

PASS if the drafted Story carries exactly the component `api`, and Claude does not propose any other or new component.
FAIL if the component is anything other than `api`, if a new component is proposed, or if the Story has no component.
