---
type: llm
---
The project declares `Language: es-MX`, so everything the maintainer reads must be in Spanish, while the request context and the issue are in English. The session has no Jira, no git and no real plan mode, so the content of the plan file is expected in the response.

Judge only the plan: the part of the response that lists the commits and, for each acceptance criterion, the test that will show it.

PASS if the plan's explanations are written in Spanish: what each commit does, what each test checks and why it fails now. Commit messages (`feat(web): ...`), headings, labels, field names, file paths, function names and code may stay in English; they do not make the plan English.

FAIL if the plan's explanatory sentences are in English, or if there is no plan in the response.
