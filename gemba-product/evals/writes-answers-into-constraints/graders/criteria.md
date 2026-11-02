---
type: llm
focus: trace
---
The brief already had a Constraints section with one bullet (the cost must fit in free plans), plus Source, Problem, Primary job, Glossary and one open decision.
PASS if the updated brief body in the reply has the person's three answers inside the Constraints section: operation (alone, only error alerts), team (Python, TypeScript and Postgres) and data (personal data including age), each as a bullet with a bold label, and the original cost bullet is still there.
FAIL if any of the three answers is missing from Constraints, if they appear only in another section or only in the conversation, if the original cost bullet is gone, or if no updated body was written.
