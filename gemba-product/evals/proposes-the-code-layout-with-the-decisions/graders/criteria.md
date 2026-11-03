---
type: llm
focus: trace
---
The MVP of the prompt is closed, has four stories for a single yoga studio, and its Constraints say free plans only, one person operating it with error alerts only, TypeScript and Postgres, and name and phone of each student. The person asks Claude to propose the architecture decisions. There is no Confluence connection, so the proposal is written in the reply.

One of the decisions Claude proposes must be the layout of the code, the decision of where each file goes. Every other decision of the proposal, its form and its length are neither required nor penalized.

The layout counts when it covers its four parts: how the folders are organized by domain, where the tests go, how the files are named, and where the migrations go (the product has a Postgres database, so it has migrations).

PASS if the response proposes the layout of the code as one of its decisions and says in it the four parts: the folders by domain, where the tests go, how the files are named and where the migrations go.
FAIL if the response does not propose a decision about the layout of the code, if it leaves it to development or says it is not an architecture decision, or if the decision lacks one of the four parts.
